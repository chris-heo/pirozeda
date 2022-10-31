# -*- coding: utf-8 -*-
import platform
import logging
from prozeda_systems import prozeda_systems

settings = {
    'serialport' : {
        'port': '/dev/serial0',
        'baudrate' : 115200,
    },
    'system' : prozeda_systems['SungoSXL_1221_HK_de'],
    'server_address' : ('localhost', 19000),
    'fslog' : {
        # interval in seconds for the log entries to be written to the filesystem
        'interval' : 5 * 60,
        # if started via cron, an absolute path is needed!
        'dir' : '/home/pi/pirozeda/logs/',
        'prefix' : 'prozeda_',
        'suffix' : '.txt',
    },
    'ramlog' : {
        # interval in seconds for the log held in RAM
        'interval' : 1 * 60,
        # see below
        'length' : 0,
    },
    'trace' : {
        'dir' : '/home/pi/pirozeda/traces/',
        'prefix' : 'prozeda_',
        'suffix' : '.txt',
    },
    'location' : {
        'lon' : 48.3, # North
        'lat' : 10.1, # East
    },
    'logging' : {
        'loggers': {
            'prozeda.prozedareader' : {
                'level' : logging.WARNING,
                'stdout' : True,
                'file' : True,
            },
            'prozeda.prozedahistory' : {
                'level' : logging.WARNING,
                'stdout' : True,
                'file' : False,
            },
            '__main__' : {
                'level' : logging.INFO,
                'stdout' : True,
                'file' : True,
            },
            'werkzeug' : {
                'level' : logging.ERROR,
                'stdout' : True,
                'file' : False,
            },
        }
        
    }
}

# overrides for test environment
if platform.system() == 'Windows':
    settings['serialport']['port'] = 'COM100'
    settings['fslog']['dir'] = 'logs/'
    settings['trace']['dir'] = 'trace/'
    settings['ramlog']['interval'] = 10

# do some final calculations
settings['ramlog']['length'] = int(24*60*60 / settings['ramlog']['interval'])
settings['fslog']['length'] = int(24*60*60 / settings['fslog']['interval'])
