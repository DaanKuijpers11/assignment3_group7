#include "filters.h"

#include <stddef.h>   // Provides NULL and size_t
#include <math.h>     // Provides exp()


//  Applies a 1-dimensional bilateral filter.
//  Returns 0 on success, -1 on invalid arguments.
int bilateral_filter(
    const double *data,    // Pointer to a 1-dimensional array.
    const size_t length,   // Number of elements in 'data'.
    const double sigma_s,  // The standard deviation of the spatial kernel (sample distance).
    const double sigma_r,  // The standard deviation of the range kernel (sample values).
    double *result         // Pointer to the output array (must have at least 'length' elements).
) {
    // Make sure that data and result point to valid arrays, and that the SD's are positive.
    if (data == NULL || result == NULL || sigma_s <= 0.0 || sigma_r <= 0.0) {
        return -1;
    }

    // The kernel size is at least 3× the spatial SD.
    const size_t kernel_size = (size_t)ceil(3.0 * sigma_s);

    // Iterate over the data and apply the filter to each sample.
    for (size_t i = 0; i < length; i++) {
        double weight_sum = 0.0;  // We need to normalize the average to the sum of weights.

        // First and last neighbor samples to include in the kernel for sample i.
        const size_t start = i > kernel_size ? i - kernel_size : 0;
        const size_t end = i + kernel_size < length - 1 ? i + kernel_size: length - 1;

        result[i] = 0.0;  // Initialize the result as zero.

        // Iterate over the samples in the neighborhood.
        for (size_t j = start; j <= end; j++) {
            const double s = (double)i - (double)j;  // Spatial distance between samples
            const double r = data[i] - data[j];  // Difference in sample values

            const double weight_s = exp(-(s * s) / (2.0 * sigma_s * sigma_s));  // Spatial weight (sample distance)
            const double weight_r = exp(-(r * r) / (2.0 * sigma_r * sigma_r));  // Range weight (sample values)
            const double weight = weight_s * weight_r;  // Net weight is the product of the spatial and range weight.

            result[i] += weight * data[j];  // Add the contribution of sample j.
            weight_sum += weight;  // Add the weight for sample j to the sum.
        }

        // Normalize the average for pixel i.
        result[i] /= weight_sum;
    }

    return 0;
}
