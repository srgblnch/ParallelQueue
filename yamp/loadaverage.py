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


class LoadAverage(object):
    def __init__(self):
        super(LoadAverage, self).__init__()
        self._loadAverage = [None, None, None]
        self._loadAverageWarning = [None, None, None]
        self._loadAverageLimit = [None, None, None]
        self._pauseDueToLoad = _Event()
        self._pauseDueToLoad.clear()

    def loadAverage():
        doc = """"""

        def fget(self):
            self._loadAverage = _getloadavg()
            return self._loadAverage

        return locals()

    loadAverage = property(**loadAverage())

    def loadAverageWarning():
        doc = """Triplet of float values that will report a warning when at
                 least one has been overcome."""

        def fget(self):
            return self._loadAverageWarning

        def fset(self, value):
            try:
                if type(value) is list and len(value) == 3:
                    lst = []
                    for v in value:
                        if v is None:
                            lst.append(v)
                        else:
                            lst.append(float(v))
                    self._loadAverageWarning = lst
            except:
                raise TypeError("a %r cannot be set as a load average warning"
                                % (value))

        return locals()

    loadAverageWarning = property(**loadAverageWarning())

    def loadAverageLimit():
        doc = """Triplet of float values that will report a warning when at
                 least one has been overcome."""

        def fget(self):
            return self._loadAverageLimit

        def fset(self, value):
            try:
                if type(value) is list and len(value) == 3:
                    lst = []
                    for v in value:
                        if v is None:
                            lst.append(v)
                        else:
                            lst.append(float(v))
                    self._loadAverageLimit = lst
            except:
                raise TypeError("a %r cannot be set as a load average warning"
                                % (value))

        return locals()

    loadAverageLimit = property(**loadAverageLimit())

    def _reviewLoadAverage(self):
        previous = self._loadAverage
        if self.__compare(self.loadAverage, self.loadAverageLimit)\
                and not self._pauseDueToLoad.is_set():
            print("%s\tALERT: load average %s pausing the processes"
                  % (_current_process(), self._loadAverage))
            self._pauseDueToLoad.set()
        elif self._pauseDueToLoad.is_set():
            print("%s\tINFO: load average %s, resuming from pause"
                  % (_current_process(), self._loadAverage))
            self._pauseDueToLoad.clear()
        elif self.__compare(self._loadAverage, self.loadAverageWarning):
            if self.__compare(self._loadAverage, previous):
                print("%s\tWARNING: load average %s"
                      % (_current_process(), self._loadAverage))
        else:
            print("%s\tDEBUG: load average %s"
                  % (_current_process(), self._loadAverage))

    def __compare(self, test, reference):
        booleans = []
        for i in range(3):
            if reference[i] is None:
                booleans.append(False)
            else:
                booleans.append(test[i] >= reference[i])
        return any(booleans)
