# -*- coding: utf-8 -*-

class ProzedaDisplaydata(object):
    """display data periodically sent by the controller"""

    def __init__(self, data, timestamp=None):
        self.data = data
        self.parsed = False
        self.timestamp = timestamp
        self.menu_info = None
        self.menu_settings = None
        self.menu_manual = None
        self.menu_specialfunc = None
        self.text = ['', '']
        self.status_pump = None
        self.status_outputs = []
        self.status_error = None
        self.status_confirmok = None

    @staticmethod
    def convert_displaytext(rawtext):
        """replace the character codes of the display to the utf8 equivalent chars"""
        text = ''.join(map(chr, rawtext))
        # the following replacements to the display contents are known:
        # 0x01: ° - degree
        # 0x05: ↙ - south west arrow
        # 0x06: ↗ - north east arrow
        # 0x07: ▲ - filled up-pointing triangle
        # 0x81: ü - german umlaut for small 'u'
        # 0x94: ö - german umlaut for small 'o'
        # 0xC6: ↓ - downwards arrow
        # 0xC7: → - rightwards arrow
        # 0xE0: ↓ - downwards arrow
        # 0xDE: ↑ - upwards arrow
        # 0xF5: ▼ - filled down-pointing triangle (not sure!)
        # 0xFA: [ - left bracket
        # 0xFC: ] - right bracket
        # 0x??: ä - german umlaut for small 'a'
        mapping = [
            ('\x01', '°'), ('\x05', '↙'), ('\x06', '↗'),
            ('\x07', '▲'), ('\x81', 'ü'), ('\x94', 'ö'),
            ('\xC6', '↓'), ('\xC7', '→'), ('\xF5', '▼'),
            ('\xE0', '↓'), ('\xDD', '\\xDD'), ('\xDE', '↑'),
            ('\xFA', '['), ('\xFC', ']'),
        ]
        # TODO: replace all non-readable characters as they seem to confuse pyjsonrpc
        for src, dst in mapping:
            text = text.replace(src, dst)
        return text

    def parse(self, force=False):
        """parse the data transferred to the external display"""
        if not force and self.parsed:
            # only parse if forced or not already parsed
            return True
        if len(self.data) != 64:
            return False

        self.text = [
            self.convert_displaytext(self.data[0:14]),  # 0x00 .. 0x0E
            self.convert_displaytext(self.data[14:24]), # 0x0E .. 0x17
            self.convert_displaytext(self.data[24:38]), # 0x18 .. 0x25
        ]
        self.menu_info = (self.data[0x26] & 0x01) != 0
        self.menu_settings = (self.data[0x2A] & 0x01) != 0
        self.menu_manual = (self.data[0x2E] & 0x10) != 0
        self.menu_specialfunc = (self.data[0x32] & 0x10) != 0

        # pump status data: 0bxxxabcxx
        # a: 'up', b: center, c: 'down'
        # let's map it to 0: symbol off, 1: down, 2: up
        tmp = self.data[0x28] & 0x1C
        if tmp == 0x00:
            self.status_pump = 0
        elif tmp == 0x0C:
            self.status_pump = 1
        elif tmp == 0x18:
            self.status_pump = 2
        else:
            self.status_pump = None

        # frame: if (self.data[0x2B] & 0x01) != 0 self.status_outputs.append('[]');
        # channel 0 (first entry below) is the frame, channels map the according number
        # channel 1 = index 1
        if (self.data[0x2B] & 0x01) != 0:
            self.status_outputs.append(0)
        if (self.data[0x2C] & 0x04) != 0:
            self.status_outputs.append(1)
        if (self.data[0x2C] & 0x02) != 0:
            self.status_outputs.append(2)
        if (self.data[0x2D] & 0x08) != 0:
            self.status_outputs.append(3)
        if (self.data[0x2D] & 0x04) != 0:
            self.status_outputs.append(4)
        if (self.data[0x2C] & 0x10) != 0:
            self.status_outputs.append(5)
        if (self.data[0x2C] & 0x08) != 0:
            self.status_outputs.append(6)
        if (self.data[0x2D] & 0x02) != 0:
            self.status_outputs.append(7)
        # couldn't enable channel 8 on test device

        self.status_error = (self.data[0x2F] & 0x01) != 0
        self.status_confirmok = (self.data[0x33] & 0x10) != 0

        self.parsed = True

    def to_object(self):
        """converts the data from this object to an object.
        Yep, I'm too dumb for proper serialisation
        """
        return {
            "timestamp" : self.timestamp, "menu_info" : self.menu_info,
            "menu_settings" : self.menu_settings, "menu_manual" : self.menu_manual,
            "menu_specialfunc" : self.menu_specialfunc, "text" : self.text,
            "status_pump" : self.status_pump, "status_outputs" : self.status_outputs,
            "status_error" : self.status_error, "status_confirmok" : self.status_confirmok,
        }

if __name__ == '__main__':
    print('you\'re not supposed to run this file')
