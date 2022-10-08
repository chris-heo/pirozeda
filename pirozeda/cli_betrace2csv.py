"""converts backend-traces to CSV"""

from prozeda import ProzedaReader, ProzedaLogdata, ProzedaHistory
from pirozeda_settings import settings

ProzedaLogdata.set_config(settings['system'])

def convert(filename, logoutput):
    
    log = open(logoutput, 'w')
    separator = '\t'
    log.write('sep=' + separator + '\n')
    colheads = ProzedaLogdata.get_column_header(None, True)
    tmp = []
    for colhead in colheads:
        tmp.append(colhead[2])
    log.write(separator.join(tmp) + '\n')


    with open(filename) as f:
        for line in f:
            parts = line.split('\t')

            if len(parts) != 3 or parts[1] != 'd':
                continue
            timestamp = float(parts[0])

            line = parts[2]
            if line.startswith("Logdata:"):
                try:
                    data = bytearray.fromhex(line[8:].strip())
                    ld = ProzedaLogdata(data, timestamp)
                    log.write(separator.join(str(x) for x in ld.get_columns(None, True)) + '\n')
                except:
                    log.write(separator.join(str(x) for x in [timestamp, 'data could not be converted']) + '\n')

            #elif line.startswith("Display:"):
            #    data = bytearray.fromhex(line[8:])
            #    self.rx_displaydata(data, timestamp)
    log.close()

files = [
    "./traces/prozeda_YYYY-MM-DD_hh.mm.ss",
]
for x in files:
    convert(x + '.txt', x + '_log.csv')