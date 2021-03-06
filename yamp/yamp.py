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

from datetime import datetime as _datetime
from datetime import timedelta as _timedelta
from .events import EventManager as _EventManager
from .loadaverage import LoadAverage as _LoadAverage
from .logger import Logger as _Logger
from .memorypercent import MemoryPercent as _MemoryPercent
from multiprocessing import cpu_count as _cpu_count
from multiprocessing import Event as _Event
from multiprocessing import Queue as _Queue
from threading import current_thread as _current_thread
from threading import Thread as _Thread
from time import sleep as _sleep
from version import version as _version
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
        super(Pool, self).__init__(*args, **kwargs)
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
        self.__loadAverage = _LoadAverage(*args, **kwargs)
        self._instances.append(self.__loadAverage)
        self.__memoryPercent = _MemoryPercent(*args, **kwargs)
        self._instances.append(self.__memoryPercent)
        self.__events = _EventManager()
        self.__events.loggingFolder = self.loggingFolder
        self.__events.loggerName = self.loggerName
        self.__events.logLevel = self.logLevel
        self.__events.logEnable = self.logEnable
        self._instances.append(self.__events)
        # hooks ---
        self.__preHook = preHook
        self.__preExtraArgs = preExtraArgs
        self.__postHook = postHook
        self.__postExtraArgs = postExtraArgs
        # setup ---
        self.__prepareParallel(parallel)
        self.__prepareInputQueue(arginLst)
        self.__prepareWorkers(*args, **kwargs)
        self.__prepareMonitoring()
        self.debug("Prepared a yamp.Pool() version %s" % (_version()))

    # Interface ---

    def start(self):
        self.info("START has been requested to the Pool")
        self.__events.start()

    def pause(self):
        self.info("PAUSE has been requested to the Pool")
        self.__events.pause()

    def isPaused(self):
        return self.__events.isPaused()

    def is_paused(self):
        return self.isPaused()

    def resume(self):
        self.info("RESUME has been requested to the Pool")
        self.__events.resume()

    def stop(self):
        self.info("STOP has been requested to the Pool")
        self.__events.stop()

    def isAlive(self):
        return self.__poolMonitor.isAlive()

    def is_alive(self):
        return self.isAlive()

    def waitUntilFinish(self):
        return self.__events.waitStop()

    # properties

    @property
    def checkPeriod(self):
        return self.__checkPeriod

    @checkPeriod.setter
    def checkPeriod(self, value):
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

    def activeWorkers():
        doc = """Number of workers available."""

        def fget(self):
            return self.workersStarted.count(True)

        return locals()

    activeWorkers = property(**activeWorkers())

    @property
    def output(self):
        return self.__collected

    @property
    def progress(self):
        pending = self.__input.qsize()
        nCollected = len(self.__collected)
        self.debug("%d collected elements from %d inputs "
                   "(%d to be taken by %d workers)"
                   % (nCollected, self.__inputNelements, pending,
                      self.activeWorkers))
        progress = float(nCollected)/self.__inputNelements
        return progress

    @property
    def workersStarted(self):
        states = []
        for worker in self.__workersLst:
            try:
                states.append(worker.isStarted())
            except Exception as e:
                self.error("Cannot get the state of %s" % (worker))
                states.append(None)
        self.debug("Checked states: %s" % states)
        return states

    @property
    def contributions(self):
        contributions = []
        for worker in self.__workersLst:
            try:
                contributions.append(worker.contribution)
            except Exception as e:
                self.error("Cannot get the contribution of %s" % (worker))
                contributions.append(None)
        self.debug("Checked contributions: %s" % contributions)
        return contributions

    @property
    def computation(self):
        ts = []
        tg = 0.0
        for worker in self.__workersLst:
            try:
                tw = worker.computation
                ts.append(_timedelta(seconds=tw))
                tg += tw
            except Exception as e:
                self.error("Cannot get the computation of %s" % (worker))
                ts.append(None)
        t0 = self.__events.whenStarted()
        t_diff = _datetime.now()-t0
        tg = _timedelta(seconds=tg)
        ratio = tg.total_seconds()/t_diff.total_seconds()
        self.debug("Since %s (%s ago) %s of parallel computations (x%.2f)"
                   "(reported by workers) distributed in [%s]"
                   % (t0, t_diff, tg, ratio,
                      "".join("%s, " % i for i in ts)[:-2]))
        return tg, ts

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
        self.info("Will use %d workers" % (self.__parallel))

    def __prepareInputQueue(self, lst):
        for element in lst:
            self.__input.put(element)
        self.__inputNelements = len(lst)
        if self.__inputNelements > 10:
            head = "%s" % lst[:5]
            tail = "%s" % lst[-5:]
            lstStr = "%s (...) %s" % (head[:-1], tail[1:])
        else:
            lstStr = "%s" % (lst)
        self.debug("input: %s (%d)" % (lstStr, self.__inputNelements))

    def __prepareWorkers(self, *args, **kwargs):
        for i in range(self.__parallel):
            newWorker = self.__buildWorker(i, *args, **kwargs)
            self.__appendWorker(newWorker)
            self._instances.append(newWorker)
            _sleep(0.1)  # to give space to the worker monitor thread
        self.debug("%d workers ready" % (self.activeWorkers))

    def __buildWorker(self, id, *args, **kwargs):
        worker = _Worker(id, self.__target, self.__input, self.__output,
                         checkPeriod=self.checkPeriod,
                         preHook=self.__preHook,
                         preExtraArgs=self.__preExtraArgs,
                         postHook=self.__postHook,
                         postExtraArgs=self.__postExtraArgs, *args, **kwargs)
        while not worker.prepared():
            self.debug("Worker%d not yet prepared, wait" % (id))
            worker.waitPrepared(1)
        return worker

    def __appendWorker(self, worker):
        self.__workersLst.append(worker)

    def __prepareMonitoring(self):
        self.__poolMonitor.start()

    def __poolMonitorThread(self):
        _current_thread().name = "PoolMonitor"
        while not self.__events.waitStart(self.checkPeriod):
            self.debug("Collector prepared, but processing not started")
            # FIXME: msg to be removed, together with the timeout
        while not self.__events.isStopped():
            if self.__events.waitStep(self.checkPeriod):
                self.__events.stepClean()
                self.debug("STEP event received")
                self.__collectOutputs()
            else:
                self.debug("Periodic check")
            self.__reviewWorkers()
            self.__loadAverage.review()
            self.__memoryPercent.review()
        while self.activeWorkers > 0:
            self.debug("Waiting workers to finish")
            self.__reviewWorkers()
            if self.activeWorkers > 0:
                _sleep(self.checkPeriod)
        self.debug("Pool complete, exiting")

    def __collectOutputs(self):
        while not self.__output.empty():
            collected = 0
            while not self.__output.empty():
                data = self.__output.get()
                collected += 1
                self.__collected.append(data)
            self.debug("collect %d outputs" % (collected))
            if self.logEnable:
                self.progress
                self.contributions
                self.computation
        if len(self.__collected) == self.__inputNelements:
            self.info("All %d inputs processed and collected"
                      % (self.__inputNelements))
            self.stop()

    def __reviewWorkers(self):
        for i, worker in enumerate(self.__workersLst):
            if not worker.isAlive():
                if self.progress > 100:
                    self.warning("Worker %s is not alive! Rebuild it"
                                 % (worker.id))
                    self.__workersLst[i] = self.__buildWorker(i)
                else:
                    self.info("pop %s from the workers list" % (worker))
                    self.__workersLst.pop(i)
#             elif self.__events.isStarted() and\
#                     not worker.isStarted() and\
#                     not worker._endProcedure():
#                 self.warning("Worker %d hasn't start when it should have "
#                              "(event: %s, worker: %s)"
#                              % (i, self.__events.isStarted(),
#                                 worker.isStarted()))
        if self.activeWorkers == 0:
            self.__events.stop()
