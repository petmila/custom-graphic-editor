import numpy as np
import scripts.exceptions as ex
import zlib


def save_data(filename: str, format: str, data):
    if format == "P6\n":
        file = open(f"{filename}.ppm", "wb")
        save_p6_file(file, format, data)
        file.close()
    elif format == "P5\n":
        file = open(f"{filename}.ppm", "wb")
        save_p5_file(file, format, data)
        file.close()
    elif format == "PNG":
        file = open(f"{filename}.png", "wb")
        save_png_file(file, format, data, 0)
        file.close()
    else:
        raise ex.InvalidFileFormatException("Invalid file format")


def save_p6_file(file, format_, data):
    file.write(bytes(format_, 'utf-8'))
    width = np.shape(data)[1]
    height = np.shape(data)[0]
    file.write(bytes(f"{width} {height}" + '\n', 'utf-8'))
    file.write(bytes(f"{255}" + '\n', 'utf-8'))
    for i in range(height):
        for j in range(width):
            for color_number in range(3):
                file.write(data[i, j, color_number])


def save_p5_file(file, format, data):
    file.write(bytes(format, 'utf-8'))
    width = np.shape(data)[1]
    height = np.shape(data)[0]
    file.write(bytes(f"{width} {height}" + '\n', 'utf-8'))
    file.write(bytes(f"{255}" + '\n', 'utf-8'))
    for i in range(height):
        for j in range(width):
            file.write(data[i, j, 0])


def save_png_file(file, format, data, gamma):
    png_header = [np.uint8(137), np.uint8(80), np.uint8(78), np.uint8(71), np.uint8(13), np.uint8(10), np.uint8(26),
                  np.uint8(10)]
    for i in png_header:
        file.write(i)
    write_length_and_name(file, 13, "IHDR")
    b_data = b''
    width = np.shape(data)[1]
    b_data = b_data + width.to_bytes(4, 'big')
    height = np.shape(data)[0]
    b_data = b_data + height.to_bytes(4, 'big')
    bit_depth = 8
    b_data = b_data + bit_depth.to_bytes(1, 'big')
    color_type = 2
    b_data = b_data + color_type.to_bytes(1, 'big')
    b_data = write_num(b_data, 1, 0, 3)
    crc = zlib.crc32(b_data)
    b_data = b_data + crc.to_bytes(4, 'big')
    file.write(b_data)
    # IDAT
    b_data = b''
    for i in range(height):
        b_data = b_data + b'0'
        b_data = b_data + data[i].tobytes()

    compress_data = zlib.compress(b_data)
    print(len(b_data), len(compress_data))
    length = len(compress_data)
    write_length_and_name(file, length, "IDAT")
    crc = zlib.crc32(compress_data)
    b_data = compress_data + crc.to_bytes(4, 'big')
    file.write(b_data)
    # gAMA
    b_data = b''
    b_data = b_data + gamma.to_bytes(4, 'big')
    length = 4
    write_length_and_name(file, length, "gAMA")
    crc = zlib.crc32(b_data)
    b_data = b_data + crc.to_bytes(4, 'big')
    file.write(b_data)
    # IEND
    write_length_and_name(file, 0, "IEND")
    # array_to_string = ''.join([''.join(['0', [''.join([data[i][j][k] for k in range(3)]) for j in range(width)][0]]
    #                                    ) for i in range(height)])

    # print(b_data)


def write_length_and_name(file, length, name):
    file.write(length.to_bytes(4, 'big'))
    file.write(str.encode(name))


def write_num(b_data, length, num, repeat):
    for i in range(repeat):
        b_data = b_data + num.to_bytes(length, 'big')
    return b_data
