# -*- coding: utf-8 -*-
from __future__ import print_function

from datetime import datetime, timedelta
import base64
import os
import time
from prozeda import ProzedaReader, ProzedaLogdata

class ProzedaHistory(object):

    config = None

    def __init__(self):
        pass

    @staticmethod
    def set_config(config):
        ProzedaHistory.config = config

    @staticmethod
    def readlogsrange(starttime, endtime, loadobject=False):
        if ProzedaHistory.config is None:
            raise Exception("config not set, use static method set_config before usage")
        result = []
        currentday = datetime.fromtimestamp(starttime)
        currentday = currentday.replace(hour=0, minute=0, second=0, microsecond=0)

        lastday = datetime.fromtimestamp(endtime)
        lastday = lastday.replace(hour=23, minute=59, second=59, microsecond=999999) 

        while True:
            dtstr = currentday.strftime('%Y-%m-%d')
            sfslog = ProzedaHistory.config['fslog']
            fname = sfslog['dir'] + sfslog['prefix'] + dtstr + sfslog['suffix']
            if os.path.isfile(fname):
                daydata = ProzedaHistory.readfilerange(fname, starttime, endtime, loadobject)
                #print('{} has {} entries'.format(fname, len(daydata)))
                result.extend(daydata)
            else:
                #print('{} does not exist'.format(fname))
                pass

            currentday += timedelta(days=1)
            if currentday > lastday:
                break
        return result

    @staticmethod
    def readfilerange(filename, starttime, endtime, loadobject = False):
        if ProzedaHistory.config is None:
            raise Exception("config not set, use static method set_config before usage")
        result = []
        with open(filename) as f:
            for line in f:
                parts = line.split('\t')

                if len(parts) != 3 or parts[1] != 'd':
                    continue
                timestamp = float(parts[0])

                if ((starttime is not None and timestamp < starttime) or
                        (endtime is not None and timestamp > endtime)):
                    continue

                if loadobject:
                    try:
                        data = base64.b64decode(parts[2])
                        data = [ord(x) for x in data]
                        result.append(ProzedaLogdata(data, timestamp))
                    except:
                        pass
                else:
                    result.append([timestamp, parts[2]])
        return result

    @staticmethod 
    def readlogsrange_as_list(starttime, endtime, selected_columns=None):
        result = []
        entries = ProzedaHistory.readlogsrange(starttime, endtime, True)
        for entry in entries:
            result.append(entry.get_columns(selected_columns, True))
        return result
    
    @staticmethod
    def readlogsrange_condensed(starttime, endtime, column_index):
        if ProzedaHistory.config is None:
            raise Exception("config not set, use static method set_config before usage")
        result = []
        entriesperday = 24*60*60 / ProzedaHistory.config['fslog']['interval']

        # due to either a bug in this software or misconfigured time zones on the machine,
        # it is required to start loading the date from the day before 

        currentday = datetime.fromtimestamp(starttime)
        currentday = currentday.replace(hour=0, minute=0, second=0, microsecond=0)

        lastday = datetime.fromtimestamp(endtime)
        lastday = lastday.replace(hour=23, minute=59, second=59, microsecond=999999) 

        # FIXME: some first values "between the days" are sometimes stored in the
        # "wrong" log file. This is not considered here and might also be troublesome
        # in other contexts. Best way would probably be to load (or store *sigh*) the
        # data in a (temporary) RDBMS...
        while True:
            dtstr = currentday.strftime('%Y-%m-%d')
            basetime = time.mktime(currentday.timetuple())
            sfslog = ProzedaHistory.config['fslog']
            fname = sfslog['dir'] + sfslog['prefix'] + dtstr + sfslog['suffix']
            if os.path.isfile(fname):
                daydata = ProzedaHistory.readfilerange(fname, starttime, endtime, True)

                result2 = [None] * entriesperday
                for entry in daydata:
                    index = int(round((entry.timestamp - basetime) / ProzedaHistory.config['fslog']['interval']))
                    if index >= 0 and index < entriesperday:
                        result2[index] = entry.get_column(column_index)
                    else:
                        # print("index ({}) is out of bounds for time offset {} on date {}".format(index, entry.timestamp - basetime, dtstr))
                        pass

                #print('{} has {} entries'.format(fname, len(daydata)))
                result.append({'date' : dtstr, 'basetime' : basetime, 'data' : result2 })
            else:
                #print('{} does not exist'.format(fname))
                pass

            currentday += timedelta(days=1)
            if currentday > lastday:
                break
        return result