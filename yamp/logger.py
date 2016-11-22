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

from datetime import datetime as _datetime
import logging as _logging
from logging import handlers as _handlers
from multiprocessing import current_process as _current_process
from multiprocessing import Lock as _Lock
import os


global lock
lock = _Lock()


class Logger(object):

    NOTSET = _logging.NOTSET
    CRITICAL = _logging.CRITICAL
    ERROR = _logging.ERROR
    WARNING = _logging.WARNING
    INFO = _logging.INFO
    DEBUG = _logging.DEBUG

    _levelStr = {_logging.NOTSET: '',
                 _logging.CRITICAL: 'CRITICAL',
                 _logging.ERROR: 'ERROR',
                 _logging.WARNING: 'WARNING',
                 _logging.INFO: 'INFO',
                 _logging.DEBUG: 'DEBUG'}

    def __init__(self, debug=False, loggerName=None):
        super(Logger, self).__init__()
        # prepare internal vbles ---
        self.__debugFlag = _logging.debug
        self.__debuglevel = 0
        self.__log2file = False
        self.__loggerName = loggerName or 'yamp'
        self.__logging_folder = None
        self.__logging_file = None
        # setup the object ---
        self.loggingFile()
        self._devlogger = _logging.getLogger(self.__loggerName)
        self._handler = None
        if not len(self._devlogger.handlers):
            self._devlogger.setLevel(_logging.DEBUG)
            self._handler = \
                _logging.handlers.RotatingFileHandler(self.__logging_file,
                                                     maxBytes=10000000,
                                                     backupCount=5)
            self._handler.setLevel(_logging.NOTSET)
            formatter = _logging.Formatter('%(asctime)s - %(levelname)s - '
                                          '%(name)s - %(message)s')
            self._handler.setFormatter(formatter)
            self._devlogger.addHandler(self._handler)
        else:
            self._handler = self._devlogger.handlers[0]

    def logEnable():
        doc = """"""

        def fget(self):
            return self.__debugFlag

        def fset(self, value):
            if type(value) is not bool:
                raise AssertionError("The value must be boolean")
            self.__debugFlag = value

        return locals()

    logEnable = property(**logEnable())

    def logLevel():
        doc = """"""

        def fget(self):
            return self.__debuglevel

        def fset(self, value):
            if type(value) not in [int, long]:
                raise AssertionError("The value must be integer")
            self.__debuglevel = level
            self._devlogger.setLevel(level)
            if self._handler is not None:
                self._handler.setLevel(level)

        return locals()

    logLevel = property(**logLevel())

    def log2file():
        doc = """"""

        def fget(self):
            return self.__log2file

        def fset(self, value):
            if type(value) is not bool:
                raise AssertionError("The value must be boolean")
            self.__log2file = value

        return locals()

    log2file = property(**log2file())

    def logMessage(self, msg, level):
        _tag = self._levelStr[level]
        prt_msg = "%s - %s - %s - %s" % (_tag, self.__loggerName,
                                         _current_process().name, msg)
        if self.__log2file:
            method = {self.CRITICAL: self._devlogger.critical,
                      self.ERROR: self._devlogger.error,
                      self.WARNING: self._devlogger.warn,
                      self.INFO: self._devlogger.info,
                      self.DEBUG: self._devlogger.debug}
            method[level](msg)
        if self.__debugFlag and level >= self.__debuglevel:
            with lock:
                when = str(_datetime.now())
                print("%s %s" % (when, prt_msg))

    def critical(self, msg):
        self.logMessage(msg, self.CRITICAL)

    def error(self, msg):
        self.logMessage(msg, self.ERROR)

    def warning(self, msg):
        self.logMessage(msg, self.WARNING)

    def info(self, msg):
        self.logMessage(msg, self.INFO)

    def debug(self, msg):
        self.logMessage(msg, self.DEBUG)

    def loggingFolder(self):
        if self.__logging_folder is None:
            logging_folder = "/var/log/%s" % (self.__loggerName)
            if not self.__buildLoggingFolder(logging_folder):
                logging_folder = "/tmp/log/%s" % (self.__loggerName)
                if not self.__buildLoggingFolder(logging_folder):
                    raise SystemError("No folder for logging available")
            self.__logging_folder = logging_folder
        else:
            if not self.__buildLoggingFolder(self.__logging_folder):
                raise SystemError("No folder for logging available")
        return self.__logging_folder

    def loggingFile(self):
        if self.__logging_file is None:
            self.__logging_file = \
                "%s/%s.log" % (self.loggingFolder(), self.__loggerName)
        return self.__logging_file

    def __buildLoggingFolder(self, folder):
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)
            return True
        except:
            return False
