#include <math.h>
#include <stdio.h>

#include "filters.h"

int main(void) {
    /* Test 1: a constant image should remain constant. */
    const double constant[3][4] = {
        {7.5, 7.5, 7.5, 7.5},
        {7.5, 7.5, 7.5, 7.5},
        {7.5, 7.5, 7.5, 7.5}
    };
    double output[3][4];

    /* Give the output a noticeable starting value.
       The filter should overwrite it, not add onto it. */
    for (size_t y = 0; y < 3; ++y) {
        for (size_t x = 0; x < 4; ++x) {
            output[y][x] = -999.0;
        }
    }

    int status = bilateral_filter(3, 4, constant, 1.0, 0.5, output);

    if (status != 0) {
        printf("FAIL: filter returned %d for the constant-image test\n", status);
        return 1;
    }

    for (size_t y = 0; y < 3; ++y) {
        for (size_t x = 0; x < 4; ++x) {
            if (!isfinite(output[y][x]) ||
                fabs(output[y][x] - 7.5) > 1e-9) {
                printf("FAIL: constant-image test at [%zu][%zu]: %f\n",
                       y, x, output[y][x]);
                return 1;
            }
        }
    }

    /* Test 2: with a small sigma_r, preserve a clean 0-to-100 edge. */
    const double step[5][7] = {
        {0, 0, 0, 100, 100, 100, 100},
        {0, 0, 0, 100, 100, 100, 100},
        {0, 0, 0, 100, 100, 100, 100},
        {0, 0, 0, 100, 100, 100, 100},
        {0, 0, 0, 100, 100, 100, 100}
    };
    double step_output[5][7];

    status = bilateral_filter(5, 7, step, 1.0, 5.0, step_output);

    if (status != 0) {
        printf("FAIL: filter returned %d for the edge test\n", status);
        return 1;
    }

    /* These pixels are immediately on either side of the edge. */
    if (!isfinite(step_output[2][2]) ||
        !isfinite(step_output[2][3]) ||
        fabs(step_output[2][2]) > 1e-6 ||
        fabs(step_output[2][3] - 100.0) > 1e-6) {
        printf("FAIL: edge test: left=%f, right=%f\n",
               step_output[2][2], step_output[2][3]);
        return 1;
    }

    printf("PASS: constant-image and edge tests\n");
    return 0;
}