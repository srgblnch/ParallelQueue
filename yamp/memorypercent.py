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
try:
    import psutil as _psutil  # soft-dependency
except:
    _psutil = None

from .logger import Logger as _Logger


class MemoryPercent(_Logger):
    def __init__(self):
        super(MemoryPercent, self).__init__()
        if _psutil is not None:
            self.__memoryPercentUsage = _psutil.virtual_memory().percent
            self.debug("Initial machine memory usage %f"
                       % (self.__memoryPercentUsage))
        else:
            self.__memoryPercentUsage = None
            self.debug("Memory management will not be available")
        self.__memoryPercentWarning = None
        self.__memoryPercentLimit = None
        self.__pauseDueToMemory = _Event()
        self.__pauseDueToMemory.clear()

    def memoryPercentUsage():
        doc = """"""

        def fget(self):
            if _psutil is not None:
                self.__memoryPercentUsage = _psutil.virtual_memory().percent
            else:
                self.__memoryPercentUsage = None
            return self.__memoryPercentUsage

        return locals()

    memoryPercentUsage = property(**memoryPercentUsage())

    def memoryPercentWarning():
        doc = """"""

        def fget(self):
            return self.__memoryPercentWarning

        def fset(self, value):
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

        return locals()

    memoryPercentWarning = property(**memoryPercentWarning())

    def memoryPercentLimit():
        doc = """"""

        def fget(self):
            return self.__memoryPercentLimit

        def fset(self, value):
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

        return locals()

    memoryPercentLimit = property(**memoryPercentLimit())

    def isPaused(self):
        return self.__pauseDueToMemory.is_set()

    def _reviewMemoryPercent(self):
        if _psutil is None:
            return
        previous = self.__memoryPercentUsage
        if self.memoryPercentLimit is not None and\
                self.memoryPercentUsage >= self.memoryPercentLimit and\
                not self.__pauseDueToMemory.is_set():
            self.critical("Memory percentage use at %f pausing the "
                          "processes" % (self.__memoryPercentUsage))
            self.__pauseDueToMemory.set()
        elif self.__pauseDueToMemory.is_set():
            self.info("Memory percentage use at %f, recovering "
                      "from pause" % (self.__memoryPercentUsage))
            self.__pauseDueToMemory.clear()
        elif self.memoryPercentWarning is not None and\
                self.__memoryPercentUsage >= self.memoryPercentWarning:
            if previous != self.__memoryPercentUsage:
                self.warning("Memory percentage use at %f"
                             % (self.__memoryPercentUsage))
        else:
            self.debug("Memory percentage use at %f"
                       % (self.__memoryPercentUsage))
