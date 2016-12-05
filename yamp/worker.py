# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

__author__ = "Sergi Blanch-Torne"
__email__ = "srgblnchtrn@protonmail.ch"
__copyright__ = "Copyright 2016 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"

from .events import EventManager as _EventManager
from .logger import Logger as _Logger
from multiprocessing import current_process as _current_process
from multiprocessing import Event as _Event
from multiprocessing import Process as _Process
from multiprocessing import Queue as _Queue
try:
    import psutil as _psutil  # soft-dependency
except:
    _psutil = None
from threading import Thread as _Thread
from threading import current_thread as _current_thread
from traceback import print_exc as _print_exc

_MAXJOINTRIES = 3


class Worker(_Logger):
    def __init__(self, id, target, inputQueue, outputQueue, checkPeriod=None,
                 preHook=None, preExtraArgs=None,
                 postHook=None, postExtraArgs=None,
                 *args, **kwargs):
        """
            Build an object...

            Arguments:
            + id: integer that can identify the worker between others.
            + target: Method that each of the parallel process will be
              executing with the input arguments. It must be callable with
              objects in the argin queue as parameters.
            + inputQueue: multithreading queue where each element is data input
              for the method that will be executed by the child process.
            + outputQueue: multithreading queue where the results will be
              stored after the execution.
            * {pre, post}Hook: callable objects to be executed before or after
              the target.
            * {pre, post}ExtraArgs: dictionaries that will be passed to hooks.
        """
        super(Worker, self).__init__(*args, **kwargs)
        self.__id = id
        if not callable(target):
            raise AssertionError("Target must be callable object")
        else:
            self.__target = target
        self.__input = inputQueue
        self.__currentArgin = None
        self.__output = outputQueue
        self.__currentArgout = None
        self.__checkPeriod = 60  # seconds
        self.checkPeriod = checkPeriod
        # Events ---
        self.__events = _EventManager()
        self.__prepared = _Event()
        self.__prepared.clear()
        self.__internalEvent = _Event()
        self.__internalEvent.clear()
        # Hooks ---
        self.__preHook = None
        self.__preExtraArgs = None
        self.__postHook = None
        self.__postExtraArgs = None
        self.preHook = preHook
        self.preExtraArgs = preExtraArgs
        self.postHook = postHook
        self.postExtraArgs = postExtraArgs
        # thread and process ---
        self.__monitor = _Thread(target=self.__thread)
        self.__worker = _Process(target=self.__procedure)
        self.__monitor.setDaemon(True)
        self.__monitor.start()
        self.__workerPausedFlag = False

    def __str__(self):
        return "%s()" % (self.name)

    def __repr__(self):
        return "%s(%d)" % (self.name, self.checkPeriod)

    def prepared(self):
        return self.__prepared.is_set()

    def waitPrepared(self, timeout=None):
        self.__prepared.wait(timeout)

    def start(self):
        """Command to launch the event needed to start the work"""
        self.debug("START has been requested to Worker %d" % (self.__id))
        self.__events.start()

    def isStarted(self):
        return self.__isProcessAlive()

    def pause(self):
        """Command to pause the execution."""
        self.debug("PAUSE has been requested to Worker %d" % (self.__id))
        return self.__events.pause()

    def isPaused(self):
        """Request to know if the execution is on pause."""
        return self.__events.isPaused()
        # FIXME: check if the process is really paused

    def resume(self):
        """Command to resume from pause."""
        self.debug("RESUME has been requested to Worker %d" % (self.__id))
        return self.__events.resume()

    def stop(self):
        """Command to finish the execution of the work."""
        self.info("STOP has been requested to Worker %d" % (self.__id))
        self.__events.stop()

