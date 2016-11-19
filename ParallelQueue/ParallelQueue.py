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


from multiprocessing import cpu_count as _cpu_count
from multiprocessing import current_process as _current_process
from multiprocessing import Lock as _Lock
from multiprocessing import Process as _Process
from multiprocessing import Queue as _Queue


class ParallelQueue(object):
    def __init__(self, method, arginLst, processors=None):
        """
            Build an object with the capacity to execute multiple process with
            the same method. It will build a pool of processes where they will
            take elements in a shared queue until the queue is empty.
            
            Arguments:
            - method: Method that each of the parallel process will be
              executing with the input arguments. It must be callable with
              objects in the list as parameters.
            - arginLst: python list where each element is data input for the
              method that will be executed in parallel.
            - processors: (optional) to establish the number of parallel
              processes that will participate. By default the maximum possible
              based on the number of cores available.
        """
        super(self.__class__, self).__init__()
        # prepare the parameters ---
        self._method = method
        maxParallelprocesses = cpu_count()
        if processors is None or processors == 'max':
            processors = maxParallelprocesses
        else:
            processors = int(processors)
            if processors < 0:
                processors = maxParallelprocesses + processors
        # prepare the parallel objects ---
        self._locker = _Lock()
