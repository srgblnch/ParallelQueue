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

from .logger import Singleton as _Singleton
from multiprocessing import Event as _Event
from multiprocessing import current_process as _current_process
from threading import current_thread as _current_thread
from traceback import print_exc as _print_exc


class EventManager(_Singleton):
    def __init__(self):
        super(EventManager, self).__init__()
        self.__startEvent = _Event()
        self.__stepEvent = _Event()
        self.__pauseEvent = _Event()
        self.__pauseRequesterStack = []
        self.__resumeEvent = _Event()
        self.__stopEvent = _Event()

    def start(self):
        # FIXME: this shall be only emitted by MainProcess, MainThread
        if not self.__startEvent.is_set():
            self.__startEvent.set()
            self.debug("START event emitted")
            return True
        return False

    def isStarted(self):
        return self.__startEvent.is_set()

    def step(self):
        # FIXME: this shall only be emitted by Workers
        self.__stepEvent.set()
        self.debug("STEP event emitted")
    
    def stepClean(self):
        self.__stepEvent.clear()
        self.debug("STEP event catch")

    def pause(self, book=False):
        """
            With this method the requester will ask emit the pause event.
            It can book the request to allow only itself to release the pause.
        """
        try:
            self.__storeRequester(book)
            self.__emitPause()
            return True
        except Exception as e:
            self.error("PAUSE request failed due to: %s" % (e))
            _print_exc()
            return False

    def isPaused(self):
        return self.__pauseEvent.is_set() and not self.__resumeEvent.is_set()

    def resume(self):
        """
            With this method the requester will ask to resume the process.
            When itself is is the list of requesters, it will be removed from
            there, or will remove one of the non-book requesters.
            Only when the list is empty will the pause event be clear and
            resume emitted.
        """
        try:
            if self.__popRequester():
                return self.__emitResume()
        except Exception as e:
            self.error("RESUME request failed due to: %s" % (e))
            _print_exc()
        return False

    def stop(self):
        # FIXME: should it filter who can raise this event?
        if not self.__stopEvent.is_set():
            self.__stopEvent.set()
            self.debug("STOP event emitted")
            return True
        return False

    def isStopped(self):
        return self.__stopEvent.is_set()

    def waitStart(self, timeout=None):
        return self.__startEvent.wait(timeout)

    def waitStep(self, timeout=None):
        return self.__stepEvent.wait(timeout)

    def waitPause(self, timeout=None):
        return self.__pauseEvent.wait(timeout)

    def waitResume(self, timeout=None):
        return self.__resumeEvent.wait(timeout)

    def waitStop(self, timeput=None):
        return self.__stopEvent.wait(timeout)

    # pause & resume ---

    def __searchRequester(self):
        nonBookRequest = None
        processName = _current_process().name
        threadName = _current_thread().name
        for i, request in enumerate(self.__pauseRequesterStack):
            if request[0] == processName and request[1] == threadName:
                self.debug("Found (%s, %s) as requester in position %d"
                           % (processName, threadName, i))
                return (True, i)
            elif nonBookRequest is None and request[2] == False:
                nonBookRequest = i
        self.debug("NOT found (%s, %s) as requester"
                   % (processName, threadName))
        if nonBookRequest is not None:
            self.debug("But a nonBook request found from (%s, %s)"
                       % (self.__pauseRequesterStack[nonBookRequest][0],
                          self.__pauseRequesterStack[nonBookRequest][1]))
        return (False, nonBookRequest)

    def __storeRequester(self, book):
        processName = _current_process().name
        threadName = _current_thread().name
        self.__pauseRequesterStack.append([processName, threadName, book])
        self.debug("Stored (%s, %s) as a requester (book=%s)"
                   % (processName, threadName, book))

    def __popRequester(self):
        found, pos = self.__searchRequester()
        if found or pos is not None:
            self.__pauseRequesterStack.pop(pos)
            processName = _current_process().name
            threadName = _current_thread().name
            self.debug("Removed '%d'th requester" % (pos))
            return True
        self.debug("pop unsatisfied")
        return False

    def __emitPause(self):
        if self.__resumeEvent.is_set():
            self.__resumeEvent.clear()
        if not self.__pauseEvent.is_set():
            self.__pauseEvent.set()
            self.debug("PAUSE event emitted")
            return True
        return False

    def __emitResume(self):
        if len(self.__pauseRequesterStack) == 0:
            if self.__pauseEvent.is_set():
                self.__pauseEvent.clear()
            if not self.__resumeEvent.is_set():
                self.__resumeEvent.set()
            self.debug("RESUME event emitted")
            return True
        self.debug("Resume stack with %d elements"
                   % (len(self.__pauseRequesterStack)))
        return False
