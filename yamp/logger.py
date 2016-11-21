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

from datetime import datetime
import logging as _logging
from logging import handlers as _handlers
from multiprocessing import current_process as _current_process
import os


class Logger(object):

    NOTSET = _logging.NOTSET
    DEBUG = _logging.DEBUG
    INFO = _logging.INFO
    WARNING = _logging.WARNING
    ERROR = _logging.ERROR
    CRITICAL = _logging.CRITICAL

    def __init__(self, debug=False, loggerName=None):
        super(Logger, self).__init__()
        self._debug = _logging.debug
        self._debuglevel = 0
        self._log2file = False
        if loggerName is not None:
            self._loggerName = loggerName
        else:
            self._loggerName = 'yamp'
        self.__logging_folder = \
            os.path.abspath(os.path.dirname(__file__))+"/logs/"
        self.__logging_file = self.__logging_folder+self._loggerName+".log"
        if not os.path.exists(self.__logging_folder):
            os.makedirs(self.__logging_folder)
        self._devlogger = _logging.getLogger(self._loggerName)
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

    # logEnable(dbg=False) #
    #  This function enables the debug information through screen (To log
    #  file is always enabled)
    #  @param dbg (not mandatory) enables/disables the log oputput. By
    #  default is disabled
    def logEnable(self, dbg=False):
        self._debug = dbg
        self.logMessage("logEnable()::Debug level set to %s"
                        % (self._debug), self.INFO)

    # logState() #
    #  This function returns the log enabled/disabled status
    #  @return Debug state
    def logState(self):
        return self._debug

    # logLevel(level) #
    #  This function sets a debug level
    #  @param level debug level to be set
    def logLevel(self, level):
        self._debuglevel = level
        self._devlogger.setLevel(level)
        if self._handler is not None:
            self._handler.setLevel(level)

    # logGetLevel() #
    #  This function returns the log level set
    #  @return Debug level set
    def logGetLevel(self):
        return self._debuglevel

    # logMessage(msg, level) #
    #  Private function that prints a log message to log file and to screen
    #  (if enabled)
    #  @param msg Message to print
    #  @param level Message debug level
    def logMessage(self, msg, level):
        prt_msg = self._loggerName+" - "+_current_process().name+" - "+msg
        if level == self.CRITICAL:
            if self._log2file:
                self._devlogger.critical(msg)
            prt_msg = "CRITICAL - "+prt_msg
        elif level == self.ERROR:
            if self._log2file:
                self._devlogger.error(msg)
            prt_msg = "ERROR    - "+prt_msg
        elif level == self.WARNING:
            if self._log2file:
                self._devlogger.warn(msg)
            prt_msg = "WARNING  - "+prt_msg
        elif level == self.INFO:
            if self._log2file:
                self._devlogger.info(msg)
            prt_msg = "INFO     - "+prt_msg
        else:
            if self._log2file:
                self._devlogger.debug(msg)
            prt_msg = "DEBUG    - "+prt_msg
        if self._debug and level >= self._debuglevel:
            print("%s %s" % (str(datetime.now()), prt_msg))

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
