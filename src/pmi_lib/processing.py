import numpy as np
from scipy.ndimage import gaussian_filter

from .classes import Image


def masked_gaussian_filter(
    image: Image, mask: np.ndarray, std: float | tuple[float, ...]
) -> Image:
    """
    Apply a Gaussian filter to an image, but only within a specified mask.

    :param data: 2D or 3D numpy array representing the image
    :param mask: 2D or 3D boolean numpy array of the same shape as data, where True indicates the region to filter
    :param std: standard deviation for Gaussian filter, can be a single float or a tuple for each dimension in mm
    :return: a new Image object with the filtered image data
    """
    # extract data and spacing from the Image object
    data = image._data
    spacing = image.spacing

    # check if the inputs are of the correct type
    if type(data) != np.ndarray:
        raise ValueError(f"Data must be a numpy array, not a {type(data)}.")

    if type(mask) != np.ndarray:
        raise ValueError(f"Mask must be a numpy array, not a {type(mask)}.")
    if mask.dtype != bool:
        raise ValueError(f"Mask must be a boolean array, not a {mask.dtype}.")

    if type(std) != float and type(std) != tuple:
        raise ValueError(
            f"Standard deviation must be a float or a tuple, not a {type(std)}."
        )

    # check if mask is compatible with given data
    if np.shape(data) != np.shape(mask):
        raise ValueError(
            f"Data shape {np.shape(data)} does not match mask shape {np.shape(mask)}."
        )

    # convert to 32-bit floating point precision
    data = data.astype(np.float32)
    mask = mask.astype(np.float32)

    # mask the image (where mask is True keep data, else set to 0)
    masked_image = mask * data

    # apply gaussian filter to the masked image
    std_pixels = tuple(
        np.asarray(std) / np.asarray(spacing)
    )  # convert std from mm to pixels
    gaus_filt_masked_img = gaussian_filter(masked_image, std_pixels)

    # apply gaussian filter to the mask
    gaus_filt_mask = gaussian_filter(mask, std_pixels)

    # normalize the filtered masked image
    gaus_filt_norm_img = gaus_filt_masked_img / gaus_filt_mask
    gaus_filt_norm_img = np.nan_to_num(
        gaus_filt_norm_img, nan=0.0
    )  # replace NaN with 0

    # re-apply mask to the normalized filtered image (to zero out areas outside the mask)
    mask_filt_img = mask * gaus_filt_norm_img

    return Image(mask_filt_img, spacing)
