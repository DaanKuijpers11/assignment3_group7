#include "filters.h"    //TODO: ADD A FILE FILTERS.H THAT HAS THE PROPER FUNCTIONS
#include <stddef.h>   // Provides NULL and size_t
#include <math.h>     // Provides exp()

// A neighborhood is often represented as a square matrix of weights, which is why image-processing explanations commonly call it a “kernel.
//KERNEL IN 2D IMAGES IS SPATIAL: For a 2D image, neighbors lie in a two-dimensional grid

//  Applies a 1-dimensional bilateral filter.
//  Returns 0 on success, -1 on invalid arguments.
//  TODO: CHECK EDGE-CASES AND ERRORS
int bilateral_filter(
    // const : the function can read the input values, but should not change them.
    size_t rows,
    size_t cols,
    const double data[rows][cols],    // Pointer to a 1-dimensional array.
                                        //const size_t length,   // Number of elements in 'data'. is not used in the 2D array version
    const double sigma_s,  // The standard deviation of the spatial kernel (sample distance).
    const double sigma_r,  // The standard deviation of the range kernel (sample values).
    double result[rows][cols]         // Pointer to the output array (must have at least 'length' elements).
    )
{
    // Make sure that data and result point to valid arrays, and that the SD's are positive.
    if (data == NULL || result == NULL || sigma_s <= 0.0 || sigma_r <= 0.0) {
        return -1;
    }

    //We are looking at equal nr of neighbors in each direction (vertical and horizontal)
    //Defining radius : the number of pixels to look in each direction <- PREVIOUSLY THAT WAS THE KERNEL!!!!!
    const size_t radius = (size_t)ceil(3.0 * sigma_s);
    // previously for 1D :The kernel size is at least 3× the spatial SD.
    //const size_t kernel_size = (size_t)ceil(3.0 * sigma_s);

    //KERNEL is how far we are looking in all directions, so it's length is length of radius to the left, right (or top/bottom) +1
    const size_t kernel_size= 2 * radius + 1;


    // Iterate over the data and apply the filter to each sample. i -> y ; j -> x
    for (size_t y = 0; y < rows; y++) {
        for (size_t x = 0; x <= cols; x++) {
            double weight_sum = 0.0;  // We need to normalize the average to the sum of weights.
            double kernel[kernel_size][kernel_size]; //2D kernel for a 2D matrix
            result[y][x]=0.0;

            // Iterate over the samples in the neighborhood. dy, dx are the changing positions in y and x direction so rows and columns
            for (size_t dy = -radius ; dy <= radius; dy++) {
                for(size_t dx = -radius; dx <= radius, dx++){
                    const double neighbor_y = (size_t)y - (size_t)dy;  // Spatial distance between samples y:centre pixel, dy: the distance it's neighnor is in the y direction
                    const double neighbor_x = (size_t)x - (size_t)dx;

                    // exception handling: Ignore neighbors outside the image boundary.
                    if (neighbor_y < 0 || neighbor_x < 0 ||
                        neighbor_y >= (ptrdiff_t)rows ||
                        neighbor_x >= (ptrdiff_t)cols)
                        continue;

                                            //const double r = data[i] - data[j];  // Difference in sample values <- formula for this changes for the 2data
                    const double distance =(dx * dx + dy * dy); //calculating the pixel distance using the 2 variable formula (squared)
                    const double value_difference = data[y][x] - data[neighbor_y][neighbor_x];

                    const double weight_s = exp(-distance/(2.0 * sigma_s * sigma_s);  // Spatial weight (sample distance)
                    const double weight_r = exp(-(value_difference * value_difference) / (2.0 * sigma_r * sigma_r));  // Range weight (sample values)
                    const double weight = weight_s * weight_r;  // Net weight is the product of the spatial and range weight.

                    result[y][x] += weight * data[neighbor_y][neighbor_x];  // Add the contribution of sample j.
                    weight_sum += weight;  // Add the weight for sample j to the sum.
            }

            // Normalize the average for pixel i.
            result[y][x] /= weight_sum;
    }

    return 0;
}
