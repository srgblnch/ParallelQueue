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
from hashlib import sha256
from logging import DEBUG
from optparse import OptionParser
from os import listdir
from os.path import isdir, islink, expanduser, getsize
from multiprocessing import Lock as _Lock
from time import sleep
from yamp import Pool, version


def prepareFileLst(basePath, hiddenFiles=False, followSymlinks=False):
    try:
        basePath = expanduser(basePath)
        pathFiles = listdir(basePath)
        answer = []
        for fileName in pathFiles:
            if not hiddenFiles and fileName.startswith('.'):
                pass
#                 print("Excluding hidden file: %s" % (fileName))
            if not followSymlinks and islink("%s/%s" % (basePath, fileName)):
                pass
#                 print("Excluding hidden file: %s" % (fileName))
            elif isdir("%s/%s" % (basePath, fileName)):
#                 print("%s/%s is a directory" % (basePath, fileName))
                subdirFiles = prepareFileLst("%s/%s" % (basePath, fileName))
#                 print("Directory contents: %s" % subdirFiles)
                for subFile in subdirFiles:
                    if not isdir(subFile):
                        answer.append(subFile)
            else:
#                 print("Append %s/%s" % (basePath, fileName))
                answer.append("%s/%s" % (basePath, fileName))
        return answer
    except Exception as e:
        print("Exception %s" % e)
        return []


def hasher(argin):
    hash = sha256()
    with open(argin, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    sleep(0.1)
    return hash.hexdigest()


def output(argin, argout, **kwargs):
    lock = kwargs['lock']
    outputFile = kwargs['outputFile']
    with lock:
        with open(outputFile, 'a') as f:
            f.write("%s\t%s\t%s\n" % (argin, argout, getsize(argin)))


def cmdArgs(parser):
    '''Include all the command line parameters to be accepted and used.
    '''
    parser.add_option('', "--processors", type="str",
                      help="Tell the application how many processors will be "
                      "used. A positive number will establish the number of "
                      "parallel workers and each will use one of the cores. "
                      "With the string'max' the application will use all the "
                      "available cores. Telling a negative number with be "
                      "understood as how many below the maximum will be used.")
    parser.add_option('', "--directory", type="str",
                      help="Path where calculate the hashes.")
    parser.add_option('', "--with-hidden-files", default=False,
                      help="Include hidden files.")
    parser.add_option('', "--follow-symlinks", default=False,
                      help="Get into symlinks.")
    parser.add_option('-o', "--output", default="hash.txt",
                      help="File name to write the output.")


MIN_T = 10


def main():
    parser = OptionParser()
    cmdArgs(parser)
    (options, args) = parser.parse_args()
    print("\n\tUsing yamp-%s\n" % (version()))
    if options.directory is not None:
        printerLock = _Lock()
        arginLst = prepareFileLst(options.directory, options.with_hidden_files,
                                  options.follow_symlinks)
        pool = Pool(hasher, arginLst, options.processors, debug=True,
                    logLevel=DEBUG, log2File=True, loggerName='Hasher',
                    loggingFolder='.', postHook=output,
                    postExtraArgs={'lock': printerLock,
                                   'outputFile': './hashlst'})
        pool.start()
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
        res = pool.output
        res.sort()
        print("\n\tresults: %s\n" % (res))
    else:
        print("\tNo default action, check help to know what can be done.\n")


if __name__ == "__main__":
    main()

