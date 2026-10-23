# HOW TO USE THE LIBRARY

## Usage
The library is designed for operations on medical imaging files in DICOM and NIFTI format.

## Installation
Refer to the README installation instructions

### Example of calling onto the functions in the terminal:
`dicom-to-nifti --help`
or
`dicom-to-nifti "path/to/dicom_series" "path/to/output.nii.gz"`

Results in the direct output in the terminal:
Usage: dicom-to-nifti [OPTIONS] DICOM_PATH NIFTI_PATH

  Convert a DICOM file or directory to a NIfTI file.

  :param dicom_path: path to the DICOM file or directory :param nifti_path:
  path to the output NIfTI file

Options:
  --help  Show this message and exit. 
  

## FUNCTIONS
### `dicom_to_nifti(dicom_path:str,nifti_path:str)`


**Used arguments**

dicom_path -> DICOM_PATH can be a single DICOM file or a directory containing one DICOM series.
nifti_path -> NIFTI_PATH is the path for the output NIfTI file.

**What is returned**

The function saves the converted image into a new NIFTI file in the location given by the nifti_path argument.

**Behavior**
- Reads the DICOM image and its spacing.
- Converts the image orientation from LPS to RAS and changes the axis order from ZYX to XYZ.
- Writes the converted image and spacing as a NIfTI file.

**Raises**
- 'click.ClickException' : The input path does not exist, the DICOM directory contains different series, or an error occurs while reading, converting, or writing the image.


### `read_dicom(file_path)`
Read a DICOM file or a directory of DICOM files and return a `DicomImage`.

**Used arguments**
'file_path' ('str')': Path to a DICOM file or to a directory containing DICOM files.

**What is returned**
- `DicomImage`: Contains the image data, metadata, and spacing.

**Behavior**

- For a file, reads that DICOM image.
- For a directory, reads its files, checks that they belong to the same DICOM series, and sorts them by spatial position before combining their image data.
- Rescales the pixel values and excludes the raw `PixelData` element from the returned metadata.

**Raises**

- `FileNotFoundError`: The path does not exist.
- `ValueError`: The directory contains DICOM files with different series identifiers.


### `read_nifti(file_path:str)`

Read  a NIFTI file and return ann 'Image'

**Used Arguments**
'file_path (str)': Path to the NIfTI file.

 **What is returned**
 'Image' : contains the image data and spacing

 **Behavior**
- Loads the image data from the NIfTI file.
- Converts the axis order from XYZ to ZYX and the orientation from RAS to LPS.
- Gets the spacing from the NIfTI image header.

**Raises**
- 'FileNotFoundError': The path does not exist.
- Possible error from NiBabel if the file exists but cannot be read as a NIfTI image.

### `write_nifti(image, file_path)`
Writes a 'Image' object into a NIFTI file

**Used Arguments**
- 'image (Image)' ': Image object containing the image data and voxel spacing.
- 'file_path (str)' ': Path where the NIfTI file will be saved.

**What is returned**
 'None' : The image is saved into the NIFTI file specified by the 'file_path' in the arguments

**Behavior**
- Converts the image data to a NumPy array.
- Converts boolean image data to uint8, since NIfTI does not support the boolean data type.
- Checks that the number of spacing values matches the number of image dimensions.
- Creates the NIfTI image using the data and spacing, then saves it to file_path.

**Raises**
- 'ValueError' : The number of spacing values does not match the number of image dimensions.
- An error from NiBabel or the operating system if the image cannot be saved to the specified path.

### `_get_z_position(dicom_image)`

Get the Z coordinate of a DICOM image from its patient-position metadata.

**Used arguments**

- `dicom_image` (`pydicom.dataset.Dataset`): DICOM dataset containing `ImagePositionPatient`.

**What is returned**

- `float`: The Z coordinate, taken from the third value in `ImagePositionPatient`.

**Behavior**

- Reads `ImagePositionPatient[2]`. This function gets the position of a single image; it does not sort images or calculate spacing.

**Raises**

- `AttributeError`: The DICOM dataset does not contain `ImagePositionPatient`.
- `IndexError`: `ImagePositionPatient` does not contain at least three values.

