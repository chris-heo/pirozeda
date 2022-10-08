# -*- coding: utf-8 -*-
"""Reads data from the Prozeda adapter"""

import threading
from datetime import datetime
import time
import collections
import re
from .prozedalog import ProzedaLogdata
from .prozedadisplay import ProzedaDisplaydata

class ProzedaCommError():
    """Communication errors detected either by the microcontroller or ProzedaReader"""

    def __init__(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self.timestamp = timestamp

class ProzedaReaderInfo():
    def __init__(self):
        self.reset_last = None
        self.reset_reason = None
        self.reset_count = None
        self.build_date = None
        self.version = None
        self.uptime_last = None
        self.voltage = None

    def parse(self, txt, timestamp):
        if txt.startswith("Built on:"):
            self.reset_last = timestamp
            res = re.findall(r"Built on: ([ADFJMNOS][abceglnoprtuvy]{2} +\d+ \d+ \d+:\d+:\d+)", txt)
            if res:
                dt = datetime.strptime(res[0], "%b %d %Y %H:%M:%S")
                self.build_date = time.mktime(dt.timetuple())
        elif txt.startswith("Version:"):
            self.version = txt[9:]
        elif txt.startswith("Info:"):
            regex = re.compile("Info: Last reset due to ([A-Z ]+)"
                               ", (?:no previous reboot|reboot #(\\d+))"
                               "(?:, uptime was (\\d+))?")
            res = re.findall(regex, txt)
            if res:
                self.reset_reason = res[0][0]
                if res[0][1] != '':
                    self.reset_count = int(res[0][1])
                else:
                    self.reset_count = None
                if res[0][2] != '':
                    self.uptime_last = int(res[0][2])
                else:
                    self.uptime_last = None

            res = re.findall(r"Info: Supply voltage = (\d+) mV", txt)
            if res:
                self.voltage = int(res[0])

class ProzedaReader():
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

        # Stats
        self.stat_logdata_cnt = 0
        self.stat_displaydata_cnt = 0
        self.stat_rxerror_cnt = 0
        self.stat_reset_cnt = 0
        self.stat_datamissing_cnt = 0

        # prozeda system information
        self.serialnumber = None
        self.systemnumber = None
        self.systemversion = None

        self.hwinfo = ProzedaReaderInfo()

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

    def rx_headerdata(self, data, timestamp):
        """called when header data is received"""
        o = 3
        segment = data[0+o]
        if segment == 0xFA:
            try:
                self.serialnumber = (data[0x21+o:0x2A+o] + data[0x31+o:0x36+o]).decode("utf8")
            except:
                pass
            self.systemnumber = data[0x39+o] << 8 | data[0x38+o]
            self.systemversion = data[0x3B+o] << 8 | data[0x3A+o]


    def rx_error(self, data, timestamp):
        """called when a error was detected by the microcontroller"""
        self.stat_rxerror_cnt += 1
        self.last_error = timestamp
        #res = re.findall(r"rxErr:(Len|CRC) e:([0-9A-F]+), a:([0-9A-F]+)", data, re.IGNORECASE)
        #if res:
        #    res[0][0]: Len|CRC
        #    res[0][1]: Expected
        #    res[0][2]: Actual

        if callable(self.evt_error_received):
            self.evt_error_received(self, timestamp, "RxError")

    def rx_hw_reset(self, timestamp):
        """called when a hardware reset was detected"""
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

            try:
                line = str(self.ser.readline(), 'utf8')
                line = line.replace("\r", "").replace("\n", "")
                timestamp = time.time()

                if callable(self.evt_rawdata_received):
                    self.evt_rawdata_received(self, timestamp, line)

                if line.startswith("Logdata:"):
                    data = bytearray.fromhex(line[8:])
                    self.rx_logdata(data, timestamp)
                elif line.startswith("Display:"):
                    data = bytearray.fromhex(line[8:])
                    self.rx_displaydata(data, timestamp)
                elif line.startswith("Header:"):
                    data = bytearray.fromhex(line[7:])
                    self.rx_headerdata(data, timestamp)
                elif line.startswith("Built on:"):
                    self.rx_hw_reset(timestamp)
                    self.hwinfo.parse(line, timestamp)
                elif line.startswith("Version:") or line.startswith("Info:"):
                    self.hwinfo.parse(line, timestamp)
                elif line.startswith("rxErr"):
                    self.rx_error(line, timestamp)
                elif line == "":
                    # nothing received, this is usually when the serial port was closed
                    self.rx_data_missing(timestamp)
                elif line.startswith("Cmd:") or line.startswith("Messages"):
                    pass # ignore
                else:
                    print("received odd data: \"%s\"" % line)
            except:
                self.rx_error(line, timestamp)


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

    def cmd_reset(self):
        """commands the microcontroller to reset"""
        self.ser.write("reset\n".encode("ascii"))

    def cmd_uptime(self):
        """commands the microcontroller to return uptime"""
        self.ser.write("uptime\n".encode("ascii"))

    def cmd_bootinfo(self):
        """commands the microcontroller to return boot info"""
        self.ser.write("bootinfo\n".encode("ascii"))

    def cmd_header(self):
        """commands the microcontroller to output headers for the amount of configured messages"""
        self.ser.write("header\n".encode("ascii"))

if __name__ == '__main__':
    print('you\'re not supposed to run this file')