#     def abort(self):
#         self.stop()  # TODO: break the execution

    def isAlive(self):
        """Request to know if the worker is alive."""
        return self.__monitor.isAlive()
        # TODO: those condition must be reviewed.

    def __isProcessAlive(self):
        return self.__worker.is_alive()

    def __checkDeadProcess(self):
        if not self.__isProcessAlive():
            if self._endProcedure():
                self.info("Worker has finish and nothing else to be made.")
                return
            self.critical("process has died and it shouldn't!")
            self.__input.put(self.__currentArgin)
            self.__worker = _Process(target=self.__procedure)
            self.__worker.start()

    # TODO: progress feature

    def _endProcedure(self):
        return self._procedureHas2End() or self.__input.empty()

    def _procedureHas2End(self):
        """End condition for the process"""
        return self.__events.isStopped()

    # thread and process ---

    def __thread(self):
        """Monitor thread function."""
        _current_thread().name = "Monitor%d" % (self.__id)
        self.__prepared.set()
        while not self.__events.waitStart(self.__checkPeriod):
            self.debug("Waiting to start")
            # FIXME: msg to be removed, together with the timeout
        self.info("Start to work: creating the fork")
        self.__worker.start()
        self.__processMonitoring()
        self.debug("Monitor has finished its task")

    def __processMonitoring(self):
        self.debug("Start monitoring")
        while not self._endProcedure():
            try:
                self.__doWait(self.__internalEvent, [[self.__events.waitPause,
                                                     self.__doPause],
                                                     [self.__events.waitResume,
                                                     self.__doResume],
                                                     ])
            except Exception as e:
                self.error("Monitor exception: %s" % (e))
                _print_exc()
        self.__doJoin()

    def __doWait(self, primaryEvent, actionsLst):
        while not primaryEvent.wait(self.__checkPeriod):
            for event, action in actionsLst:
                if event(self.__checkPeriod):
                    action()
        self.debug("Internal event received")

    def __doPause(self):
        if _psutil is None:
            self.warning("Without psutil pause will be when the process "
                         "finish its current task.")
        else:
            if not self.__workerPausedFlag:
                self.debug("psutil.Process(%d).suspend()"
                           % (self.__worker.pid))
                _psutil.Process(self.__worker.pid).suspend()
                self.__workerPausedFlag = True
            else:
                self.debug("Process(%d) already suspended"
                           % (self.__worker.pid))

    def __doResume(self):
        if _psutil is not None:
            if self.__workerPausedFlag:
                self.debug("psutil.Process(%d).resume()" % (self.__worker.pid))
                _psutil.Process(self.__worker.pid).resume()
                self.__workerPausedFlag = False
            else:
                self.debug("Process(%d) already resumed" % (self.__worker.pid))

    def __doJoin(self):
        tries = 0
        while self.__worker.is_alive():
            self.__worker.join(self.__checkPeriod)
            if self.__worker.is_alive():
                tries += 1
                self.warning("Worker didn't join (try %d)" % (tries))
                if tries > _MAXJOINTRIES and _psutil is not None:
                    self.error("Worker hasn't finishing, terminating")
                    _psutil.Process(self.__worker.pid).terminate()
        self.info("Worker %d joined" % (self.__id))

    def __procedure(self):
        """Function of the fork process"""
        _current_process().name = "Process%d" % (self.__id)
        _current_thread().name = "Worker%d" % (self.__id)
        self.debug("Fork starts")
        while not self._endProcedure():
            try:
                if self.__events.isPaused():
                    self.info("paused")
                    if self._procedureHas2End():
                        break
                    while not self.__events.waitResume(self.checkPeriod):
                        pass
                    self.info("resume")
                else:
                    self.__currentArgin = self.__input.get()
                    self.debug("argin: %s" % (self.__currentArgin))
                    if self.__preHook is not None:
                        self.debug("call preHook")
                        self.__preHook(self.__currentArgin,
                                       **self.__preExtraArgs)
                    if self._procedureHas2End():
                        break
                    self.__currentArgout = self.__target(self.__currentArgin)
                    self.info("argout: %s" % (self.__currentArgout))
                    self.__output.put([self.__currentArgin,
                                       self.__currentArgout])
                    if self.__postHook is not None:
                        self.debug("call postHook")
                        self.__postHook(self.__currentArgin,
                                        self.__currentArgout,
                                        **self.__postExtraArgs)
                    self.__events.step()
            except Exception as e:
                self.error("exception: %s" % (e))
                _print_exc()
        # process has finish, lets wake up the monitor
        self.__internalEvent.set()
        self.debug("Internal event emitted to report end of the procedure")

    # properties ---

    def checkPeriod():
        doc = """
        Even the intercommunication uses (multiprocessing) Events, this value
        will be used as a timeout for periodical checks.
              """

        def fget(self):
            return self.__checkPeriod

        def fset(self, v):
            if v is None:
                return
            if type(v) is not int:
                self.warning("Check period must be an integer, ignoring")
            else:
                self.__checkPeriod = v

        return locals()

    checkPeriod = property(**checkPeriod())

    def preHook():
        doc = """
        Function to be called before each execution of the worker target
              """

        def fget(self):
            return self.__preHook

        def fset(self, f):
            if f is not None and not callable(f):
                self.warning("Hooks must be callable objects, ignoring")
            else:
                self.__preHook = f

        return locals()

    preHook = property(**preHook())

    def preExtraArgs():
        doc = """
        Extra argument as a dictionary with information to be passed to the
        prehook.
              """

        def fget(self):
            return self.__preExtraArgs

        def fset(self, v):
            self.__preExtraArgs = v

        return locals()

    preExtraArgs = property(**preExtraArgs())

    def postHook():
        doc = """
        Function to be called after each execution of the worker target
              """

        def fget(self):
            return self.__postHook

        def fset(self, f):
            if f is not None and not callable(f):
                self.warning("Hooks must be callable objects, ignoring")
            else:
                self.__postHook = f

        return locals()

    postHook = property(**postHook())

    def postExtraArgs():
        doc = """
        Extra argument as a dictionary with information to be passed to the
        posthook.
              """

        def fget(self):
            return self.__postExtraArgs

        def fset(self, v):
            self.__postExtraArgs = v

        return locals()

    postExtraArgs = property(**postExtraArgs())

    def name():
        doc = """Name of the Worker"""

        def fget(self):
            return "Worker%d" % (self.__id)

        return locals()

    name = property(**name())

    def pid():
        doc = """Process ID of the worker's child process"""

        def fget(self):
            return self.__worker.pid

        return locals()

    pid = property(**pid())
