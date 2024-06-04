import numpy as np
import math


class Resampling:
    def __init__(self):
        self.curr_colormap = np.zeros(0)
        self.new_colormap = np.zeros(0)
        self.curr_height = 0
        self.curr_width = 0
        self.new_height = 0
        self.new_width = 0
        self.offset_x = 0
        self.offset_y = 0
        self.b_splain = 0
        self.c_splain = 0

    def resample(self, curr_colormap, new_height, new_width, algorithm, offset_x, offset_y, b_splain, c_splain):
        self.curr_colormap = curr_colormap.copy()
        self.curr_height = np.shape(self.curr_colormap)[0]
        self.curr_width = np.shape(self.curr_colormap)[1]
        self.new_height = new_height
        self.new_width = new_width
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.b_splain = b_splain
        self.c_splain = c_splain
        self.new_colormap = np.empty((self.curr_height, self.new_width, 3), dtype=float)
        if algorithm == 'Nearest_neighbor':
            self.nearest_neighbor()
        elif algorithm == 'Bilinear_interpolation':
            self.base_algorithm(self.in_bilinear_converter, self.bilenear_get_coordinate_x_zero)
        elif algorithm == 'Lanczos3':
            self.base_algorithm(self.in_lanczos3_converter, self.lanczos3_get_coordinate_x_zero)
        elif algorithm == 'BC-Splines':
            self.base_algorithm(self.in_bc_splain_converter, self.bc_splain_get_coordinate_x_zero)
        return self.new_height, self.new_width, self.new_colormap

    def nearest_neighbor(self):
        for i in range(self.curr_height):
            for j in range(self.new_width):
                position = self.get_position_in_curr_colormap(j, self.curr_width, self.new_width, self.offset_x)
                if position >= self.curr_width:
                    position = self.curr_width - 1
                if position < 0:
                    position = 0
                self.new_colormap[i, j] = self.curr_colormap[i, int(position)].copy()
        self.curr_colormap = self.new_colormap[0:self.curr_height, :, :].copy()
        self.new_colormap = np.empty((self.new_height, self.new_width, 3), dtype=float)
        for i in range(self.new_width):
            for j in range(self.new_height):
                position = self.get_position_in_curr_colormap(j, self.curr_height, self.new_height, self.offset_y)
                if position >= self.curr_width:
                    position = self.curr_width - 1
                if position < 0:
                    position = 0
                self.new_colormap[j, i] = self.curr_colormap[int(position), i].copy()
        return self.new_colormap

    def get_position_in_curr_colormap(self, px_number, curr_measurements, new_measurements, offset):
        return float(((px_number - offset) / new_measurements) * curr_measurements)

    def bilenear_get_coordinate_x_zero(self):
        return 1

    def lanczos3_get_coordinate_x_zero(self):
        return 3

    def bc_splain_get_coordinate_x_zero(self):
        return 2

    def in_bilinear_converter(self, value, old_min, old_max):
        old_range = old_max - old_min
        new_range = 2
        new_min = -1
        return self.bilinear_function((((value - old_min) * new_range) / old_range) + new_min)

    def bilinear_function(self, x):
        if x <= -1 or x >= 1:
            return 0
        if -1 < x < 0:
            return x + 1
        if 0 <= x < 1:
            return -x + 1

    def in_lanczos3_converter(self, value, old_min, old_max):
        old_range = old_max - old_min
        new_range = 2
        new_min = -1
        return self.lanczos3_function((((value - old_min) * new_range) / old_range) + new_min)

    def lanczos3_function(self, x):
        if x <= -3 or x >= 3:
            return 0
        if x == 0:
            return 1
        return (3 * math.sin(math.pi * x) * math.sin(math.pi * x / 3)) / (math.pi * math.pi * x * x)

    def in_bc_splain_converter(self, value, old_min, old_max):
        old_range = old_max - old_min
        new_range = 2
        new_min = -1
        return self.bc_splain_function((((value - old_min) * new_range) / old_range) + new_min)

    def bc_splain_function(self, x):
        if x <= -2 or x >= 2:
            return 0
        if math.fabs(x) < 1:
            return ((12 - 9 * self.b_splain - 6 * self.c_splain) * (math.fabs(x) ** 3) + (
                        -18 + 12 * self.b_splain + 6 * self.c_splain) * (math.fabs(x) ** 2) + (
                                6 - 2 * self.b_splain)) / 6
        if 1 <= math.fabs(x) < 2:
            return ((-self.b_splain - 6 * self.c_splain) * (math.fabs(x) ** 3) + (
                        6 * self.b_splain + 30 * self.c_splain) * (math.fabs(x) ** 2) + (
                                -12 * self.b_splain - 48 * self.c_splain) * math.fabs(x) + (
                                8 * self.b_splain + 24 * self.c_splain)) / 6

    def base_algorithm(self, alg_func, get_zero_coordinate):
        for i in range(self.curr_height):
            for j in range(self.new_width):
                if self.new_width >= self.curr_width:
                    position = self.get_position_in_curr_colormap(j, self.curr_width, self.new_width, self.offset_x)
                    if position >= self.curr_width:
                        position = self.curr_width - 1
                    if position < 0:
                        position = 0
                    left_value = position - get_zero_coordinate()
                    right_value = position + get_zero_coordinate()
                    result = 0
                    coefficient_sum = 0
                    for k in range(int(left_value), round(right_value) + 1):
                        coordinate = self.get_coordinate(k, self.curr_width)
                        if left_value <= coordinate <= right_value:
                            coefficient = alg_func(coordinate, left_value, right_value)
                            coefficient_sum += coefficient
                            result += coefficient * self.curr_colormap[i, coordinate]
                    if coefficient_sum != 0:
                        result = result / coefficient_sum
                    self.new_colormap[i, j] = result
                else:
                    left_value = self.get_position_in_curr_colormap(j - get_zero_coordinate(), self.curr_width,
                                                                    self.new_width, self.offset_x)
                    right_value = self.get_position_in_curr_colormap(j + get_zero_coordinate(), self.curr_width,
                                                                     self.new_width, self.offset_x)
                    result = 0
                    coefficient_sum = 0
                    for k in range(int(left_value), round(right_value) + 1):
                        coordinate = self.get_coordinate(k, self.curr_width)
                        if left_value <= coordinate <= right_value:
                            coefficient = alg_func(coordinate, left_value, right_value)
                            coefficient_sum += coefficient
                            result += coefficient * self.curr_colormap[i, coordinate]
                    if coefficient_sum != 0:
                        result = result / coefficient_sum
                    self.new_colormap[i, j] = result

        self.curr_colormap = self.new_colormap.copy()
        self.new_colormap = np.empty((self.new_height, self.new_width, 3), dtype=float)
        for i in range(self.new_width):
            for j in range(self.new_height):
                if self.new_height >= self.curr_height:
                    position = self.get_position_in_curr_colormap(j, self.curr_height, self.new_height,
                                                                  self.offset_y)
                    if position >= self.new_height:
                        position = self.new_height - 1
                    if position < 0:
                        position = 0
                    left_value = position - get_zero_coordinate()
                    right_value = position + get_zero_coordinate()
                    result = 0

                    coefficient_sum = 0
                    for k in range(int(left_value), round(right_value) + 1):
                        coordinate = self.get_coordinate(k, self.curr_height)
                        if left_value <= coordinate <= right_value:
                            coefficient = alg_func(coordinate, left_value, right_value)
                            result += coefficient * self.curr_colormap[coordinate, i]
                            coefficient_sum += coefficient
                    if coefficient_sum != 0:
                        result = result / coefficient_sum
                    self.new_colormap[j, i] = result
                else:
                    left_value = self.get_position_in_curr_colormap(j - get_zero_coordinate(), self.curr_height,
                                                                    self.new_height,
                                                                    self.offset_y)
                    right_value = self.get_position_in_curr_colormap(j + get_zero_coordinate(), self.curr_height,
                                                                     self.new_height,
                                                                     self.offset_y)
                    result = 0
                    coefficient_sum = 0
                    for k in range(int(left_value), round(right_value) + 1):
                        coordinate = self.get_coordinate(k, self.curr_height)
                        if left_value <= coordinate <= right_value:
                            coefficient = alg_func(coordinate, left_value, right_value)
                            coefficient_sum += coefficient
                            result += coefficient * self.curr_colormap[coordinate, i]
                    if coefficient_sum != 0:
                        result = result / coefficient_sum
                    self.new_colormap[j, i] = result
        return self.new_colormap

    def get_coordinate(self, k, measurements):
        if k < 0:
            return -k
        if k >= measurements:
            return 2*measurements - k - 1
        return k
