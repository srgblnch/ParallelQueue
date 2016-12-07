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

from .conditioncheck import ConditionCheck as _ConditionCheck
from os import getloadavg as _getloadavg


class LoadAverage(_ConditionCheck):
    def __init__(self, *args, **kwargs):
        super(LoadAverage, self).__init__(*args, **kwargs)
        self.__loadAverage = [None, None, None]
        self.__loadAverageWarning = [None, None, None]
        self.__loadAverageLimit = [None, None, None]

    def _getValue(self):
        self.__loadAverage = _getloadavg()
        return self.__loadAverage

    def _getWarning(self):
        return self.__loadAverageWarning

    def _setWarning(self, value):
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

    def _getLimit(self):
        return self.__loadAverageLimit

    def _setLimit(self, value):
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

    def review(self):
        previous = self.__loadAverage
        if self.__compare(self.value, self.limit) and not self._IBookPause():
            self.critical("load average %s pausing the processes"
                          % (str(self.__loadAverage)))
            self._bookPause()
        elif self._IBookPause():
            self.info("load average %s, resuming from pause"
                      % (str(self.__loadAverage)))
            self._resume()
        elif self.__compare(self.__loadAverage, self.warning):
            if self.__compare(self.__loadAverage, previous):
                self.warning("load average %s" % (str(self.__loadAverage)))
        else:
            self.debug("load average %s" % (str(self.__loadAverage)))

    def __compare(self, test, reference):
        booleans = []
        for i in range(3):
            if reference[i] is None:
                booleans.append(False)
            else:
                booleans.append(test[i] >= reference[i])
        return any(booleans)
