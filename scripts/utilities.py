import numpy as np


def unnormalize_data(data):
    colormap = data.copy()
    colormap = colormap.astype("float")
    colormap = colormap / 255
    return colormap


# данные переводятся обратно в [0-255] перед сохранением/отрисовкой
def normalize_data(data):
    normalized_colormap = data.copy()
    normalized_colormap = (normalized_colormap * 255)
    normalized_colormap = np.round(normalized_colormap)
    normalized_colormap[normalized_colormap > 255] = 255
    normalized_colormap[normalized_colormap < 0] = 0
    normalized_colormap = normalized_colormap.astype("uint8")
    return normalized_colormap