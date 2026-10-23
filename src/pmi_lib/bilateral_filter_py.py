_lib = np.ctypeslib.load_library("pmi", Path(__file__).parent)

import math

import numpy as np
from .classes import Image # Used for the Image - objects

from matplotlib import pyplot as plt


def bilateral_filter(image: Image, sigma_s: float, sigma_r: float) -> Image:
    """
    Applies a 1-dimensional bilateral filter.

    :param image: An Image object containing the input data.
    :param sigma_s: The standard deviation of the spatial kernel (sample distance).
    :param sigma_r: The standard deviation of the range kernel (sample values).
    :return: A filtered 1-dimensional numpy array.
    """
    # ValueError for when the image is not 2D.
    if image._data.ndim != 2:
        raise ValueError("The image must be 2D.")

    data = image._data

    # Initialize the result as an array of zeros with the same shape and datatype as the image.
    result = np.zeros_like(data, dtype=float)

    # Convert the spatial kernel size from millimeters to pixels for 2D.
    spacing_y, spacing_x = image.spacing
    kernel_y = math.ceil(3 * sigma_s / spacing_y)
    kernel_x = math.ceil(3 * sigma_s / spacing_x)

    # Two loops for all the pixel in 2D image
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            weight_sum = 0.0

            # Determine the 2D-kernel boundaries, ensuring they stay within the image dimensions. Around the pixel (i, j).
            start_y = max(i - kernel_y, 0)
            end_y = min(i + kernel_y, data.shape[0] - 1)
            start_x = max(j - kernel_x, 0)
            end_x = min(j + kernel_x, data.shape[1] - 1)

            # Two loops for all the pixel in the 2D-kernel
            for k in range(start_y, end_y + 1):
                for l in range(start_x, end_x + 1):
                    # Calculate spatial distance in millimeters, changed to 2D.
                    s = ((i - k) * spacing_y) ** 2
                    s += ((j - l) * spacing_x) ** 2

                    # Difference in pixel values (intensity difference).
                    r = data[i, j] - data[k, l]

                    weight_s = np.exp(-s / (2 * sigma_s**2))
                    weight_r = np.exp(-r**2 / (2 * sigma_r**2))
                    weight = weight_s * weight_r

                    # Now use the 2D-pixelindices (k, l) to access the pixel value in the 2D-image.
                    result[i, j] += weight * data[k, l]
                    weight_sum += weight

            result[i, j] /= weight_sum

            # Make resulting image object.
            result_image = Image(result, spacing=image.spacing)

    return result_image