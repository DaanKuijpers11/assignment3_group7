_lib = np.ctypeslib.load_library("pmi", Path(__file__).parent)
import math

from matplotlib import pyplot as plt


def bilateral_filter(data: np.ndarray, sigma_s: float, sigma_r: float) -> np.ndarray:
    """
    Applies a 1-dimensional bilateral filter.

    :param data: A 1-dimensional numpy array.
    :param sigma_s: The standard deviation of the spatial kernel (sample distance).
    :param sigma_r: The standard deviation of the range kernel (sample values).
    :return: A filtered 1-dimensional numpy array.
    """
    # The kernel size is at least 3× the spatial SD.
    kernel_size = math.ceil(3 * sigma_s)

    # Initialize the result as an array of zeros with the same shape and datatype as the data.
    result = np.zeros_like(data)

    # Iterate over the data and apply the filter to each sample.
    for i in range(data.shape[0]):
        weight_sum = 0.0  # We need to normalize the average to the sum of weights.

        # First and last neighbor samples to include in the kernel for sample i.
        start = max(i - kernel_size, 0)
        end = min(i + kernel_size, data.shape[0] - 1)

        # Iterate over the samples in the neighborhood.
        for j in range(start, end + 1):
            s = i - j  # Spatial distance between samples
            r = data[i] - data[j]  # Difference in sample values

            weight_s = np.exp(-s**2 / (2 * sigma_s**2))  # Spatial weight (sample distance)
            weight_r = np.exp(-r**2 / (2 * sigma_r**2))  # Range weight (sample values)
            weight = weight_s * weight_r  # Net weight is the product of the spatial and range weight.

            result[i] += weight * data[j]  # Add the contribution of sample j.
            weight_sum += weight  # Add the weight for sample j to the sum.

        # Normalize the average for pixel i.
        result[i] /= weight_sum

    return result
