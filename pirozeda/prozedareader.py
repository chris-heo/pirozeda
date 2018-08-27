"""Reads data from the Prozeda adapter"""

from __future__ import print_function
import threading
import time
import collections
import serial

class ProzedaLogdata(object):
    """Prozeda log data periodically sent by the controller"""

    def __init__(self, data, timestamp=None):
        self.data = data
        if timestamp is None:
            timestamp = time.time()

        self.timestamp = timestamp

        """parsed data from msg"""
        self.date = None
        self.time = None
        self.seconds = None
        self.temperature = [None] * 12
        self.adcs = [None] * 2 # element 0 seems to be system voltage
        self.output = [None] * 7
        self.error = [None] * 0
        self.storage = [None] * 2
        self.dummy = [None] * 3
        self.function_active = [None] * 4
        self.flow_rate = None
        self.tapping = None
        self.unknown = None
        self.checksum = None

        self.parsed = False

    def parse(self, force=False):
        """maps the received data to the values"""
        if not force and self.parsed:
            # only parse if forced or not already parsed
            return
        if len(self.data) != 68:
            return
        #SOF - ignore
        pos = 2
        self.date, pos = self.parse_uint16(pos, self.data)
        self.time, pos = self.parse_uint16(pos, self.data)
        #self.seconds, pos = self.parse_uint16(pos, self.data)
        for i in range(len(self.temperature)):
            tmp, pos = self.parse_int16(pos, self.data)
            self.temperature[i] = float(tmp) / 10
        for i in range(len(self.adcs)):
            tmp, pos = self.parse_uint8(pos, self.data)
            self.adcs[i] = float(tmp) / 10
        for i in range(len(self.output)):
            self.output[i], pos = self.parse_uint8(pos, self.data)
        for i in range(len(self.error)):
            self.error[i], pos = self.parse_uint8(pos, self.data)
        #self.storage[0], pos = self.parse_uintN(pos, self.data, 4)
        self.dummy[0], pos = self.parse_uint16(pos, self.data)
        self.storage[1], pos = self.parse_uint16(pos, self.data)
        self.dummy[1], pos = self.parse_uint16(pos, self.data)
        for i in range(len(self.function_active)):
            self.function_active[i], pos = self.parse_uint16(pos, self.data)
        self.flow_rate, pos = self.parse_uint16(pos, self.data)
        self.tapping, pos = self.parse_int16(pos, self.data)
        self.dummy[2], pos = self.parse_uint16(pos, self.data)
        self.unknown, pos = self.parse_uint8(pos, self.data)
        #checksum - ignore (it's already checked in the microcontroller)
        self.parsed = True

    def to_object(self):
        """returns the captured data as an object"""
        self.parse()
        return {"timestamp" : self.timestamp, "temperature" : self.temperature, "output" : self.output}

    @staticmethod
    def parse_uint8(pos, data):
        """parses an uint8 at the given position of data"""
        val = data[pos]
        return (val, pos + 1)

    @staticmethod
    def parse_uint16(pos, data):
        """parses an uint16 at the given position of data"""
        val = data[pos] | (data[pos+1] << 8)
        return (val, pos + 2)

    @staticmethod
    def parse_uintN(pos, data, cnt):
        """parses an uint with N bytes at the given position of data"""
        val = 0
        for i in range(cnt):
            val |= data[pos] << (i * 8)
            pos += 1
        return (val, pos)

    @staticmethod
    def parse_int16(pos, data):
        """parses an int16 at the given position of data"""
        val = data[pos] | (data[pos+1] << 8)
        if val > 0x8000:
            val -= 0x10000
        return (val, pos + 2)

class ProzedaDisplaydata(object):
    """display data periodically sent by the controller"""

    def __init__(self, data, timestamp=None):
        self.data = data
        if timestamp is None:
            timestamp = time.time()
        self.timestamp = timestamp

class ProzedaCommError(object):
    """Communication errors reported either by the microcontroller or ProzedaReader"""

    def __init__(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self.timestamp = timestamp

class ProzedaReader(object):
    """Reader for the data on the wire aquired by the microcontroller"""

    def __init__(self, serialport, logcount=10, dispcount=10):
        self.ser = serial.Serial(serialport, 115200)
        self.thread_serial = threading.Thread(target=self.serialreader_run, args=())
        self.thread_serial.daemon = True

        self.readerrunning = True
        self.rx_error_count = 0
        self.last_error = None
        self.hist_logdata = collections.deque(maxlen=logcount)
        self.hist_dispdata = collections.deque(maxlen=dispcount)
        #self.hist_commerror = collections.deque(maxlen=errcount) #TODO: implement

        # Callbacks
        self.evt_logdata_received = None
        self.evt_displaydata_received = None
        self.evt_error_received = None

        self.thread_serial.start()

    def stop(self):
        """stops the reader"""
        self.readerrunning = False
        self.ser.close()

    def rx_logdata(self, data, timestamp):
        """called when new log data is received"""
        entry = ProzedaLogdata(data, timestamp)
        self.hist_logdata.append(entry)
        if callable(self.evt_logdata_received):
            self.evt_logdata_received(self, entry)

    def rx_displaydata(self, data, timestamp):
        """called when new display data is received"""
        entry = ProzedaDisplaydata(data, timestamp)
        self.hist_dispdata.append(entry)
        if callable(self.evt_displaydata_received):
            self.evt_displaydata_received(self, entry)

    def rx_error(self, timestamp):
        """called when a error was detected by the microcontroller"""
        self.rx_error_count += 1
        self.last_error = timestamp
        if callable(self.evt_error_received):
            self.evt_error_received(self, timestamp, "RxError")

    def hw_reset(self, timestamp):
        """called when a error was detected by the microcontroller"""
        self.rx_error_count += 1
        self.last_error = timestamp
        if callable(self.evt_error_received):
            self.evt_error_received(self, timestamp, "Reset")

    def rx_data_missing(self, timestamp):
        """called when no data is received"""
        self.rx_error_count += 1
        self.last_error = timestamp
        if callable(self.evt_error_received):
            self.evt_error_received(self, timestamp, "DataMissing")

    def serialreader_run(self):
        """receiver thread"""
        while True:
            if not self.readerrunning:
                return

            line = self.ser.readline().replace("\r", "").replace("\n", "")
            timestamp = time.time()

            if line.startswith("Logdata:"):
                data = bytearray.fromhex(line[8:])
                self.rx_logdata(data, timestamp)
            elif line.startswith("Display:"):
                data = bytearray.fromhex(line[8:])
                self.rx_displaydata(data, timestamp)
            elif line.startswith("Built on:"):
                self.hw_reset(timestamp)
            elif line == "rxErr":
                self.rx_error(timestamp)
            elif line == "":
                # nothing received, this is usually when the serial port was closed
                self.rx_data_missing(timestamp)
            else:
                print("received odd data: \"%s\"" % line)

    def communication_alive(self, timeout=10):
        """returns true if the communication is alive and false if not"""
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
