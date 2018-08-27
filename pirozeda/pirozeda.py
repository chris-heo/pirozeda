"""This file is the main interface of the prozeda interface
it reads the data from the hardware, stores the data periodically
to the file system and provides a simple interface"""

from __future__ import print_function
import time
import datetime
import collections
import base64
import threading
import pyjsonrpc
import prozedareader
import datalogger

class JsonrpcRequestHandler(pyjsonrpc.HttpRequestHandler):
    """this is the json request handler, the interface to the webserver"""

    cachelog = None

    @pyjsonrpc.rpcmethod
    def info(self):
        return "Version 0.1"

    @pyjsonrpc.rpcmethod
    def get_lastday(self):
        retval = []
        for item in self.cachelog:
            retval.append(item.to_object())
        return retval

    @pyjsonrpc.rpcmethod
    def get_lastday_status(self):
        return (len(self.cachelog), self.cachelog.maxlen)

    @pyjsonrpc.rpcmethod
    def flushfile(self):
        # TODO: implement
        return True

    @staticmethod
    def startserver():
        http_server = pyjsonrpc.ThreadingHttpServer(
            server_address=('', 19000),
            RequestHandlerClass=JsonrpcRequestHandler
        )

        server_thread = threading.Thread(target=http_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

def main():
    """Main function of the program"""

    # before we run the actual program, let's wait until we got a "valid" system time
    # when the system starts, we live in 1970, this is not quite useful when writing
    # logs. Therefore, it's better to wait until the system synced the time

    while datetime.datetime.now().year < 2000:
        print("system time invalid, waiting for NTP update...")
        time.sleep(10)

    fslogperiod = 5 * 60 # period in seconds for the log to be written to the file system

    cachelogperiod = 60 # period in seconds for the log held in RAM
    cachelogcount = (24*60*60) / cachelogperiod # number of records held in RAM. Let's take 24h

    cachelog = collections.deque(maxlen=cachelogcount)

    # please only modify from here if you know what to do
    fslogcnt = 0
    cachelogcnt = 0

    prozeda = prozedareader.ProzedaReader("COM3")
    log = datalogger.DataLogger("logs/prozeda_", ".txt")
    JsonrpcRequestHandler.startserver()

    JsonrpcRequestHandler.cachelog = cachelog

    print("ready")
    try:
        while True:

            time.sleep(1)
            if not prozeda.communication_alive():
                print("no data received")

            fslogcnt += 1
            if fslogcnt == fslogperiod:
                fslogcnt = 0
                logentry = prozeda.get_latest_logentry()
                if logentry is not None:
                    log.write(logentry.timestamp, "d", base64.b64encode(logentry.data))
                    # log.flush() # only enable flush for development
                    # (log will be written to file system for every line)
                else:
                    log.write(time.time(), "w", "no data")

            cachelogcnt += 1
            if cachelogcnt == cachelogperiod:
                cachelogcnt = 0
                cachelog.append(prozeda.get_latest_logentry())

    except KeyboardInterrupt:
        print("quitting...")
        prozeda.stop()
        exit()

if __name__ == "__main__":
    main()
