import zlib
import scripts.exceptions as ex
import numpy as np


class PNGParser:
    def __init__(self):
        self.color_type = ""
        self.gamma = 0
        self.height = 0
        self.width = 0
        self.bit_depth = ""
        self.palette = np.zeros((0, 0))
        self.colormap = np.zeros((0, 0, 0))
        self.zip_data = b''
        self.filter_types = np.zeros(0)
        self.end = 0
        self.i = 0
        self.j = 0

    def parse(self, file):
        buf = b'0'
        fragment_name = [0] * 4
        while fragment_name[0] != b'' or self.end == 0:
            length = self.get_integer(file, 4)
            for i in range(0, 4):
                fragment_name[i] = file.read(1)
            self.resolve_fragment_name(file, fragment_name, length)
        convert_data = zlib.decompress(self.zip_data)
        print(len(self.zip_data), len(convert_data))
        if self.color_type == 0:
            k = 0
            for i in range(self.height):
                self.filter_types[i] = convert_data[k]
                k += 1
                for j in range(self.width):
                    self.colormap[i, j] = convert_data[k]
                    k += 1
            self.filter_fun()
            return self.height, self.width, self.colormap, "PNG", float(self.gamma/100000)
        elif self.color_type == 2:
            k = 0
            for i in range(self.height):
                self.filter_types[i] = convert_data[k]
                k += 1
                for j in range(self.width):
                    for color_number in range(3):
                        self.colormap[i, j, color_number] = convert_data[k]
                        k += 1
            self.filter_fun()
            return self.height, self.width, self.colormap, "PNG", float(self.gamma/100000)
        elif self.color_type == 3:
            k = 0
            for i in range(self.height):
                self.filter_types[i] = convert_data[k]
                k += 1
                for j in range(self.width):
                    self.colormap[i, j] = self.palette[convert_data[k]]
                    k += 1
            return self.height, self.width, self.colormap, "PNG", float(self.gamma/100000)

    def resolve_fragment_name(self, file, fragment_name, length):
        if self.check_equal(fragment_name, "IHDR"):
            print("IHDR")
            self.width = self.get_integer(file, 4)
            self.height = self.get_integer(file, 4)
            self.bit_depth = self.get_integer(file, 1)
            self.color_type = self.get_integer(file, 1)
            self.colormap = np.empty((self.height, self.width, 3), dtype=np.uint8)
            self.filter_types = np.empty(self.height)
            print(file.read(7))
        elif self.check_equal(fragment_name, "IDAT"):
            print("IDAT")
            buf = file.read(length)
            self.zip_data = self.zip_data + buf
            # convert_data = zlib.decompress(buf)
            # print(len(buf), len(convert_data))
            file.read(4)

        elif self.check_equal(fragment_name, "IEND"):
            print("IEND")
            self.end = 1
        elif self.check_equal(fragment_name, "PLTE"):
            if length % 3 != 0:
                raise ex.InvalidFileStructureException("Incorrect")
            self.palette = np.empty((length, 3), dtype=np.uint8)
            for i in range(0, int(length/3)):
                for j in range(3):
                    self.palette[i, j] = self.get_integer(file, 1)
            file.read(4)
        elif self.check_equal(fragment_name, "gAMA"):
            self.gamma = self.get_integer(file, 4)
            file.read(4)
        else:
            if int.from_bytes(fragment_name[0], byteorder='big') & (1 << 5) == 0:
                pass
                # raise ex.InvalidFileStructureException("Unknown important fragment")
            file.read(length)
            file.read(4)

    def get_integer(self, file, size):
        data = file.read(size)
        return int.from_bytes(data, byteorder='big')

    def check_equal(self, fragment_name, name):
        for i in range(4):
            if fragment_name[i] != name[i].encode('ascii'):
                return 0
        return 1

    def filter_fun(self):
        last_string = np.zeros((self.width, 3), dtype=np.uint8)

        for i in range(self.height):
            line_buf = self.colormap[i]
            if self.filter_types[i] == 0:
                pass
            elif self.filter_types[i] == 1:
                last_px = np.zeros(3)
                for j in range(self.width):
                    buf = self.colormap[i][j]
                    for color_number in range(3):
                        self.colormap[i][j][color_number] = (int(self.colormap[i][j][color_number]) + int(
                            last_px[color_number])) % 256
                    last_px = buf
            elif self.filter_types[i] == 2:
                for j in range(self.width):
                    for color_number in range(3):
                        self.colormap[i][j][color_number] = (int(self.colormap[i][j][color_number]) + int(
                            last_string[j][color_number])) % 256

            elif self.filter_types[i] == 3:
                last_px = np.zeros(3)
                for j in range(self.width):
                    for color_number in range(3):
                        avg = int((int(last_px[color_number]) + int(last_string[j][color_number])) / 2)
                        self.colormap[i][j][color_number] = (int(self.colormap[i][j][color_number]) + avg) % 256
                    last_px = self.colormap[i][j]


            elif self.filter_types[i] == 4:
                last_px = np.zeros(3)
                for j in range(self.width):
                    left, up, left_up = 0, 0, 0
                    # buf = self.colormap[i][j].copy()
                    for color_number in range(3):
                        left = last_px[color_number]
                        up = last_string[j][color_number]
                        if j != 0:
                            left_up = last_string[j - 1][color_number]
                        num = self.paeth_predictor(left, up, left_up)
                        # print(i, j, " ", num, left, up, left_up, "__", self.colormap[i][j][color_number])
                        self.colormap[i][j][color_number] = (int(self.colormap[i][j][color_number]) + num) % 256
                    last_px = self.colormap[i][j]

            last_string = line_buf
            # print("FFFFF1", last_string[0:10],"FFFFF2", self.colormap[0:10])

    def paeth_predictor(self, a: int, b: int, c: int):
        p = (int(a) + int(b) - int(c))
        pa = abs(p - a)
        pb = abs(p - b)
        pc = abs(p - c)
        if pa <= pb and pa <= pc:
            return a
        elif pb <= pc:
            return b
        else:
            return c