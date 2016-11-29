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

from os import getloadavg as _getloadavg
from multiprocessing import current_process as _current_process
from multiprocessing import Event as _Event

from .logger import Logger as _Logger


class LoadAverage(_Logger):
    def __init__(self):
        super(LoadAverage, self).__init__()
        self.__loadAverage = [None, None, None]
        self.__loadAverageWarning = [None, None, None]
        self.__loadAverageLimit = [None, None, None]
        self.__pauseDueToLoad = _Event()
        self.__pauseDueToLoad.clear()

    def loadAverage():
        doc = """"""

        def fget(self):
            self.__loadAverage = _getloadavg()
            return self.__loadAverage

        return locals()

    loadAverage = property(**loadAverage())

    def loadAverageWarning():
        doc = """Triplet of float values that will report a warning when at
                 least one has been overcome."""

        def fget(self):
            return self.__loadAverageWarning

        def fset(self, value):
            try:
                if type(value) is list and len(value) == 3:
                    lst = []
                    for v in value:
                        if v is None:
                            lst.append(v)
                        else:
                            lst.append(float(v))
                    self.__loadAverageWarning = lst
            except:
                raise TypeError("a %r cannot be set as a load average warning"
                                % (value))

        return locals()

    loadAverageWarning = property(**loadAverageWarning())

    def loadAverageLimit():
        doc = """Triplet of float values that will report a warning when at
                 least one has been overcome."""

        def fget(self):
            return self.__loadAverageLimit

        def fset(self, value):
            try:
                if type(value) is list and len(value) == 3:
                    lst = []
                    for v in value:
                        if v is None:
                            lst.append(v)
                        else:
                            lst.append(float(v))
                    self.__loadAverageLimit = lst
            except:
                raise TypeError("a %r cannot be set as a load average warning"
                                % (value))

        return locals()

    loadAverageLimit = property(**loadAverageLimit())

    def isPaused(self):
        return self.__pauseDueToLoad.is_set()

    def _reviewLoadAverage(self):
        previous = self.__loadAverage
        if self.__compare(self.loadAverage, self.loadAverageLimit)\
                and not self.__pauseDueToLoad.is_set():
            self.critical("load average %s pausing the processes"
                          % (str(self.__loadAverage)))
            self.__pauseDueToLoad.set()
            self._pauseWorkers()
        elif self.__pauseDueToLoad.is_set():
            self.info("load average %s, resuming from pause"
                      % (str(self.__loadAverage)))
            self.__pauseDueToLoad.clear()
            self._resumeWorkers()
        elif self.__compare(self.__loadAverage, self.loadAverageWarning):
            if self.__compare(self.__loadAverage, previous):
                self.warning("load average %s" % (str(self.__loadAverage)))
        else:
            pass
            # self.debug("load average %s" % (str(self.__loadAverage)))

    def __compare(self, test, reference):
        booleans = []
        for i in range(3):
            if reference[i] is None:
                booleans.append(False)
            else:
                booleans.append(test[i] >= reference[i])
        return any(booleans)
