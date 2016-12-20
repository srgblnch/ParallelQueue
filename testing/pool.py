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

from datetime import datetime
from datetime import timedelta
from logging import DEBUG
import sys
from time import sleep
from yamp import Pool, version


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

MIN_T = 20
MAX_T = 60

CPUINTENSIVE = False


def tester(argin):
    from random import randint
    if CPUINTENSIVE:
        t0 = datetime.now()
        t_ = randint(MIN_T, MAX_T)
        while (datetime.now()-t0).seconds < t_:
            argout = argin**2
    else:
        sleep(randint(MIN_T, MAX_T))
        argout = argin**2
    # print("%s^2 = %s" % (argin, argout))
    return argout


def pauseTest(pool, pauseLoops):
    if pauseLoops >= 5:
        if pool.isPaused():
            print("\n\tresume...\n")
            pool.resume()
        return pauseLoops
    elif pauseLoops <= 5 and (0.3 < pool.progress < 0.7):
        if pauseLoops == 0:
            print("\n\tpause\n")
            pool.pause()
        print("\n\twait... (%d)\n" % (pauseLoops))
        sleep(MIN_T)  # pool.checkPeriod)
        return pauseLoops+1
    return pauseLoops


def main():
    from optparse import OptionParser
    parser = OptionParser()
    cmdArgs(parser)
    (options, args) = parser.parse_args()
    print("\n\tUsing yamp-%s\n" % (version()))
    if options.samples is not None:
        arginLst = range(options.samples)
        pool = Pool(tester, arginLst, options.processors, debug=True,
                    logLevel=DEBUG, log2File=True, loggerName='PoolTest',
                    loggingFolder='.')
        print("\n\tPrepared a Pool of %d workers to process %d samples. "
              "Artificially, each sample will take randomly between "
              "%d and %d seconds to complete\n"
              % (pool.activeWorkers, len(arginLst), MIN_T, MAX_T))
#         pool.loggingFolder = '.'
#         print pool.loggingFile()
        pool.checkPeriod = MAX_T*2
        sleep(1)
        pool.start()
        pauseLoops = 0
        while pool.isAlive():
            sleep(MIN_T)
            computation, perWorker = pool.computation
            for i, each in enumerate(perWorker):
                perWorker[i] = "%s" % each
            contributions = pool.contributions
            states = pool.workersStarted
            for i, each in enumerate(states):
                s = "%s" % each
                states[i] = s[0]
            progress = pool.progress
            print("\n\tprogress: %.2f%%" % ((progress)*100))
            print("\tcontributions: %s" % (contributions))
            print("\tstates: %s" % (states))
            print("\tcomputation: %s %s\n" % (computation, perWorker))
#             pauseLoops = pauseTest(pool, pauseLoops)
        res = pool.output
        res.sort()
        print("\n\tresults: %s\n" % (res))
        sys.exit(0)
    else:
        print("\tNo default action, check help to know what can be done.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
