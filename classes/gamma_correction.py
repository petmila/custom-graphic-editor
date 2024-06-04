import numpy as np
import math


class GammaCorrection:
    def gamma_correction(self, colormap, current_gamma, new_gamma):
        return self.from_linear(self.to_linear(colormap, current_gamma), new_gamma)

    def to_linear(self, colormap, current_gamma):
        linear_colormap = colormap.copy()
        if current_gamma == 0:
            linear_colormap = self.from_sRGB(linear_colormap)
        else:
            linear_colormap = linear_colormap ** current_gamma
        return linear_colormap

    def from_linear(self, linear_colormap, new_gamma):
        gamma_colormap = linear_colormap.copy()
        if new_gamma == 0:
            gamma_colormap = self.to_sRGB(gamma_colormap)
        else:
            gamma_colormap = gamma_colormap ** 1 / new_gamma
        return gamma_colormap

    def to_sRGB(self, linear_colormap):
        srgb_colormap = linear_colormap.copy()
        func = np.vectorize(self.one_color_to_sRGB)
        return func(srgb_colormap)

    def from_sRGB(self, srgb_colormap):
        linear_colormap = srgb_colormap.copy()
        func = np.vectorize(self.one_color_to_linear)
        return func(linear_colormap)

    def one_color_to_linear(self, color_srgb: float):
        color_lin = 0
        if color_srgb <= 0.04045:
            color_lin = color_srgb / 12.92
        else:
            color_lin = ((color_srgb + 0.055) / 1.055) ** 2.4
        return color_lin

    def one_color_to_sRGB(self, color_lin: float):
        color_srgb = 0
        if color_lin <= 0.0031308:
            color_srgb = color_lin * 12.92
        else:
            color_srgb = 1.055 * (color_lin ** (1 / 2.4)) - 0.055
        return color_srgb

    def one_value_to_linear(self, value: float, current_gamma: float):
        if math.isclose(current_gamma, 0):
            value = self.one_color_to_linear(value)
        else:
            value = value ** current_gamma
        return value

    def one_value_from_linear(self, value: float, new_gamma: float):
        if math.isclose(new_gamma, 0):
            value = self.one_color_to_sRGB(value)
        else:
            value = value ** (1 / new_gamma)
        return value
