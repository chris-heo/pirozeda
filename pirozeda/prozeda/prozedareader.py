# -*- coding: utf-8 -*-
"""Reads data from the Prozeda adapter"""

from __future__ import print_function
import threading
import time
import collections
from .prozedalog import ProzedaLogdata
from .prozedadisplay import ProzedaDisplaydata

class ProzedaCommError(object):
    """Communication errors detected either by the microcontroller or ProzedaReader"""

    def __init__(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self.timestamp = timestamp

class ProzedaReader(object):
    """Reader for the data aquired by the microcontroller"""

    def __init__(self, serialport, logcount=10, dispcount=10):
        self.ser = serialport
        self.thread_serial = threading.Thread(target=self.serialreader_run, args=())
        self.thread_serial.daemon = True

        self.readerrunning = True
        self.last_error = None
        self.hist_logdata = collections.deque(maxlen=logcount)
        self.hist_dispdata = collections.deque(maxlen=dispcount)
        #self.hist_commerror = collections.deque(maxlen=errcount) #TODO: implement

        # Callbacks
        self.evt_rawdata_received = None
        self.evt_logdata_received = None
        self.evt_displaydata_received = None
        self.evt_error_received = None

        #stats
        self.stat_resettime = time.time()
        self.stat_logdata_cnt = 0
        self.stat_displaydata_cnt = 0
        self.stat_rxerror_cnt = 0
        self.stat_reset_cnt = 0
        self.stat_datamissing_cnt = 0
        

        self.thread_serial.start()

    def stop(self):
        """stops the reader"""
        self.readerrunning = False
        self.ser.close()

    def rx_logdata(self, data, timestamp):
        """called when new log data is received"""
        self.stat_logdata_cnt += 1
        entry = ProzedaLogdata(data, timestamp)
        self.hist_logdata.append(entry)
        if callable(self.evt_logdata_received):
            self.evt_logdata_received(self, entry)

    def rx_displaydata(self, data, timestamp):
        """called when new display data is received"""
        self.stat_displaydata_cnt += 1
        entry = ProzedaDisplaydata(data, timestamp)
        self.hist_dispdata.append(entry)
        if callable(self.evt_displaydata_received):
            self.evt_displaydata_received(self, entry)

    def rx_error(self, timestamp):
        """called when a error was detected by the microcontroller"""
        self.stat_rxerror_cnt += 1
        self.last_error = timestamp
        if callable(self.evt_error_received):
            self.evt_error_received(self, timestamp, "RxError")

    def hw_reset(self, timestamp):
        """called when a error was detected by the microcontroller"""
        self.stat_reset_cnt += 1
        self.last_error = timestamp
        if callable(self.evt_error_received):
            self.evt_error_received(self, timestamp, "Reset")

    def rx_data_missing(self, timestamp):
        """called when no data is received"""
        self.stat_reset_cnt += 1
        self.last_error = timestamp
        if callable(self.evt_error_received):
            self.evt_error_received(self, timestamp, "DataMissing")

    def serialreader_run(self):
        """
            receiver thread
        """
        while True:
            if not self.readerrunning:
                return

            line = self.ser.readline().replace("\r", "").replace("\n", "")
            timestamp = time.time()

            if callable(self.evt_rawdata_received):
                self.evt_rawdata_received(self, timestamp, line)

            try:
                if line.startswith("Logdata:"):
                    data = bytearray.fromhex(line[8:])
                    self.rx_logdata(data, timestamp)
                elif line.startswith("Display:"):
                    data = bytearray.fromhex(line[8:])
                    self.rx_displaydata(data, timestamp)
                elif line.startswith("Header:"):
                    pass
                    #TODO: implement
                elif line.startswith("Built on:"):
                    self.hw_reset(timestamp)
                elif line == "rxErr":
                    self.rx_error(timestamp)
                elif line == "":
                    # nothing received, this is usually when the serial port was closed
                    self.rx_data_missing(timestamp)
                else:
                    print("received odd data: \"%s\"" % line)
            except:
                self.rx_error(timestamp)


    def communication_alive(self, timeout=10):
        """returns true if the communication is alive and false if not
        only logdata is used but it these are missing something is terribly wrong.
        """

        if not self.hist_logdata:
            return False
        elif self.hist_logdata[-1].timestamp < (time.time() - timeout):
            return False
        return True

    def get_latest_logentry(self):
        """returns the latest log entry received"""
        if not self.hist_logdata:
            return None
        return self.hist_logdata[-1]

if __name__ == '__main__':
    print('you\'re not supposed to run this file')
