from prozeda import ProzedaReader, ProzedaLogdata, ProzedaHistory
from pirozeda_settings import settings
import base64

ProzedaLogdata.set_config(settings['system'])

def convert(filename, log):
    with open(filename) as f:
        for line in f:
            parts = line.split('\t')

            if len(parts) != 3 or parts[1] != 'd':
                print('meep ' + line)
                continue
            timestamp = float(parts[0])

            if parts[1] == 'd':
                try:
                    hexdata = base64.b64decode(parts[2])
                    data = [ord(x) for x in hexdata]
                    ld = ProzedaLogdata(data, timestamp)
                    cols = ld.get_columns(None, True)
                    cols.append(''.join('{:02X}'.format(c) for c in data))
                    log.write(separator.join(str(x) for x in cols).replace('.', ',') + '\n')
                except:
                    log.write(separator.join(str(x) for x in [timestamp, 'data could not be converted']) + '\n')

files = [
    './logs/prozeda_YYYY-MM-DD',
]


log = open('./logs/all_log.csv', 'w')
separator = '\t'
log.write('sep=' + separator + '\n')
colheads = ProzedaLogdata.get_column_header(None, True)
tmp = []
for colhead in colheads:
    tmp.append(colhead[2])
log.write(separator.join(tmp) + '\n')

for x in files:
    convert(x + '.txt', log)

log.close()