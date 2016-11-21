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


from yamp import Pool
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


def tester(argin):
    from random import randint
    argout = argin**2
    sleep(randint(1, 5))
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
            sleep(obj.checkPeriod)
        res = obj.output
        res.sort()
        print("results: %s" % (res))
    else:
        print("\n\tNo default action, check help to know what can be done.\n")

if __name__ == "__main__":
    main()
