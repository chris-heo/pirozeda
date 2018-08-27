# -*- coding: utf-8 -*-
"""This file is the main interface of the prozeda interface
it reads the data from the hardware, stores the data periodically
to the file system and provides a simple interface"""

from __future__ import print_function
import os
import gc, sys
import time
from datetime import datetime, timedelta
import collections
import base64
import threading
import pyjsonrpc
from prozeda import ProzedaReader, ProzedaLogdata, ProzedaHistory
from datalogger import DataLogger
import serial
from pirozeda_settings import settings

def dir_getsize(start_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def app_ramusage():
    return sum(sys.getsizeof(i) for i in gc.get_objects())

class JsonrpcRequestHandler(pyjsonrpc.HttpRequestHandler):
    """this is the json request handler, the interface to the webserver"""

    pirozeda = None

    @pyjsonrpc.rpcmethod
    def info(self):
        return "Version 0.2"

    @pyjsonrpc.rpcmethod
    def settings_get(self):
        return settings
    
    @pyjsonrpc.rpcmethod
    def system_stats(self, livetrace_last_timestamp=None):
        result = {
                'logsize' : dir_getsize(settings['fslog']['dir']),
                'thisram' : app_ramusage(),
                'ramlog' : {'size' : self.pirozeda.ramlog.maxlen, 'items' : len(self.pirozeda.ramlog)},
                'tracing' : self.pirozeda.trace.stats(),
                'reader' : {
                    'resettime' : self.pirozeda.prozeda.stat_resettime,
                    'logdata' : self.pirozeda.prozeda.stat_logdata_cnt,
                    'displaydata' : self.pirozeda.prozeda.stat_displaydata_cnt,
                    'rxerror' : self.pirozeda.prozeda.stat_rxerror_cnt,
                    'reset' : self.pirozeda.prozeda.stat_reset_cnt,
                    'datamissing' : self.pirozeda.prozeda.stat_datamissing_cnt,
                    'nodatareceiving' : 0,
                },
                'livetrace' : None
            }
        
        if livetrace_last_timestamp is not None:
            result['livetrace'] = self.pirozeda.trace.livetrace_get(livetrace_last_timestamp)
        
        return result
    
    @pyjsonrpc.rpcmethod
    def current_logentry(self, raw=False):
        le = self.pirozeda.prozeda.get_latest_logentry()
        if le:
            retval = {'data' : le.get_columns(None, True)}
            if raw == True:
                retval['raw'] = ''.join('{:02X}'.format(c) for c in le.data)
            return retval
        else:
            return None

    @pyjsonrpc.rpcmethod
    def columnheader_get(self, selected_columns=None, include_timestamp=False):
        """
            Returns all selected column names
        """
        return ProzedaLogdata.get_column_header(selected_columns, include_timestamp)

    @pyjsonrpc.rpcmethod
    def ramlog_getlast(self, count=None, columns=None):
        """
            Returns the last <count> entries of the ramlog.
            If <count> is omitted or None, all entries will be returned
        """
        if count is None:
            count = len(self.pirozeda.ramlog)

        retval = {
                'columns' : ProzedaLogdata.get_column_header(columns, True),
                'data' : [],
            }

        # deque doesn't support slicing, so we need to do it on our own
        start = max(0, len(self.pirozeda.ramlog) - count)
        for i in range(start, len(self.pirozeda.ramlog)):
            item = self.pirozeda.ramlog[i]
            if item is not None:
                item = item.get_columns(columns, True)
            retval['data'].append(item)
        return retval

    @pyjsonrpc.rpcmethod
    def fslog_flush(self):
        """
            Flushes the buffer of the filesystem log
        """
        return self.pirozeda.fslog.flush()
    
    @pyjsonrpc.rpcmethod
    def fslog_read(self, starttime, endtime, selected_columns=None):
        self.pirozeda.fslog.flush()
        return ProzedaHistory.readlogsrange_as_list(starttime, endtime, selected_columns)

    def fslog_readcondensed(self, starttime, endtime, column_index):
        self.pirozeda.fslog.flush()
        return ProzedaHistory.readlogsrange_condensed(starttime, endtime, column_index)

    @pyjsonrpc.rpcmethod
    def display_getcurrent(self, raw=False):
        """
            Returns the display content
        """
        if not self.pirozeda.prozeda.hist_dispdata:
            return None
        dispdata = self.pirozeda.prozeda.hist_dispdata[-1]
        if not dispdata:
            return None
        dispdata.parse()
        result = dispdata.to_object()
        if raw:
            result['raw'] = ''.join('{:02X}'.format(c) for c in dispdata.data)
        return result
    
    @pyjsonrpc.rpcmethod
    def trace_start(self, duration):
        """
            Starts the file trace or bumps the trace duration and returns the info of the trace
        """
        self.pirozeda.trace.start(duration)
        return self.pirozeda.trace.stats()

    
    @pyjsonrpc.rpcmethod
    def trace_stop(self):
        """
            Stops the file trace
        """
        self.pirozeda.trace.stop()

    @pyjsonrpc.rpcmethod
    def trace_live(self, last_timestamp=0):
        return {
                'now' : time.time(),
                'data' : self.pirozeda.trace.livetrace_get(last_timestamp)
            }

    @staticmethod
    def startserver():
        http_server = pyjsonrpc.ThreadingHttpServer(
            server_address=settings['server_address'],
            RequestHandlerClass=JsonrpcRequestHandler
        )

        server_thread = threading.Thread(target=http_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()


class ProzedaTrace(object):
    def __init__(self, fileprefix, filesuffix):
        self.fileprefix = fileprefix
        self.filesuffix = filesuffix

        self.starttime = None
        self.stoptime = None
        self.logger = None
        
        self.livetrace = collections.deque(maxlen=100)
    
    def start(self, duration, comment=None):
        if self.starttime == None:
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
        result = {'file' : None, 'start' : self.starttime, 'stop' : self.stoptime, 'remaining' : None, 'size' : None }
        if self.stoptime is not None:
            result['remaining'] = self.stoptime - time.time()
        if self.logger is not None:
            result['file'] = self.logger.filename
            result['size'] = self.logger.get_filesize()
        return result

    def data_received(self, prd, timestamp, line):
        if time.time() >= self.stoptime:
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

        strace = settings['trace']
        self.trace = ProzedaTrace(strace['dir'] + strace['prefix'], strace['suffix'])

        ProzedaLogdata.set_config(settings['system'])
        ProzedaHistory.set_config(settings)

        sserial = settings['serialport']
        serialport = serial.Serial(sserial['port'], sserial['baudrate'])

        self.prozeda = ProzedaReader(serialport)
        sfslog = settings['fslog']
        self.fslog = DataLogger(sfslog['dir'] + sfslog['prefix'], sfslog['suffix'])

        self.prozeda.evt_rawdata_received = self.trace.data_received

        JsonrpcRequestHandler.pirozeda = self

    def run(self):
        JsonrpcRequestHandler.startserver()

        try:
            while True:

                time.sleep(0.1)
                ts = time.time()
                if not self.prozeda.communication_alive():
                    # nag only every 10 seconds
                    if ts >= (self.commdead_last + 10):
                        self.commdead_last = ts
                        print("no data received")

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

        except KeyboardInterrupt:
            print("quitting...")
            self.prozeda.stop()
            exit()

def main():
    """Main function of the program"""

    # before we run the actual program, let's wait until we got a "valid" system time
    # when the system starts, it lives in 1970, this is not quite useful when writing
    # logs. Therefore, it's better to wait until the system got a proper time
    while datetime.now().year < 2000:
        print("system time invalid, waiting for NTP update...")
        time.sleep(10)
    
    print("ready.")

    meh = Pirozeda()
    meh.run()

if __name__ == "__main__":
    main()
