# -*- coding: utf-8 -*-
# öäüÖÄÜß, maybe this triggers vscode to open the file as unicode
from __future__ import print_function

class ProzedaLogColumn(object):
    """column for decoding data entries from a Prozeda controller"""
    def __init__(self, columntype, shortname, name, ignore=False, arg=None):
        """for columntype see pirozeda_settings.py"""
        self.columntype = columntype
        self.shortname = shortname
        self.ignore = ignore
        self.name = name
        self.arg = arg

    def parse(self, pos, data):
        """parses the date according to the column's configuration"""
        coltype = self.columntype
        if coltype in [0x01]:
            # Temperature
            val, pos = self.parse_int16(pos, data)
            return (float(val) / 10, pos)
        elif coltype in [0x00, 0x07, 0x08, 0x09, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x13]:
            return self.parse_uint16(pos, data)
        elif coltype in [0x1B]:
            # Tapping
            val, pos = self.parse_uint16(pos, data)
            return (float(val) / 10, pos)
        elif coltype in [0x02, 0x0A]:
            return self.parse_uint8(pos, data)
        elif coltype == 0xFF:
            return self.parse_uintn(pos, data, self.arg)

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
    def parse_uintn(pos, data, cnt):
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

    def to_list(self):
        """converts this object to a list"""
        return [self.columntype, self.shortname,
                self.name, self.ignore, self.arg]

class ProzedaLogdata(object):
    """Prozeda log data periodically sent by the controller"""

    columnconfig = []

    @staticmethod
    def set_config(config):
        ProzedaLogdata.columnconfig = []
        for column in config:
            ignore = False
            arg = None
            if len(column) > 3:
                ignore = column[3]
            if len(column) > 4:
                arg = column[4]
            obj = ProzedaLogColumn(column[0], column[1], column[2], ignore, arg)
            ProzedaLogdata.columnconfig.append(obj)

    def __init__(self, data, timestamp=None):
        self.data = data
        self.timestamp = timestamp
        self.columns = []
        self.parsed = False

    @staticmethod
    def get_column_indices(shortname):
        """returns the column indeces that matches the given shortname
        (simple wildcard supported)
        """
        result = []
        index = 0
        for item in ProzedaLogdata.columnconfig:
            if item.shortname == shortname:
                result.append(index)
            elif shortname.endswith('*') and item.shortname[:len(shortname)-1] == shortname[:-1]:
                result.append(index)
            index += 1
        return result

    @staticmethod
    def get_column_header(selected_columns=None, include_timestamp=False):
        """returns the column headers for the data represented by this class"""
        result = []

        for column in ProzedaLogdata.columnconfig:
            result.append(column.to_list())

        if selected_columns:
            result2 = []
            for index in selected_columns:
                result2.append(result[index])
            result = result2

        if include_timestamp:
            result.insert(0, [0xFE, 't', 'timestamp', True])
        return result

    def parse(self, force=False, offset=2):
        """maps the received data to the values"""
        if len(ProzedaLogdata.columnconfig) == 0:
            raise Exception("config not set, use static method set_config before instantiating objects")
        if not force and self.parsed:
            # only parse if forced or not already parsed
            return True
        if len(self.data) != 68:
            return False
        # ignore SOF
        pos = offset
        self.columns = []
        for column in ProzedaLogdata.columnconfig:
            val, pos = column.parse(pos, self.data)
            self.columns.append(val)

        self.parsed = True
        return True

    def get_column(self, column_index):
        self.parse()
        return self.columns[column_index]

    def get_columns(self, selected_columns=None, include_timestamp=False):
        """returns the column data for this object"""
        self.parse()
        result = list(self.columns)

        if selected_columns:
            result2 = []
            for index in selected_columns:
                result2.append(result[index])
            result = result2

        if include_timestamp:
            result.insert(0, self.timestamp)
        return result

if __name__ == '__main__':
    print('you\'re not supposed to run this file')
