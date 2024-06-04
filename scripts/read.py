import re
import numpy as np
import scripts.exceptions as ex
from classes.png_parser import PNGParser


def reading(file_name):
    file = open(file_name, 'rb')
    # считывание первой строки, в которой указывается формат файла
    file_format = file.readline()
    if is_it_png(file, file_format):
        return png_parse(file, file_format)
    elif re.match(r"P5\n", bytes.decode(file_format)):
        return pnm5_parse(file, file_format)
    elif re.match(r"P6\n", bytes.decode(file_format)):
        return pnm6_parse(file, file_format)
    else:
        raise ex.InvalidFileStructureException("Invalid file type name")


def pnm6_parse(file, file_format):
    size = file.readline()  # строка с размерами файла
    width, height = map(int, size.split())
    third_string = file.readline()
    check_sign(width, height)
    if int(third_string) == 255:  # строка "255"
        data = np.empty((height, width, 3), dtype=np.uint8)
        for i in range(height):
            for j in range(width):
                for color_number in range(3):
                    data[i, j, color_number] = int.from_bytes(file.read(1), "big")
        file.close()
        return height, width, data, bytes.decode(file_format), 0
    else:
        raise ex.InvalidFileStructureException("Invalid file type name")


def pnm5_parse(file, file_format):
    size = file.readline()  # строка с размерами файла
    width, height = map(int, size.split())
    third_string = file.readline()
    check_sign(width, height)
    if int(third_string) == 255:  # строка "255"
        data = np.empty((height, width, 3), dtype=np.uint8)
        for i in range(height):
            for j in range(width):
                color = int.from_bytes(file.read(1), "big")
                for color_number in range(3):
                    data[i, j, color_number] = color
        file.close()
        return height, width, data, bytes.decode(file_format), 0
    else:
        raise ex.InvalidFileStructureException("Invalid file type name")


def check_sign(*args):  # Check is this unsigned int or not
    for num in args:
        if num <= 0:
            raise ex.InvalidFileStructureException("Invalid number")


def is_it_png(file, file_format):
    png_header = [137, 80, 78, 71, 13, 10, 26, 10]
    if len(file_format) != 6:
        return 0
    for i in range(6):
        if file_format[i] != png_header[i]:
            return 0
    file_format = file.readline()
    if len(file_format) != 2:
        return 0
    for i in range(2):
        if file_format[i] != png_header[i + 6]:
            return 0
    return 1

def png_parse(file, file_format):
    parser = PNGParser()
    return parser.parse(file)
