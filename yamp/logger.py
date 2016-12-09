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
from threading import current_thread as _current_thread
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

    def __init__(self, debug=False, logLevel=_logging.INFO, log2File=False,
                 loggerName=None, loggingFolder=None):
        super(Logger, self).__init__()
        # prepare internal vbles ---
        self.__logEnable = debug
        self.__logLevel = logLevel
        self.__log2file = log2File
        self.__loggerName = loggerName or 'yamp'
        self.__loggingFolder = loggingFolder
        self.__loggingFile = None
        self._instances = []  # FIXME: this is dirty and ugly
        # setup the object ---
        self.__devlogger = _logging.getLogger(self.__loggerName)
        self.__handler = None
        self.__prepareHandler()

    def logMessage(self, msg, level):
        _tag = self._levelStr[level]
        prt_msg = "%8s - %s - %s - %s - %s" % (_tag, self.__loggerName,
                                               _current_process().name,
                                               _current_thread().name, msg)
        if self.__logEnable and level >= self.__logLevel:
            if self.__log2file:
                method = {self.CRITICAL: self.__devlogger.critical,
                          self.ERROR: self.__devlogger.error,
                          self.WARNING: self.__devlogger.warn,
                          self.INFO: self.__devlogger.info,
                          self.DEBUG: self.__devlogger.debug}
                method[level](msg)
            with lock:
                when = str(_datetime.now())
                print("%s - %s" % (when, prt_msg))

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

    def __prepareHandler(self):
        if not len(self.__devlogger.handlers):
            self.__devlogger.setLevel(_logging.DEBUG)
            self.__handler = \
                _logging.handlers.RotatingFileHandler(self.loggingFile,
                                                      maxBytes=10000000,
                                                      backupCount=5)
            self.__handler.setLevel(_logging.NOTSET)
            formatter = _logging.Formatter('%(asctime)s - %(levelname)s - '
                                           '%(name)s - %(processName)s - '
                                           '%(threadName)s - %(message)s')
            self.__handler.setFormatter(formatter)
            self.__devlogger.addHandler(self.__handler)
        else:
            self.__handler = self.__devlogger.handlers[0]

    def __prepareLogging(self):
        if self.__loggingFolder is None:
            logging_folder = "/var/log/%s" % (self.__loggerName)
            if not self.__buildLoggingFolder(logging_folder):
                logging_folder = "/tmp/log/%s" % (self.__loggerName)
                if not self.__buildLoggingFolder(logging_folder):
                    raise SystemError("No folder for logging available")
            self.__loggingFolder = logging_folder
        else:
            if not self.__buildLoggingFolder(self.__loggingFolder):
                raise SystemError("No folder for logging available")

    def __buildLoggingFolder(self, folder):
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)
            return True
        except:
            return False

    def logEnable():
        doc = """"""

        def fget(self):
            return self.__logEnable

        def fset(self, value):
            if type(value) is not bool:
                raise AssertionError("The value must be boolean")
            self.__logEnable = value
            for child in self._instances:
                child.logEnable = value

        return locals()

    logEnable = property(**logEnable())

    def logLevel():
        doc = """"""

        def fget(self):
            return self.__logLevel

        def fset(self, level):
            if type(level) not in [int, long]:
                raise AssertionError("The value must be integer")
            self.__devlogger.setLevel(level)
            if self.__handler is not None:
                self.__handler.setLevel(level)
            self.__logLevel = level
            for child in self._instances:
                child.logLevel = value

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
            for child in self._instances:
                child.log2file = value

        return locals()

    log2file = property(**log2file())

    def loggerName():
        doc = """"""

        def fget(self):
            self.__prepareLogging()
            return self.__loggerName

        def fset(self, name):
            backName = self.__loggerName
            self.__loggerName = name
            try:
                self.__prepareLogging()
            except Exception as e:
                self.__loggerName = backName
                self.error("CANNOT set %s as logging folder: %s" % (name, e))
            for child in self._instances:
                child.loggerName = value

        return locals()

    loggerName = property(**loggerName())

    def loggingFolder():
        doc = """"""

        def fget(self):
            self.__prepareLogging()
            return self.__loggingFolder

        def fset(self, folder):
            backFolder = self.__loggingFolder
            self.__loggingFolder = folder
            try:
                self.__prepareLogging()
            except Exception as e:
                self.__loggingFolder = backFolder
                self.error("CANNOT set %s as logging folder: %s" % (folder, e))
            for child in self._instances:
                child.loggingFolder = value

        return locals()

    loggingFolder = property(**loggingFolder())

    def loggingFile():
        doc = """"""

        def fget(self):
            if self.__loggingFile is None:
                self.__loggingFile = \
                    "%s/%s.log" % (self.loggingFolder, self.__loggerName)
            return self.__loggingFile

        return locals()

    loggingFile = property(**loggingFile())


class Singleton(Logger):
    """
        A superclass found in stackoverflow [1]
[1]: http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """
    _instances = {}
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def __init__(self, *args, **kwargs):
        super(Singleton, self).__init__(*args, **kwargs)
