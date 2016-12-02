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


from multiprocessing import cpu_count as _cpu_count
from multiprocessing import Event as _Event
from multiprocessing import Queue as _Queue
from threading import current_thread as _current_thread
from threading import Thread as _Thread

from .logger import Logger as _Logger
from .worker import Worker as _Worker


class Pool(_Logger):
    def __init__(self, target, arginLst, parallel=None, checkPeriod=None,
                 preHook=None, preExtraArgs=None,
                 postHook=None, postExtraArgs=None,
                 *args, **kwargs):
        """
            Build an object with the capacity to execute multiple process with
            the same method. It will build a pool of processes where they will
            take elements in a shared queue until the queue is empty.

            Arguments:
            - target: Method that each of the parallel process will be
              executing with the input arguments. It must be callable with
              objects in the list as parameters.
            - arginLst: python list where each element is data input for the
              method that will be executed in parallel.
            - parallel: (optional) to establish the number of parallel
              processes that will participate. By default the maximum possible
              based on the number of cores available.
        """
        super(self.__class__, self).__init__(*args, **kwargs)
        # prepare the parameters ---
        self.__target = target
        self.__checkPeriod = 60  # seconds
        self.__parallel = None
        self.__workersLst = []
        self.__input = _Queue()
        self.__inputNelements = 0
        self.__output = _Queue()
        self.__poolMonitor = _Thread(target=self.__poolMonitorThread)
        self.__poolMonitor.setDaemon(True)
        self.__collected = []
        # structures for the child processes
        self.__startProcess = _Event()
        self.__stepProcess = _Event()
        self.__pauseProcess = _Event()
        self.__resumeProcess = _Event()
        self.__stopProcess = _Event()
        # hooks ---
        self.__preHook = preHook
        self.__preExtraArgs = preExtraArgs
        self.__postHook = postHook
        self.__postExtraArgs = postExtraArgs
        # setup ---
        self.__prepareParallel(parallel)
        self.__prepareInputQueue(arginLst)
        self.__prepareWorkers()
        self.__prepareMonitoring()

    # Interface ---

    def __eventSet(self, event, cmd):
        if event.is_set():
            self.warning("Cannot %s when it was already" % (cmd))
            return
        self.debug("%s()" % (cmd))
        event.set()

    def start(self):
        self.__eventSet(self.__startProcess, "Start")

    def pause(self):
        self.__resumeProcess.clear()
        self.__eventSet(self.__pauseProcess, "Pause")

    def isPaused(self):
        return self.__pauseProcess.is_set()

    def is_paused(self):
        return self.isPaused()

    def resume(self):
        if not self.__pauseProcess.is_set():
            self.warning("Nothing to be resumed if not paused")
            return
        self.__pauseProcess.clear()
        self.__eventSet(self.__resumeProcess, "Resume")

    def stop(self):
        self.__eventSet(self.__stopProcess, "Stop")

    def isAlive(self):
        return self.__startProcess.is_set() and not self.__stopProcess.is_set()

    def is_alive(self):
        return self.isAlive()

    # properties

    def checkPeriod():
        def fget(self):
            return self.__checkPeriod

        def fset(self, value):
            oldValues = []
            try:
                for i, worker in enumerate(self.__workersLst):
                    oldValues.append(worker.checkPeriod)
                    worker.checkPeriod = value
            except Exception as e:
                self.error("Exception setting a new checkPeriod in worker "
                           "%d (%s): %s" % (i, worker, e))
                for j in range(i-1, -1, -1):
                    worker.checkPeriod = oldValues[j]
            else:
                self.__checkPeriod = value

        return locals()

    checkPeriod = property(**checkPeriod())

    def activeWorkers():
        doc = """Number of workers available."""

        def fget(self):
            return len(self.__workersLst)

        return locals()

    activeWorkers = property(**activeWorkers())

    def output():
        doc = """"""

        def fget(self):
            return self.__collected

        return locals()

    output = property(**output())

    def progress():
        doc = """"""

        def fget(self):
            pending = self.__input.qsize()
            nCollected = len(self.__collected)
            self.debug("%d collected elements from %d inputs "
                       "(%d to be taken by %d workers)"
                       % (nCollected, self.__inputNelements, pending,
                          self.activeWorkers))
            return float(nCollected)/self.__inputNelements

        return locals()

    progress = property(**progress())

    # internal characteristics ---

    def __prepareParallel(self, parallel):
        maxParallelprocesses = _cpu_count()
        if parallel is None or parallel == 'max':
            parallel = maxParallelprocesses
        else:
            parallel = int(parallel)
            if parallel < 0:
                parallel = maxParallelprocesses + parallel
        self.__parallel = parallel
        self.debug("Will use %d cores" % (self.__parallel))

    def __prepareInputQueue(self, lst):
        for element in lst:
            self.__input.put(element)
        self.__inputNelements = len(lst)
        self.debug("input: %s (%d)" % (lst, self.__inputNelements))

    def __prepareWorkers(self):
        for i in range(self.__parallel):
            newWorker = self.__buildWorker(i)
            self.__appendWorker(newWorker)
        self.debug("%d workers prepared" % (self.activeWorkers))

    def __buildWorker(self, id):
        return _Worker(id, self.__target, self.__input, self.__output,
                       checkPeriod=self.checkPeriod,
                       startProcessEvent=self.__startProcess,
                       stepProcessEvent=self.__stepProcess,
                       pauseProcessEvent=self.__pauseProcess,
                       resumeProcessEvent=self.__resumeProcess,
                       stopProcessEvent=self.__stopProcess,
                       preHook=self.__preHook,
                       preExtraArgs=self.__preExtraArgs,
                       postHook=self.__postHook,
                       postExtraArgs=self.__postExtraArgs,)

    def __appendWorker(self, worker):
        self.__workersLst.append(worker)

    def __prepareMonitoring(self):
        self.__poolMonitor.start()

    def __poolMonitorThread(self):
        _current_thread().name = "PoolMonitor"
        while not self.__startProcess.wait(self.checkPeriod):
            self.debug("Collector prepared, but processing not started")
            # FIXME: msg to be removed, together with the timeout
        while not self.__stopProcess.is_set():
            self.__stepProcess.wait()
            self.__collectOutputs()
            self.__reviewWorkers()

    def __collectOutputs(self):
        while not self.__output.empty():
            collected = 0
            while not self.__output.empty():
                data = self.__output.get()
                collected += 1
                self.__collected.append(data)
            self.debug("collect %d outputs" % (collected))

    def __reviewWorkers(self):
        for worker in self.__workersLst:
            if not worker.isAlive():
                i = self.__workersLst.index(worker)
                self.info("pop %s from the workers list" % (worker))
                self.__workersLst.pop(i)
        if self.activeWorkers == 0:
            self.__stopProcess.set()
