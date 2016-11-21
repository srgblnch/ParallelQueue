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

from multiprocessing import current_process as _current_process
from multiprocessing import Event as _Event
from threading import Thread as _Thread
from time import sleep as _sleep

from .logger import Logger as _Logger

_CHECKPERIOD = 60  # a minute


class MonitorThread(_Logger):
    def __init__(self):
        super(MonitorThread, self).__init__()
        self._monitorThread = _Thread(target=self.__monitor)
        self._monitorThread.setDaemon(True)
        self._joinerEvent = _Event()
        self._joinerEvent.clear()
        self._workersLst = []
        self._monitorMethods = []
        self._checkPeriod = _CHECKPERIOD

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

    def __monitor(self):
        self.debug("Monitor begins")
        for worker in self._workersLst:
            self.debug("Start %s worker" % (worker.name))
            worker.start()
        while not self._procedureHasEnd():
            for method in self._monitorMethods:
                method()
            _sleep(self._checkPeriod)
        self._joinWorkers()

    def _procedureHasEnd(self):
        if self._joinerEvent.is_set():
            return True

    def _addMonitorMethod(self, method):
        self._monitorMethods.append(method)
