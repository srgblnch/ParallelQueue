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

from .events import EventManager as _EventManager
from .logger import Logger as _Logger
from multiprocessing import Event as _Event


class ConditionCheck(_Logger):
    def __init__(self, *args, **kwargs):
        super(ConditionCheck, self).__init__(*args, **kwargs)
        self.__IPaused = _Event()
        self.__events = _EventManager()

    def _IBookPause(self):
        return self.__IPaused.is_set()

    def _bookPause(self):
        self.__events.pause(book=True)
        self.__IPause.set()

    def _resume(self):
        self.__events.resume()
        self.__IPause.clear()

    def value():
        def fget(self):
            return self._getValue()

        return locals()

    value = property(**value())

    def _getValue(self):
        raise NotImplementedError("Subclass must implement it")

    def warning():
        def fget(self):
            return self._getWarning()

        def fset(self, value):
            self._setWarning(value)

        return locals()

    warning = property(**warning())

    def _getWarning(self):
        raise NotImplementedError("Subclass must implement it")
    
    def _setWarning(self, value):
        raise NotImplementedError("Subclass must implement it")

    def limit():
        def fget(self):
            return self._getLimit()

        def fset(self, value):
            self._setLimit(value)

        return locals()

    limit = property(**limit())

    def _getLimit(self):
        raise NotImplementedError("Subclass must implement it")
    
    def _setLimit(self, value):
        raise NotImplementedError("Subclass must implement it")

    def review(self):
        raise NotImplementedError("Subclass must implement it")
