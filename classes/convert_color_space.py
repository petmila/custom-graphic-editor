import numpy as np
import enum


class ColorSpace(enum.Enum):
    RGB = 0
    HSL = 1
    HSV = 2
    CMY = 3
    YCbCr601 = 4
    YCbCr709 = 5
    YCoCg = 6


class ColorSpaceConverter:
    def from_rgb(self, colormap, to_color_space):
        new_colormap = np.copy(colormap)
        if to_color_space == ColorSpace.HSL:
            new_colormap = self.convert_function(new_colormap.copy(), self.toHSL)
        elif to_color_space == ColorSpace.HSV:
            new_colormap = self.convert_function(new_colormap.copy(), self.toHSV)
        elif to_color_space == ColorSpace.CMY:
            new_colormap = self.convert_function(new_colormap.copy(), self.toCMY)
        elif to_color_space == ColorSpace.YCbCr601:
            new_colormap = self.convert_function(new_colormap.copy(), self.toYCbCr601)
        elif to_color_space == ColorSpace.YCbCr709:
            new_colormap = self.convert_function(new_colormap.copy(), self.toYCbCr709)
        elif to_color_space == ColorSpace.YCoCg:
            new_colormap = self.convert_function(new_colormap.copy(), self.toYCoCg)

        return new_colormap

    def to_rgb(self, colormap, from_color_space):
        new_colormap = np.copy(colormap)
        if from_color_space == ColorSpace.HSL:
            new_colormap = self.convert_function(new_colormap.copy(), self.fromHSL)
        elif from_color_space == ColorSpace.HSV:
            new_colormap = self.convert_function(new_colormap.copy(), self.fromHSV)
        elif from_color_space == ColorSpace.CMY:
            new_colormap = self.convert_function(new_colormap.copy(), self.fromCMY)
        elif from_color_space == ColorSpace.YCbCr601:
            new_colormap = self.convert_function(new_colormap.copy(), self.fromYCbCr601)
        elif from_color_space == ColorSpace.YCbCr709:
            new_colormap = self.convert_function(new_colormap.copy(), self.fromYCbCr709)
        elif from_color_space == ColorSpace.YCoCg:
            new_colormap = self.convert_function(new_colormap.copy(), self.fromYCoCg)

        return new_colormap

    def convert_function(self, colormap, function):
        for i in range(np.shape(colormap)[0]):
            for j in range(np.shape(colormap)[1]):
                colormap[i][j][0], colormap[i][j][1], colormap[i][j][2] = \
                    function(colormap[i][j][0], colormap[i][j][1], colormap[i][j][2])
        return colormap

    def toHSL(self, r: float, g: float, b: float):
        max_color = max(r, g, b)
        min_color = min(r, g, b)
        chroma = max_color - min_color

        # Hue
        if chroma == 0:
            # Hue will be undefine and we take the value 0
            hue = 0
        elif max_color == r:
            hue = ((g - b) / chroma) % 6
        elif max_color == g:
            hue = ((b - r) / chroma) + 2
        elif max_color == b:
            hue = ((r - g) / chroma) + 4
        hue *= 60

        # Lightness
        lightness = (max_color + min_color) / 2

        # Saturation
        if lightness == 1 or lightness == 0:
            saturation = 0
        else:
            saturation = chroma / (1 - abs(2 * lightness - 1))

        hue = hue / 360
        return hue, saturation, lightness

    def fromHSL(self, hue: float, saturation: float, lightness: float):
        hue = hue * 360

        chroma = (1 - abs(2 * lightness - 1)) * saturation
        hue = hue / 60
        x = chroma * (1 - abs((hue % 2) - 1))
        if hue < 1 or hue >= 6:
            r, g, b = chroma, x, 0
        elif hue < 2:
            r, g, b = x, chroma, 0
        elif hue < 3:
            r, g, b = 0, chroma, x
        elif hue < 4:
            r, g, b = 0, x, chroma
        elif hue < 5:
            r, g, b = x, 0, chroma
        elif hue < 6:
            r, g, b = chroma, 0, x

        m = lightness - (chroma / 2)
        return r + m, g + m, b + m

    def toHSV(self, r: float, g: float, b: float):
        max_color = max(r, g, b)
        min_color = min(r, g, b)
        chroma = max_color - min_color

        # Hue
        if chroma == 0:
            # Hue will be undefine and we take the value 0
            hue = 0
        elif max_color == r:
            hue = ((g - b) / chroma) % 6
        elif max_color == g:
            hue = ((b - r) / chroma) + 2
        elif max_color == b:
            hue = ((r - g) / chroma) + 4
        hue *= 60

        # Value
        value = max_color

        # Saturation
        if (value == 0):
            saturation = 0
        else:
            saturation = chroma / value

        hue = hue / 360
        return hue, saturation, value

    def fromHSV(self, hue: float, saturation: float, value: float):
        hue = hue * 360

        chroma = value * saturation
        hue = hue / 60
        x = chroma * (1 - abs((hue % 2) - 1))
        if hue < 1 or hue >= 6:
            r, g, b = chroma, x, 0
        elif (hue < 2):
            r, g, b = x, chroma, 0
        elif (hue < 3):
            r, g, b = 0, chroma, x
        elif (hue < 4):
            r, g, b = 0, x, chroma
        elif (hue < 5):
            r, g, b = x, 0, chroma
        elif (hue < 6):
            r, g, b = chroma, 0, x

        m = value - chroma
        return r + m, g + m, b + m

    def toCMY(self, r, g, b):
        c = 1 - r
        m = 1 - g
        y = 1 - b
        return c, m, y

    def fromCMY(self, c, m, y):
        r = 1 - c
        g = 1 - m
        b = 1 - y
        return r, g, b

    def toYCbCr601(self, r, g, b):
        k_b = 0.114
        k_r = 0.299
        y = k_r * r + (1 - k_r - k_b) * g + k_b * b
        p_b = (b - y) / (2 * (1 - k_b))
        p_r = (r - y) / (2 * (1 - k_r))
        # y = y * 219 + 16
        # c_b = p_b * 224 + 128
        # c_r = p_r * 224 + 128

        p_b += 0.5
        p_r += 0.5
        return y, p_b, p_r

    def fromYCbCr601(self, y, p_b, p_r):
        p_b -= 0.5
        p_r -= 0.5

        k_b = 0.114
        k_r = 0.299
        # y = (y - 16) / 219
        # p_b = (c_b - 128) / 224
        # p_r = (c_r - 128) / 224

        b = 2 * p_b * (1 - k_b) + y
        r = 2 * p_r * (1 - k_r) + y
        g = (y - k_r * r - k_b * b) / (1 - k_r - k_b)
        return r, g, b

    def toYCbCr709(self, r, g, b):
        k_b = 0.0722
        k_r = 0.2126
        y = k_r * r + (1 - k_r - k_b) * g + k_b * b
        p_b = (b - y) / (2 * (1 - k_b))
        p_r = (r - y) / (2 * (1 - k_r))
        # y = y * 219 + 16
        # c_b = p_b * 224 + 128
        # c_r = p_r * 224 + 128

        p_b += 0.5
        p_r += 0.5
        return y, p_b, p_r

    def fromYCbCr709(self, y, p_b, p_r):
        p_b -= 0.5
        p_r -= 0.5

        k_b = 0.0722
        k_r = 0.2126
        # y = (y - 16) / 219
        # p_b = (c_b - 128) / 224
        # p_r = (c_r - 128) / 224

        b = 2 * p_b * (1 - k_b) + y
        r = 2 * p_r * (1 - k_r) + y
        g = (y - k_r * r - k_b * b) / (1 - k_r - k_b)
        return r, g, b

    def toYCoCg(self, r, g, b):
        y = 1 / 4 * r + 1 / 2 * g + 1 / 4 * b
        c_o = 1 / 2 * r - 1 / 2 * b
        c_g = -1 / 4 * r + 1 / 2 * g - 1 / 4 * b

        c_o += 0.5
        c_g += 0.5
        return y, c_o, c_g

    def fromYCoCg(self, y, c_o, c_g):
        c_o -= 0.5
        c_g -= 0.5

        r = y + c_o - c_g
        g = y + c_g
        b = y - c_o - c_g
        return r, g, b
