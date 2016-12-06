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

from datetime import timedelta
from yamp import Pool, version
from time import sleep


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


def tester(argin):
    from random import randint
    argout = argin**2
    sleep(randint(MIN_T, MAX_T))
    print("%s^2 = %s" % (argin, argout))
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
        pool = Pool(tester, arginLst, options.processors)
        print("\n\tPrepared a Pool of %d workers to process %d samples. "
              "Artificially, each sample will take randomly between "
              "%d and %d seconds to complete\n"
              % (pool.activeWorkers, len(arginLst), MIN_T, MAX_T))
#         pool.loggingFolder = '.'
#         print pool.loggingFile()
        pool.log2file = True
        pool.checkPeriod = MAX_T*2
        sleep(1)
        pool.start()
        pauseLoops = 0
        while pool.isAlive():
            sleep(MIN_T)
            computation, _ = pool.computation
            contributions = pool.contributions
            progress = pool.progress
            print("\n\tprogress: %.2f%%" % ((progress)*100))
            print("\tcontributions: %s" % (contributions))
            print("\tcomputation: %s\n" % (computation))
#             pauseLoops = pauseTest(pool, pauseLoops)
        res = pool.output
        res.sort()
        print("\n\tresults: %s\n" % (res))
    else:
        print("\tNo default action, check help to know what can be done.\n")

if __name__ == "__main__":
    main()
