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
from threading import Thread as _Thread


_CHECKPERIOD = 60  # a minute


class Pool(object):
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
        self._target = target
        maxParallelprocesses = _cpu_count()
        if parallel is None or parallel == 'max':
            parallel = maxParallelprocesses
        else:
            parallel = int(parallel)
            if parallel < 0:
                parallel = maxParallelprocesses + parallel
        self._parallel = parallel
        print("Will use %d cores" % (self._parallel))
        self._workersLst = []
        self.__prepareWorkers()
        self._monitorThread = _Thread(target=self.__monitor)
        # prepare the parallel objects ---
        self._checkPeriod = _CHECKPERIOD
        self._idx = 0
        self._joinerEvent = _Event()
        self._joinerEvent.clear()
        # self._locker = _Lock()  # TODO: for the logging
        self._queue = _Queue()
        for element in arginLst:
            self._queue.put(element)
        self._output = _Queue()
        self._collectedOutput = []

    def activeWorkers():
        doc = """"""

        def fget(self):
            return len(self._workersLst)

        return locals()

    activeWorkers = property(**activeWorkers())

    def checkPeriod():
        doc = """Period, in seconds that the monitor thread will check the
                 parallel processes."""

        def fget(self):
            return self._checkPeriod

        def fset(self, value):
            try:
                self._checkPeriod = int(value)
            except:
                raise TypeError("a %r cannot be set as a check period"
                                % (type(value)))

        return locals()

    checkPeriod = property(**checkPeriod())

    def output():
        doc = """"""

        def fget(self):
            return self._collectedOutput

        return locals()

    output = property(**output())

    def start(self):
        print("%s\tStart()" % (_current_process()))
        self._monitorThread.start()

    def stop(self):
        print("%s\tStop()" % (_current_process()))
        self._joinerEvent.set()

    def isAlive(self):
        return self._monitorThread.isAlive()

    def __prepareWorkers(self):
        for self._idx in range(self._parallel):
            self._workersLst.append(self.__buildWorker(self._idx))
        print("%s\t%d workers prepared" % (_current_process(), self._idx))

    def __buildWorker(self, id):
        return _Process(target=self.__worker, name=str("%d" % (id)),
                        args=(id,))

    def __monitor(self):
        print("%s\tMonitor begins" % (_current_process()))
        for worker in self._workersLst:
            print("%s\tStart %s worker" % (_current_process(), worker))
            worker.start()
        while not self.__procedureHasEnd():
            self.__reviewProcessesState()
            self.__collectOutputs()
            # TODO: review memory use of this process and the workers
            _sleep(self._checkPeriod)
        self.__joinWorkers()

    def __procedureHasEnd(self):
        # TODO: extend
        if self._joinerEvent.is_set():
            return True
        return self._queue.empty()

    def __reviewProcessesState(self):
        pidsLst = [w.pid for w in self._workersLst]
        while not all([True if pid is not None else False for pid in pidsLst]):
            try:
                idx = pidsLst.index(None)
            except:
                pass
            else:
                deadWorker = workersLst.pop(idx)
                print("%s\tWorker %s hasn't PID, replacing it\n"
                      % (_current_process(), deadWorker.name))
                self._idx += 1
                newWorker = buildWorker(self._idx)
                workersLst.append(newWorker)
                newWorker.start()
                deadWorker.join()

    def __collectOutputs(self):
        while not self._output.empty():
            data = self._output.get()
            print("%s\tcollect %d outputs: %s"
                  % (_current_process(), len(data), data))
            self._collectedOutput.append(data)

    def __joinWorkers(self):
        while len(self._workersLst) > 0:
            print("%s\tjoin %d workers" % (_current_process(),
                                           len(self._workersLst)))
            for w in self._workersLst:
                if not w.is_alive():
                    w.join(1)
                    self._workersLst.pop(self._workersLst.index(w))
                    print("%s\t%s still alive" % (_current_process(), w))
            _sleep(self._checkPeriod)
            # TODO: do something with workers that never ends.

    def __worker(self, id):
        print("%s\tWorker %d starts" % (_current_process(), id))
        while not self.__procedureHasEnd():
            try:
                argin = self._queue.get()
                print("%s\tWorker %d in  %s" % (_current_process(), id, argin))
                argout = self._target(argin)
                print("%s\tWorker %d out %s"
                      % (_current_process(), id, argout))
                self._output.put((argin, argout))
                # TODO: hook with a method to be called, using a lock between
                #       those process with what ever the user likes to execute.
                #       For example store results in a file.
            except Exception as e:
                pass  # TODO: log it


def cmdArgs(parser):
    '''Include all the command line parameters to be accepted and used.
    '''
#     parser.add_option('', "--loglevel", type="str",
#                       help="output prints log level: "
#                            "{error,warning,info,debug,trace}.")
    parser.add_option('', "--processors", type="str",
                      help="Tell the application how many processors will be "
                      "used. A positive number will establish the number of "
                      "parallel workers and each will use one of the cores. "
                      "With the string'max' the application will use all the "
                      "available cores. Telling a negative number with be "
                      "understood as how many below the maximum will be used.")
    parser.add_option('', "--samples", type="int",
                      help="How many elements will be set in the arginLst.")


def tester(argin):
    from random import randint
    argout = argin**2
    _sleep(randint(1, 5))
    print("%s^2 = %s" % (argin, argout))
    return argout


def main():
    from optparse import OptionParser
    parser = OptionParser()
    cmdArgs(parser)
    (options, args) = parser.parse_args()
    if options.samples is not None:
        arginLst = range(options.samples)
        obj = Pool(tester, arginLst, options.processors)
        obj.checkPeriod = 1
        obj.start()
        while obj.isAlive():
            _sleep(obj.checkPeriod)
        print("results: %s" % (obj.output))
    else:
        print("\n\tNo default action, check help to know what can be done.\n")

if __name__ == "__main__":
    main()
