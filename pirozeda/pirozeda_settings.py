# -*- coding: utf-8 -*-
import platform
from prozeda_systems import prozeda_systems

settings = {
    'serialport' : {
        'port': '/dev/serial0',
        'baudrate' : 115200,
    },
    'system' : prozeda_systems['SungoSXL_1221_de_TBC'],
    'server_address' : ('', 19000),
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
    }
}

# overrides for test environment
if platform.system() == 'Windows':
    settings['serialport']['port'] = 'COM4'
    #settings['serialport']['port'] = 'COM30'
    settings['fslog']['dir'] = 'logs/'
    settings['trace']['dir'] = 'trace/'
    settings['ramlog']['interval'] = 10

# do some final calculations
settings['ramlog']['length'] = 24*60*60 / settings['ramlog']['interval']
settings['fslog']['length'] = 24*60*60 / settings['fslog']['interval']