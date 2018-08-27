import time
import os
import errno

class DataLogger(object):
    fileprefix = ''
    filesuffix = ''
    filename = ''
    filehandle = None
    formatstr = '{:.3f}\t{}\t{}\n'

    def __init__(self, fileprefix, filesuffix):
        self.fileprefix = fileprefix
        self.filesuffix = filesuffix
        self.openfile()

    def __del__(self):
        self.close()


    def openfile(self):
        oldfilename = self.filename
        self.filename = self.fileprefix + time.strftime('%Y-%m-%d') + self.filesuffix

        # open the file only if it has a different file name
        if oldfilename != self.filename:
            if self.filehandle != None:
                self.write(None, 'i', 'Log closed')
                self.filehandle.close()

            # create directory if it doesn't exist
            if not os.path.exists(os.path.dirname(self.filename)):
                try:
                    os.makedirs(os.path.dirname(self.filename))
                except OSError as ex:
                    if ex.errno != errno.EEXIST:
                        raise

            # open/create the file for append
            self.filehandle = open(self.filename, 'a')
            self.write(None, 'i', 'Log opened')

    def write(self, logtime, logtype, data):
        self.openfile()
        if logtime == None:
            logtime = time.time()
        self.filehandle.write(self.formatstr.format(logtime, logtype, data))

    def flush(self):
        self.filehandle.flush()

    def close(self):
        self.write(None, 'i', 'Log closed')
        self.filehandle.flush()
        self.filehandle.close()

