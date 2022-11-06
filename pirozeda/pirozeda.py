#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""This file is the main interface of the prozeda interface
it reads the data from the hardware, stores the data periodically
to the file system and provides a simple interface"""

import os
import gc
import sys
import time
from datetime import datetime
import collections
import base64
import threading
import logging, logging.handlers
import serial
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
from prozeda import ProzedaReader, ProzedaLogdata, ProzedaHistory
from datalogger import DataLogger
from pirozeda_settings import settings

logger = logging.getLogger(__name__)

formatter = logging.Formatter(
    '%(asctime)s\t%(levelname)s\t%(name)s\t%(filename)s:%(funcName)s:%(lineno)s\t%(message)s',
)

handler_stdout = logging.StreamHandler()
handler_stdout.setFormatter(formatter)
handler_file = None

# set up loggers
for logger_name in settings['logging']['loggers']:
    cfg = settings['logging']['loggers'][logger_name]
    l = logging.getLogger(logger_name)
    l.handlers.clear()
    l.setLevel(cfg["level"])
    if cfg["stdout"] is True:
        l.addHandler(handler_stdout)
    if cfg["file"] is True:
        if handler_file is None:
            handler_file = logging.handlers.RotatingFileHandler(
                settings['logging']['logfile'], maxBytes=(1048576*5), backupCount=7
            )
            handler_file.setFormatter(formatter)
        l.addHandler(handler_file)

# exception hook for logging
def _exception_hook(exctype, value, traceback):
    logger.critical("Exception: %s - %s" % (exctype, value))
    sys.__excepthook__(exctype, value, traceback)

if settings['logging']['exception_hook'] is True:
    sys.excepthook = _exception_hook

def dir_getsize(start_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def app_ramusage():
    return sum(sys.getsizeof(i) for i in gc.get_objects())

class JsonrpcRequestHandler:
    """this is the json request handler, the interface to the webserver"""

    pirozeda = None

    @classmethod
    def info(cls):
        return "Version 0.4"

    @classmethod
    def settings_get(cls):
        """Returns the settings of the system

        Return:
            dict: Dictionary of the system settings. See pirozeda_settings
        """
        return settings

    @classmethod
    def system_stats(cls, livetrace_last_timestamp=None):
        """Returns system statistics including log sizes (ram and fs), reader stats and livetraces

        Args:
            livetrace_last_timestamp (Optional[int]): timestamp (UTC) from when traces have to be
                returned. Defaults to None. If provided, the method will return all messages
                received via UART after the given timestamp

        Returns:
            dict: dictionary of the statistics.
        """

        hwinfo = cls.pirozeda.prozeda.hwinfo
        result = {
            'logsize' : dir_getsize(settings['fslog']['dir']),
            'thisram' : app_ramusage(),
            'ramlog' : {'size' : cls.pirozeda.ramlog.maxlen, 'items' : len(cls.pirozeda.ramlog)},
            'tracing' : cls.pirozeda.trace.stats(),
            'reader' : {
                'reset' :
                {
                    'time' : hwinfo.reset_last,
                    'reason' : hwinfo.reset_reason,
                    'count' : hwinfo.reset_count,
                },
                'builddate' : hwinfo.build_date,
                'version' : hwinfo.version,
                'voltage' : hwinfo.voltage,
                'stats' :
                {
                    'logdata' : cls.pirozeda.prozeda.stat_logdata_cnt,
                    'displaydata' : cls.pirozeda.prozeda.stat_displaydata_cnt,
                    'rxerror' : cls.pirozeda.prozeda.stat_rxerror_cnt,
                    'reset' : cls.pirozeda.prozeda.stat_reset_cnt,
                    'datamissing' : cls.pirozeda.prozeda.stat_datamissing_cnt,
                    'nodatareceiving' : 0,
                },
            },
            'system' : {
                'serialnumber' : cls.pirozeda.prozeda.serialnumber,
                'sysnumber' : cls.pirozeda.prozeda.systemnumber,
                'sysversion' : cls.pirozeda.prozeda.systemversion,
            },
            'livetrace' : None
        }

        if livetrace_last_timestamp is not None:
            result['livetrace'] = cls.pirozeda.trace.livetrace_get(livetrace_last_timestamp)

        return result

    @classmethod
    def current_logentry(cls, raw=False):
        """Returns the latest received log entry. Optionally including the raw received data

            Args:
                raw (Optional[bool]): If true, raw message will be returned as Hexstring.
                    Defaults to False.

            Returns:
                dict: dictionary of interpreted and optionally raw data. Keys ware 'data' and 'raw'
        """
        le = cls.pirozeda.prozeda.get_latest_logentry()
        if le:
            retval = {'data' : le.get_columns(None, True)}
            if raw == True:
                retval['raw'] = ''.join('{:02X}'.format(c) for c in le.data)
            return retval
        else:
            return None

    @classmethod
    def columnheader_get(cls, selected_columns=None, include_timestamp=False):
        """Returns all selected column information

        Args:
            selected_columns (Optional[list]): List of columns (column-indices).
                None will return all columns. Defaults to None.
            include_timestamp (Optional[bool]): Include timestamp in returned list Defaults to False

        Returns:
            list: List of columns. Column data follows format defined in pirozeda_settings resp. 
                prozeda_systems.
        """
        return ProzedaLogdata.get_column_header(selected_columns, include_timestamp)

    @classmethod
    def ramlog_getlast(cls, count=None, columns=None):
        """Returns the last entries from the ramlog.

        Args:
            count (Optional[int]): Number of log-entries to be returned.
                If None, all entries will be returned. Defaults to None.
            columns (Optional[int]): Columns to be returned, see columnheader_get.
                If None, all columns will be returned. Defaults to None
        """
        if count is None:
            count = len(cls.pirozeda.ramlog)

        retval = {
            'columns' : ProzedaLogdata.get_column_header(columns, True),
            'data' : [],
        }

        # deque doesn't support slicing, so we need to do it manually
        start = max(0, len(cls.pirozeda.ramlog) - count)
        for i in range(start, len(cls.pirozeda.ramlog)):
            item = cls.pirozeda.ramlog[i]
            if item is not None:
                item = item.get_columns(columns, True)
            retval['data'].append(item)
        return retval

    @classmethod
    def fslog_flush(cls):
        """Flushes the buffer of the filesystem log"""
        return cls.pirozeda.fslog.flush()

    @classmethod
    def fslog_read(cls, starttime, endtime, selected_columns=None):
        """Reads entries in the given time range from the file system logs.

        Args:
            startime (int): UTC timestamp from when the entries should be read.
            endtime (int): UTC timestamp until when the entries should be read.
            selected_columns (Optional[list]): List of columns that should be returned.
                Defaults to None (all columns).

        Returns:
            dict: List of found log entries.
        """
        cls.pirozeda.fslog.flush()
        return ProzedaHistory.readlogsrange_as_list(starttime, endtime, selected_columns)

    @classmethod
    def fslog_readcondensed(cls, starttime, endtime, column_index):
        """Reads one column in the given time range from the file system logs as "condensed" list

        Args:
            startime (int): UTC timestamp from when the entries should be read.
            endtime (int): UTC timestamp until when the entries should be read.
            column_index (int): index of columns that should be returned.

        Returns:
            dict: List of found log entries. Data is aligned (if possible) to the number of slots
                of measurements defined by the interval of the fslog
        """
        cls.pirozeda.fslog.flush()
        return ProzedaHistory.readlogsrange_condensed(starttime, endtime, column_index)

    @classmethod
    def display_getcurrent(cls, raw=False):
        """Returns the display content

        Args:
            raw (Optional[bool]): If true, raw message will be returned as Hexstring. 
                Defaults to False.
        """
        if not cls.pirozeda.prozeda.hist_dispdata:
            return None
        dispdata = cls.pirozeda.prozeda.hist_dispdata[-1]
        if not dispdata:
            return None
        dispdata.parse()
        result = dispdata.to_object()
        if raw:
            result['raw'] = ''.join('{:02X}'.format(c) for c in dispdata.data)
        return result

    @classmethod
    def trace_start(cls, duration):
        """Starts the file trace or bumps the trace duration and returns the info of the trace

        Args:
            duration (int): time in seconds (from now) the trace should be recorded

        Returns:
            dict: Statistics of the trace-system
        """
        cls.pirozeda.trace.start(duration)
        return cls.pirozeda.trace.stats()


    @classmethod
    def trace_stop(cls):
        """Stops the file trace"""
        cls.pirozeda.trace.stop()

    @classmethod
    def trace_live(cls, last_timestamp=0):
        """Get live messages from the UART

        Args:
            last_timestamp (Optional[int]): last timestamp (UTC) from when the trace messages
                should be returned. Defaults to 0 (all messages).

        Returns:
            dict: current timestamp (for synchronisation) List of trace messages including timestamp
        """
        return {
            'now' : time.time(),
            'data' : cls.pirozeda.trace.livetrace_get(last_timestamp)
        }

    @classmethod
    def hw_reset(cls):
        cls.pirozeda.prozeda.cmd_reset()


class ProzedaTrace(object):
    def __init__(self, fileprefix, filesuffix):
        self.fileprefix = fileprefix
        self.filesuffix = filesuffix

        self.starttime = None
        self.stoptime = None
        self.logger = None

        self.livetrace = collections.deque(maxlen=100)

    def start(self, duration, comment=None):
        if self.starttime is None:
            self.starttime = time.time()

        if duration is None:
            duration = 0
        self.stoptime = time.time() + int(duration)

        if self.logger is None:
            self.logger = DataLogger(self.fileprefix, self.filesuffix, '%Y-%m-%d_%H.%M.%S', True)

        if comment is not None and self.logger is not None:
            self.logger.write(None, 'c', comment)

    def stop(self):
        if self.logger is not None:
            self.logger.close()
        self.logger = None
        self.starttime = None
        self.stoptime = None

    def stats(self):
        result = {
            'file' : None,
            'start' : self.starttime,
            'stop' : self.stoptime,
            'remaining' : None,
            'size' : None
        }
        if self.stoptime is not None:
            result['remaining'] = self.stoptime - time.time()
        if self.logger is not None:
            result['file'] = self.logger.filename
            result['size'] = self.logger.get_filesize()
        return result

    def data_received(self, prd, timestamp, line):
        if self.stoptime and time.time() >= self.stoptime:
            self.stop()

        if self.logger is not None:
            self.logger.write(timestamp, 'd', line)

        self.livetrace.append([timestamp, line])

    def livetrace_get(self, last_timestamp=0):
        result = []
        for item in self.livetrace:
            if item[0] > last_timestamp:
                result.append(item)
        return result

class Pirozeda(object):
    def __init__(self):
        self.ramlog = collections.deque(maxlen=settings['ramlog']['length'])
        self.fslog_last = 0
        self.ramlog_last = 0
        # avoid no data received error right at the beginning
        self.commdead_last = time.time()
        self.comm_last = 0
        self.meminfo_last = 0

        strace = settings['trace']
        self.trace = ProzedaTrace(strace['dir'] + strace['prefix'], strace['suffix'])

        ProzedaLogdata.set_config(settings['system'])
        ProzedaHistory.set_config(settings)

        logger.info("Settings: %s" % (str(settings)))

        sserial = settings['serialport']
        serialport = serial.Serial(sserial['port'], sserial['baudrate'])

        self.prozeda = ProzedaReader(serialport)
        sfslog = settings['fslog']
        self.fslog = DataLogger(sfslog['dir'] + sfslog['prefix'], sfslog['suffix'])

        self.prozeda.evt_rawdata_received = self.trace.data_received

        JsonrpcRequestHandler.pirozeda = self

        self.dispatcher = {}

        for m in [
                "info", "settings_get", "system_stats", "current_logentry", "columnheader_get",
                "ramlog_getlast", "fslog_flush", "fslog_read", "fslog_readcondensed",
                "display_getcurrent", "trace_start", "trace_stop", "trace_live", "hw_reset"
        ]:
            self.dispatcher[m] = getattr(JsonrpcRequestHandler, m)

    @Request.application
    def server_application(self, request):
        #dispatcher["echo"] = lambda s: s
        response = JSONRPCResponseManager.handle(request.data, self.dispatcher)
        return Response(response.json, mimetype='application/json')

    def server_start(self):
        server_thread = threading.Thread(
            target=run_simple,
            args=(
                settings['server_address'][0],
                settings['server_address'][1],
                self.server_application))
        server_thread.daemon = True
        server_thread.start()

    def run(self):
        self.server_start()

        try:
            while True:

                time.sleep(0.1)
                ts = time.time()
                if self.prozeda.communication_alive():
                    self.comm_last = time.time()
                else:
                    # nag only every 10 seconds
                    if ts >= (self.commdead_last + 10):
                        self.commdead_last = ts
                        dur = "since startup"
                        if self.comm_last > 0:
                            dur = "for %u seconds" % (time.time() - self.comm_last)
                        logger.warning("No data received %s" % (dur))

                if ts >= (self.fslog_last + settings['fslog']['interval']):
                    self.fslog_last = ts
                    logentry = self.prozeda.get_latest_logentry()
                    # TODO: check if logentry is old
                    if logentry is not None:
                        self.fslog.write(logentry.timestamp, "d", base64.b64encode(logentry.data))
                        # fslog.flush() # only enable flush for development
                        # (log will be written to file system for every line)
                    else:
                        self.fslog.write(time.time(), "w", "no data")

                if ts >= (self.ramlog_last + settings['ramlog']['interval']):
                    self.ramlog_last = ts
                    logentry = self.prozeda.get_latest_logentry()
                    # TODO: check if logentry is old
                    if logentry is not None:
                        self.ramlog.append(logentry)

                if (settings['logging']['log_ramusage_interval'] is not None and
                    ts >= (self.meminfo_last + settings['logging']['log_ramusage_interval'])):
                    self.meminfo_last = ts
                    logger.info("Memory usage: %u" % (app_ramusage()))


        except KeyboardInterrupt:
            logger.info("Quitting... (Keyboard interrupt)")
            self.prozeda.stop()
            exit()

def main():
    """Main function of the program"""

    # before we run the actual program, let's wait until we got a "valid" system time
    # when the system starts, it lives in 1970, this is not quite useful when writing
    # logs. Therefore, it's better to wait until the system got a proper time
    while datetime.now().year < 2000:
        logger.warning("System time invalid, waiting for update...")
        time.sleep(10)

    logger.info("Ready")

    meh = Pirozeda()
    meh.run()

if __name__ == "__main__":
    main()
