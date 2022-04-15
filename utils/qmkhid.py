import hid
import os
from configparser import ConfigParser
from time import sleep
# data
# 0x01 : write string to a row
#   0x0X : X is the row rest of data is byte string to write to that row
# 0x02 :
#   0x<column>0x<row> : turn this pixel on.
# 0x03 : scroll commands
#   0x01: turn off scroll
#   0x02: turn on scroll
#   0x03: scroll right
#   0x04: scroll left
#   0x05: scroll speed
#     0x0X: where x is a value of 0 to 7
#   0x06: scroll area
#     0x<start>0x<stop> : start_line and end_line
# 0x04 : oled set brightness
#   0x0x : brightness value
# 0x05 : query device
#   0x01 : is_oled_on
#   0x02 : oled_on
#   0x03 : oled_off
# 0x08 : clearing a row
#   0x0X : where X is the row to clear
#   0x08 : clear all rows


class QMKDevice():
    def __init__(self, config_path):
        '''
        size of the screen is 128x64 pixels
        '''
        config = ConfigParser()
        config.read(config_path)

        def _to_int(string, base=16):
            return int(string, base)

        self.vid = _to_int(config['DEVICE']['VID'])
        self.pid = _to_int(config['DEVICE']['PID'])
        self.usage_page = _to_int(config['DEVICE']['USAGE_PAGE'])
        self.usage = _to_int(config['DEVICE']['USAGE'])
        self.raw_epsize = int(config['DEVICE']['RAW_EPSIZE'])
        self.cols = int(config['DEVICE']['COLUMNS'])
        self.rows = int(config['DEVICE']['ROWS'])

        self.report_id  = b'\x00'

        self.cmd_line   = b'\x01'

        self.cmd_pixel  = b'\x02'
        self.end_pixel  = b'\xff'

        self.cmd_scroll = b'\x03'
        self.scroll_off = b'\x01'
        self.scroll_on  = b'\x02'
        self.scroll_rgt = b'\x03'
        self.scroll_lft = b'\x04'
        self.scrl_speed = b'\x05'
        self.scrl_area  = b'\x06'

        self.cmd_bright = b'\x04'

        self.query      = b'\x05'
        self.oled_state = b'\x01'
        self.oled_on    = b'\x02'
        self.oled_off   = b'\x03'
        self.layer_state = b'\x04'
        self.brightness = b'\x05'
        self.max_chars  = b'\x06'
        self.max_lines  = b'\x07'

        self.layer      = b'\x06'

        self.exit       = b'\x07'

        self.cmd_erase  = b'\x08'

        devices = hid.enumerate()
        for device in devices:
            if (
                device["vendor_id"] == self.vid
                and device["product_id"] == self.pid
                and device["usage_page"] == self.usage_page
                and device["usage"] == self.usage
            ):
                self.device = hid.Device(path=device['path'])
                break



    def get_device_info(self):
        print("Device manufacturer: {}".format(self.device.manufacturer))
        print("Product: {}".format(self.device.product))

    def write(self, data):
        '''write to device'''
        data = self.tobytes(data)
        self.device.write(data)

    def read(self, timeout=None):
        '''reads from device, timeout in ms'''
        return self.device.read(size=self.raw_epsize, timeout=timeout)

    def read_layer(self, timeout=None):
        data = self.read(timeout=timeout)
        if len(data) != 0:
            data = int.from_bytes(data, 'little')
            return(data)
        else:
            return(None)

    def write_then_read(self, data):
        ''' used for getting info about the state of the device'''
        self.write(data)
        data = self.read()
        data = int.from_bytes(data, 'little')
        return data

    def close(self):
        '''always close your connection'''
        self.disconnect()
        self.device.close()

    def open(self):
        self.device.open()

    def pad(self, data):
        '''pad the data just before it's send'''
        data = self.report_id + data + b'\x00' * (self.raw_epsize - len(data))
        return data

    def tobyte(self, data):
        if type(data) is bytes:
            return data
        return (data).to_bytes(1, 'big')

    def tobytes(self, data):
        ''' the output here can be directly sent to self.write'''
        out = b''
        for num in data:
            if type(num) is str:
                num = str.encode(num)
            out += self.tobyte(num)
        out = self.pad(out)
        return out

    def clear_screen(self):
        '''clears the screen'''
        data = [self.cmd_erase, self.cmd_erase]
        self.write(data)

    def clear_line(self, line):
        '''clears a given line'''
        data = [self.cmd_erase, line]
        self.write(data)

    def send_pixels(self, pixels, value=1, offset=(0,0)):
        '''turns on one pixel'''
        data = [value]
        for pixel in pixels:
            data += list(sum(x) for x in zip(pixel, offset))
        data.insert(0, self.cmd_pixel)
        data.append(self.end_pixel)
        self.write(data)

    def prepare_pixel_buffer(self, pixels, value, offset=(0,0)):
        def chunk(pixel_list, size=int(self.raw_epsize/2)-2):
            for x in range(0, len(pixel_list), size):
                yield pixel_list[x:x+size]

        for pixel_group in chunk(pixels):
            self.send_pixels(pixels=pixel_group, value=value, offset=offset)

    def turn_pixels_on(self, pixels, offset):
        self.prepare_pixel_buffer(pixels=pixels, value=1, offset=offset)

    def turn_pixels_off(self, pixels, offset):
        self.prepare_pixel_buffer(pixels=pixels, value=0, offset=offset)


    def send_line(self, line, data):
        '''sends data to an oled line'''
        self.clear_line(line)
        data = [self.cmd_line, line, data]
        self.write(data)

    def send_raw(self, data):
        '''send raw data
        DO NOT DO THIS unless you know what you are sending'''
        self.device.write(data)

    def oled_scroll_off(self):
        '''stops oled scroll'''
        data = [self.cmd_scroll, self.scroll_off]
        self.write(data)

    def oled_scroll_right(self):
        '''scrolls oled buffer right'''
        data = [self.cmd_scroll, self.scroll_rgt]
        self.write(data)

    def oled_scroll_left(self):
        '''scrolls oled buffer left'''
        data = [self.cmd_scroll, self.scroll_lft]
        self.write(data)

    def oled_scroll_set_speed(self, speed):
        '''sets oled scroll speed'''
        data = [self.cmd_scroll, self.scrl_speed, speed]
        self.write(data)

    def oled_scroll_set_area(self, start, end):
        '''defines oled scroll area'''
        data = [self.cmd_scroll, self.scrl_area, start, end]
        self.write(data)

    def oled_set_brightness(self, brightness):
        '''sets the oled brightness'''
        if not 0 <= brightness <= 255:
            raise Exception("Invalid value: {}".format(brightness))
        data = [self.cmd_bright, brightness]
        self.write(data)

    def get_scroll_state(self):
        pass

    def vibrate(self, speed):
        pass

    def scroll_text(self, line, text, delay=.1, direction=True):
        '''
        scrolls any text
           inputs:
               line:  the line number to write text to
               text:  the text to scroll
               delay: the delay between each frame
               direction: True=left, False=right
        '''
        if len(text) < self.cols:
            text = text.ljust(self.cols + 1)
        else:
            text = text.ljust(len(text) + 5)
        def gen_data(text):
            data = list(range(self.cols))
            for index, letter in enumerate(text):
                try:
                    data[index] = letter
                except:
                    data = "".join(data)
                    return(data)
        data = gen_data(text)
        self.send_line(line, data)
        sleep(delay)
        for rotate in range(len(text)):
            text = list(text)
            if direction:
                text.append(text.pop(0))
            else:
                text.insert(0, text.pop())
            text = "".join(text)
            data = gen_data(text)
            self.send_line(line, data)
            sleep(delay)


    def get_oled_state(self):
        '''
        returns oled state
        True = on
        False = offset
        '''
        data = [self.query, self.oled_state]
        oled_state = self.write_then_read(data)
        if oled_state:
            return(True)
        else:
            return(False)

    def turn_oled_on(self):
        '''turns on oled and waits .5 seconds before doing anything'''
        data = [self.query, self.oled_on]
        self.write(data)
        sleep(.5)

    def turn_oled_off(self):
        ''' turns off oled and waits .2 seconds before doing anything'''
        data = [self.query, self.oled_off]
        self.write(data)
        sleep(.2)

    def get_layer(self):
        '''get highest layer
        you'll need to know what each layer'''
        data = [self.query, self.layer_state]
        layer = self.write_then_read(data)
        return layer

    def oled_get_brightness(self):
        '''get oled brightness'''
        data = [self.query, self.brightness]
        brightness = self.write_then_read(data)
        return brightness

    def oled_max_chars(self):
        '''get oled maximum number of characters that will fit on a line'''
        data = [self.query, self.max_chars]
        max_chars = self.write_then_read(data)
        return max_chars

    def oled_max_lines(self):
        '''get the maximum number of lines that will fit on the OLED'''
        data = [self.query, self.max_lines]
        max_lines = self.write_then_read(data)
        return max_lines

    def draw_picture(self, file_path, origin):
        '''draws a binary image onto the screen'''
        pixels = []
        offset = origin
        with open(file_path) as f:
            lines = f.readlines()

        for pixel_y, line in enumerate(lines):
            for pixel_x, bit in enumerate(line):
                if bit == '1':
                    pixels.append((pixel_x, pixel_y))
        self.turn_pixels_on(pixels=pixels, offset=offset)

    def set_layer(self, layer):
        data = [self.layer, layer]
        self.write(data)

    def disconnect(self):
        self.clear_screen()
        data = [self.exit]
        self.write(data)


def main():
    abspath = os.path.abspath(__file__)
    dirname = os.path.dirname(abspath)
    os.chdir(dirname)
    config_path = os.path.join(dirname, 'config.ini')

    try:
        me = QMKDevice(config_path)
        me.clear_screen()
        # me.send_line(line=0, data='Hello World!')
        # me.draw_picture(file_path='billybreathes.txt', origin=(0,0))
        # me.get_device_info()
        # print(me.read())
        # print(me.get_layer())
        # while True:
        #     result = me.read(timeout=10000)
        #     if result:
        #         print(result)
        app_layers = {"Spotify.exe": 1,
                      "Discord.exe": 2}




        # me.scroll_text(line=0, text="What direction will this scroll?", direction=True)
    finally:
        me.close()

if __name__ == '__main__':
    main()
