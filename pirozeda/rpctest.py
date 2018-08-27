"""This file is the main interface of the prozeda interface
it reads the data from the hardware, stores the data periodically
to the file system and provides a simple interface"""

from __future__ import print_function
import time
import threading
import pyjsonrpc

class JsonrpcRequestHandler(pyjsonrpc.HttpRequestHandler):
    """this is the json request handler, the interface to the webserver"""

    cachelog = None

    @pyjsonrpc.rpcmethod
    def info(self):
        return "Version 0.1"

    @pyjsonrpc.rpcmethod
    def get_data(self):
        return "meh"

    @staticmethod
    def startserver():
        http_server = pyjsonrpc.ThreadingHttpServer(
            server_address=('', 19001),
            RequestHandlerClass=JsonrpcRequestHandler
        )

        server_thread = threading.Thread(target=http_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

def main():
    JsonrpcRequestHandler.startserver()

    #JsonrpcRequestHandler.cachelog = cachelog

    print("ready")
    try:
        while True:
        
            time.sleep(0.1)
            

    except KeyboardInterrupt:
        print("quitting...")
        exit()


if __name__ == "__main__":
    main()