### `_get_spacing(dicom_list)`

Get the pixel spacing and, when available, the spacing between DICOM slices.

**Used arguments**

- `dicom_list` (`list[pydicom.dataset.Dataset]`): DICOM datasets. For multiple slices, they should be ordered by position.

**What is returned**

- `list[float]`: The spacing values. Returns `[dx, dy]` for one dataset, or `[dx, dy, dz]` for multiple datasets.

**Behavior**

- Gets `dx` and `dy` from the first dataset’s `PixelSpacing`.
- If the list contains multiple datasets, calculates `dz` as the distance between the first and last image positions divided by the number of intervals between slices.
- Does not sort the datasets; for multiple slices, their order affects the calculated `dz`.

**Raises**

- `IndexError`: The list is empty.
- `AttributeError`: A dataset is missing metadata required to calculate spacing.



### `masked_gaussian_filter(image, mask, std)`

Apply a Gaussian filter to image data within a specified mask and return a new `Image`.

**Used arguments**

- `image` (`Image`): Image object containing the data to filter and its voxel spacing.
- `mask` (`numpy.ndarray`): Boolean array with the same shape as the image data. `True` marks the region to filter.
- `std` (`float` or `tuple[float, ...]`): Gaussian standard deviation in millimetres. A tuple can specify a value for each image dimension.

**What is returned**

- `Image`: A new image object containing the filtered data and the original image spacing.

**Behavior**

- Converts the standard deviation from millimetres to pixels using the image spacing.
- Filters the masked image and the mask, then normalizes the filtered image by the filtered mask.
- Sets values outside the mask to zero in the returned image.
- Replaces `NaN` values produced during normalization with zero.

**Raises**

- `ValueError`: The image data or mask is not a NumPy array, the mask is not boolean, `std` is not a float or tuple, or the mask shape does not match the image data shape.


## CLASSES

## `Image`

Represent an N-dimensional image as a NumPy array with spacing information.

**Used arguments**

- `data` (`numpy.ndarray`): The image data.
- `spacing` (`tuple[float, ...]` or `None`): The spacing in millimetres for each image dimension. If omitted, each dimension’s spacing defaults to `1.0`.

**What is returned**

- `Image`: An image object containing the data and spacing. The data is stored in `_data`, and spacing is available through `spacing`.

**Behavior**

- Converts numeric spacing values to floats.
- Supports getting the outer dimension’s size with `len(image)`.
- Supports NumPy array conversion, including optional data-type conversion.
- Supports indexing, such as `image[key]`.
- `get_pixel_area()` returns the area of one pixel, in mm², using the first two spacing values.
- `get_voxel_volume()` returns the volume of one voxel, in mm³, using the first three spacing values.
- Printing the object shows its data type, shape, and spacing.

**Raises**

- `TypeError`: `data` is not a NumPy array; `spacing` is not a tuple or `None`; or a spacing value is not numeric or is boolean.
- `ValueError`: The number of spacing values does not match the number of image dimensions; the image has fewer than two dimensions when calculating pixel area; or it has fewer than three dimensions when calculating voxel volume.

## `DicomImage`

Represent a DICOM image as an `Image` with additional DICOM metadata.

**Used arguments**

- `data` (`numpy.ndarray`): The image data.
- `metadata` (`dict[str, Any]`): A dictionary containing DICOM metadata.
- `spacing` (`tuple[float, ...]` or `None`): The spacing in millimetres for each image dimension. If omitted, each dimension’s spacing defaults to `1.0`.

**What is returned**

- `DicomImage`: An image object containing the image data, spacing, and DICOM metadata.

**Behavior**

- Inherits the image data, spacing, and functionality of `Image`.
- Stores the supplied metadata in `metadata`.

**Raises**

- `TypeError`: `metadata` is not a dictionary, or the inherited `Image` initialization receives arguments of the wrong type.
- `ValueError`: The inherited `Image` initialization finds that the number of spacing values does not match the number of image dimensions.


## `test(file_path)`
It is possible to test the functions in the pmi_lib module. In order to do that in the command line user should run:
python -c "from pmi_lib.testing import test; test(r'C:\path\to\your\dicom_file.dcm')"

