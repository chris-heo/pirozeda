import time
import os
import errno

class DataLogger(object):

    def __init__(self, fileprefix, filesuffix, timeformat='%Y-%m-%d', filenamestatic=False):
        self.filehandle = None
        self.formatstr = '{:.3f}\t{}\t{}\n'

        self.fileprefix = fileprefix
        self.filesuffix = filesuffix
        self.timeformat = timeformat
        self.filename = None
        self.filenamestatic = filenamestatic
        self.openfile()

    def __del__(self):
        self.close()

    def get_filesize(self):
        #return os.fstat(self.filehandle.fileno()).st_size
        return self.filehandle.tell()

    def openfile(self):
        oldfilename = self.filename
        #FIXME
        if self.filenamestatic == False or self.filename is None:
            self.filename = self.fileprefix + time.strftime(self.timeformat) + self.filesuffix

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
        if self.filehandle != None:
            self.filehandle.flush()
            return True
        return False

    def close(self):
        if self.filehandle is None:
            return
        self.write(None, 'i', 'Log closed')
        self.filehandle.flush()
        self.filehandle.close()
        self.filehandle = None

