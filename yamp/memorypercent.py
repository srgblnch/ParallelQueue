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
try:
    import psutil as _psutil  # soft-dependency
except:
    _psutil = None


class MemoryPercent(_ConditionCheck):
    def __init__(self, *args, **kwargs):
        super(MemoryPercent, self).__init__(*args, **kwargs)
        if _psutil is not None:
            self.__memoryPercentUsage = _psutil.virtual_memory().percent
            self.debug("Initial machine memory usage %f"
                       % (self.__memoryPercentUsage))
        else:
            self.__memoryPercentUsage = None
            self.debug("Memory management will not be available")
        self.__memoryPercentWarning = None
        self.__memoryPercentLimit = None

    def _getValue(self):
        if _psutil is not None:
            self.__memoryPercentUsage = _psutil.virtual_memory().percent
        else:
            self.__memoryPercentUsage = None
        return self.__memoryPercentUsage

    def _getWarning(self):
        return self.__memoryPercentWarning

    def _setWarning(self, value):
        try:
            if value is None:  # to establish no limit
                self.__memoryPercentWarning = value
            else:
                value = float(value)
                if 0 < value <= 100.0:
                    self.__memoryPercentWarning = value
                else:
                    raise
        except:
            raise TypeError("a %r cannot be set as a memory percentage "
                            "warning" % (value))

    def _getLimit(self):
        return self.__memoryPercentLimit

    def _setLimit(self, value):
        try:
            if value is None:  # to establish no limit
                self.__memoryPercentLimit = value
            else:
                value = float(value)
                if 0 < value <= 100.0:
                    self.__memoryPercentLimit = value
                else:
                    raise
        except:
            raise TypeError("a %r cannot be set as a memory percentage "
                            "limit" % (value))

    def review(self):
        # FIXME: use self.value instead of __getValue()
        # FIXME: use self.warning instead of __getWarning()
        # FIXME: use self.limit instead of __getLimit()
        if _psutil is None:
            return
        previous = self.__memoryPercentUsage
        if self.limit is not None and self.value >= self.limit and\
                not self._IBookPause():
            self.critical("Memory percentage use at %f pausing the "
                          "processes" % (self.__memoryPercentUsage))
            self._bookPause()
        elif self._IBookPause():
            self.info("Memory percentage use at %f, recovering "
                      "from pause" % (self.__memoryPercentUsage))
            self._resume()
        elif self.warning is not None and\
                self.__memoryPercentUsage >= self.warning:
            if previous != self.__memoryPercentUsage:
                self.warning("Memory percentage use at %f"
                             % (self.__memoryPercentUsage))
        else:
            self.debug("Memory percentage use at %f"
                       % (self.__memoryPercentUsage))
