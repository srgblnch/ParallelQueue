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
from multiprocessing import current_process as _current_process
from multiprocessing import Event as _Event
from multiprocessing import Lock as _Lock
from multiprocessing import Process as _Process
from multiprocessing import Queue as _Queue
from time import sleep as _sleep

from traceback import print_exc as _print_exc

from .loadaverage import LoadAverage as _LoadAverage
from .memorypercent import MemoryPercent as _MemoryPercent
from .monitorthread import MonitorThread as _MonitorThread


class Pool(_LoadAverage, _MemoryPercent, _MonitorThread):
    def __init__(self, target, arginLst, parallel=None):
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
        super(self.__class__, self).__init__()
        # prepare the parameters ---
        self.__target = target
        self.__parallel = None
        self.__lastWorkerId = None
        self.__input = _Queue()
        self.__output = _Queue()
        self.__collected = []
        # self._locker = _Lock()  # TODO: for the logging
        # setup ---
        self.__prepareParallel(parallel)
        self.__prepareInputQueue(arginLst)
        self.__prepareWorkers()
        self.__prepareMonitoring()

    # Interface ---

    def start(self):
        self.debug("Start()")
        _MonitorThread.start(self)

    def stop(self):
        self.debug("Stop()")
        _MonitorThread.stop(self)

    def isAlive(self):
        return _MonitorThread.isAlive(self)

    def is_alive(self):
        return self.isAlive()

    def isPaused(self):
        return _LoadAverage.isPaused(self) or _MemoryPercent.isPaused(self)

    def is_paused(self):
        return self.isPaused()

    def output():
        doc = """"""

        def fget(self):
            return self.__collected

        return locals()

    output = property(**output())

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
        self.debug("input: %s" % (lst))

    def __prepareWorkers(self):
        if self.__lastWorkerId is None:
            workerIds = range(self.__parallel)
        else:
            workerIds = range(self.__lastWorkerId, self.__parallel)
        for self.__lastWorkerId in workerIds:
            newWorker = self.__buildWorker(self.__lastWorkerId)
            self._appendWorker(newWorker)
        self.debug("%d workers prepared" % (self.activeWorkers))

    def __buildWorker(self, id):
        return _Process(target=self.__worker, name=str("%d" % (id)),
                        args=(id,))

    def __worker(self, id):
        self.debug("Worker %d starts" % (id))
        while not self._procedureHasEnd():
            try:
                if self.isPaused():
                    self.info("Worker %d paused" % (id))
                    while self.isPaused():
                        _sleep(self.checkPeriod)  # FIXME: use a wait()
                    self.info("Worker %d resume" % (id))
                else:
                    argin = self.__input.get()
                    self.info("Worker %d in  %s" % (id, argin))
                    argout = self.__target(argin)
                    self.info("Worker %d out %s" % (id, argout))
                    self.__output.put((argin, argout))
                    # TODO: hook with a method to be called, using a lock
                    #       between those process with what ever the user
                    #       likes to execute. For example store results in a
                    #       file.
            except Exception as e:
                self.error("Worker %d exception: %s" % (id, e))
                _print_exc()

    def _procedureHasEnd(self):
        if _MonitorThread._procedureHasEnd(self):
            return True
        return self.__input.empty()

    def __prepareMonitoring(self):
        self._addMonitorMethod(self._reviewProcessesState)
        self._addMonitorMethod(self._collectOutputs)
        self._addMonitorMethod(self._reviewLoadAverage)
        self._addMonitorMethod(self._reviewMemoryPercent)

    def _reviewProcessesState(self):
        pidsLst = self.workerPIDs
        while not all([True if pid is not None else False for pid in pidsLst]):
            try:
                idx = pidsLst.index(None)
            except:
                pass
            else:
                deadWorker = self._popWorker(idx)
                self.warning("Worker %s hasn't PID, replacing it\n"
                             % (deadWorker.name))
                self.__lastWorkerId += 1
                newWorker = buildWorker(self.__lastWorkerId)
                self._appendWorker(newWorker)
                newWorker.start()
                deadWorker.join()

    def _collectOutputs(self):
        while not self.__output.empty():
            collected = 0
            while not self.__output.empty():
                data = self.__output.get()
                collected += 1
                self.__collected.append(data)
            self.debug("collect %d outputs" % (collected))
