
import math

import numpy as np

from .classes import Image


def bilateral_filter_py(
    image: Image, sigma_s: float, sigma_r: float
) -> Image:
    """Apply a 2D bilateral filter to an Image."""
    if image._data.ndim != 2:
        raise ValueError("The image must be 2D.")

    if sigma_s <= 0 or sigma_r <= 0:
        raise ValueError("sigma_s and sigma_r must be positive.")

    data = image._data.astype(float, copy=False)
    result = np.zeros_like(data, dtype=float)

    # Convert sigma_s from millimeters to a pixel radius in each dimension.
    spacing_y, spacing_x = image.spacing
    kernel_y = math.ceil(3 * sigma_s / spacing_y)
    kernel_x = math.ceil(3 * sigma_s / spacing_x)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            weight_sum = 0.0

            start_y = max(0, i - kernel_y)
            end_y = min(data.shape[0], i + kernel_y + 1)
            start_x = max(0, j - kernel_x)
            end_x = min(data.shape[1], j + kernel_x + 1)

            for k in range(start_y, end_y):
                for l in range(start_x, end_x):
                    # Calculate squared physical distance in mm.
                    s = ((i - k) * spacing_y) ** 2
                    s += ((j - l) * spacing_x) ** 2

                    # Calculate the difference in image intensity.
                    r = data[i, j] - data[k, l]

                    weight_s = np.exp(-s / (2 * sigma_s**2))
                    weight_r = np.exp(-r**2 / (2 * sigma_r**2))
                    weight = weight_s * weight_r

                    result[i, j] += weight * data[k, l]
                    weight_sum += weight

            result[i, j] /= weight_sum

    return Image(result, spacing=image.spacing)
