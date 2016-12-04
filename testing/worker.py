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

from yamp import Worker
from multiprocessing import Event as _Event
from multiprocessing import Lock as _Lock
from multiprocessing import Queue as _Queue
from random import randint as _randint
from time import sleep


def preProcess(argin, **kwargs):
    lock = kwargs['lock']
    with lock:
        print("> pre-processing: %s" % (str(argin)))
        sleep(0.1)
        print("< pre-processing")


def target(argin):
    print("> process")
    sleep(1)
    print("< process")
    return _randint(0, 100)


def postProcess(argin, argout, **kwargs):
    lock = kwargs['lock']
    with lock:
        print("> post-processing: %s -> %s" % (str(argin), str(argout)))
        sleep(0.1)
        if argin == kwargs['breaker']:
            print("< breaker!!")
            kwargs['worker'].stop()
        else:
            print("< post-processing")


def firstTest():
    id = 0
    input = _Queue()
    for i in range(10):
        input.put(i)
    output = _Queue()
    # TODO: play with the checkPeriod
    start = _Event()
    step = _Event()
    pause = _Event()
    resume = _Event()
    stop = _Event()
    printerLock = _Lock()
    print("\n\tFirst test:")
    worker = Worker(id, target, input, output, debug=True)
    worker.start()
    sleep(3)
    worker.pause()
    sleep(3)
    worker.resume()
    while worker.isAlive():
        sleep(3)
    print("\n\tTest passed")


def secondTest():
    id = 1
    input = _Queue()
    for i in range(10):
        input.put(i)
    output = _Queue()
    # TODO: play with the checkPeriod
    start = _Event()
    step = _Event()
    pause = _Event()
    resume = _Event()
    stop = _Event()
    printerLock = _Lock()
    print("\n\tSecond test:")
    worker = Worker(id, target, input, output, debug=True)
    worker.postHook = postProcess
    worker.postExtraArgs = {'lock': printerLock,
                            'breaker': 8, 'worker': worker}
    worker.start()
    while worker.isAlive():
        sleep(3)
        worker.pause()
        sleep(3)
        worker.resume()
        sleep(3)
    print("\n\tTest passed")


def main():
    firstTest()
    secondTest()

if __name__ == "__main__":
    main()
