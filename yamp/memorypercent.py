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


class MemoryPercent(object):
    def __init__(self):
        super(MemoryPercent, self).__init__()
        if _psutil is not None:
            self._memoryPercentUsage = _psutil.virtual_memory().percent
            print("%s\tDEBUG: Initial machine memory usage %f"
                  % (_current_process(), self._memoryPercentUsage))
        else:
            self._memoryPercentUsage = None
            print("%s\tDEBUG: Memory management will not be available"
                  % (_current_process()))
        self._memoryPercentWarning = None
        self._memoryPercentLimit = None
        self._pauseDueToMemory = _Event()
        self._pauseDueToMemory.clear()

    def memoryPercentUsage():
        doc = """"""

        def fget(self):
            if _psutil is not None:
                self._memoryPercentUsage = _psutil.virtual_memory().percent
            else:
                self._memoryPercentUsage = None
            return self._memoryPercentUsage

        return locals()

    memoryPercentUsage = property(**memoryPercentUsage())

    def memoryPercentWarning():
        doc = """"""

        def fget(self):
            return self._memoryPercentWarning

        def fset(self, value):
            try:
                if value is None:  # to establish no limit
                    self._memoryPercentWarning = value
                else:
                    value = float(value)
                    if 0 < value <= 100.0:
                        self._memoryPercentWarning = value
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
            return self._memoryPercentLimit

        def fset(self, value):
            try:
                if value is None:  # to establish no limit
                    self._memoryPercentLimit = value
                else:
                    value = float(value)
                    if 0 < value <= 100.0:
                        self._memoryPercentLimit = value
                    else:
                        raise
            except:
                raise TypeError("a %r cannot be set as a memory percentage "
                                "limit" % (value))

        return locals()

    memoryPercentLimit = property(**memoryPercentLimit())

    def _reviewMemoryPercent(self):
        if _psutil is None:
            return
        previous = self._memoryPercentUsage
        if self.memoryPercentLimit is not None and\
                self.memoryPercentUsage >= self.memoryPercentLimit and\
                not self._pauseDueToMemory.is_set():
            print("%s\tALERT: memory percentage use at %f pausing the "
                  "processes" % (_current_process(),
                                 self._memoryPercentUsage))
            self._pauseDueToMemory.set()
        elif self._pauseDueToMemory.is_set():
            print("%s\tINFO: memory percentage use at %f, recovering "
                  "from pause" % (_current_process(),
                                  self._memoryPercentUsage))
            self._pauseDueToMemory.clear()
        elif self.memoryPercentWarning is not None and\
                self._memoryPercentUsage >= self.memoryPercentWarning:
            if previous != self._memoryPercentUsage:
                print("%s\tWARNING: memory percentage use at %f"
                      % (_current_process(), self._memoryPercentUsage))
        else:
            print("%s\tDEBUG: memory percentage use at %f"
                  % (_current_process(), self._memoryPercentUsage))
