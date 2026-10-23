import os

import nibabel as nib
import numpy as np
import click
from pydicom import dcmread
from pydicom.pixels import apply_rescale
from scipy.ndimage import gaussian_filter
from pmi_lib.image import Image
from pmi_lib.dicom_image import DicomImage

def _get_z_position(dicom_image):
    """
    Extract the z-coordinate of a DICOM image's position.

    Args:
        dicom_image: A pydicom Dataset representing a DICOM image.

    Returns:
        float: The z-coordinate of the image position.
    """
    return dicom_image.ImagePositionPatient[2]


def _get_spacing(dicom_list):
    """calculate spacing of a 2D or 3D dicom image

    Args:
        dicom_list (list): list of dicom data

    Returns:
        tuple(float): tuple of floats containing the pixelspacing in mm.
        Returns (dx, dy) for a single image or (dx, dy, dz) for a multiple slices.
    """
    n = len(dicom_list)  # The number of slices in the list.
    dx, dy = dicom_list[0].PixelSpacing  # x and y pixel spacing from the first slice.

    if n > 1:
        # Get the 3D patient-space positions of the first and last slices.
        # Euclidean distance, and divide it by n-1 to get the slice spacing.
        z_first = np.array(dicom_list[0].ImagePositionPatient)
        z_last = np.array(dicom_list[-1].ImagePositionPatient)
        dz = np.linalg.norm(z_last - z_first) / (n - 1)
        return (float(dx), float(dy), float(dz)) # must be tuple of floats for input Image class
    else:
        # No slice spacing needed for single images
        return (float(dx), float(dy)) # must be tuple of floats for input Image class


def read_dicom(file_path):
    """
    Read a DICOM image or a directory containing a DICOM image series.

    Args:
        file_path (str): Path to a DICOM file or a directory containing
            DICOM image files.

    Returns:
        tuple containing:
            - data (numpy.ndarray): The rescaled image data. A directory
              of slices produces a 3D array; a single file usually produces
              a 2D array.
            - spacing (list): The pixel spacing in millimetres, with two
              values for a single image or three for a multi-slice series.
    """

    # Check if file_path is a directory. If it is, then iterate over the directory and create a 3d volume.
    # If it is not a directory, then open the file as usual.
    if os.path.isdir(file_path):

        dicom_images = sorted([
            dcmread(os.path.join(file_path, file))
            for file in os.listdir(file_path)
            if os.path.isfile(os.path.join(file_path, file))
        ], key=_get_z_position)

        if not dicom_images:
            # Files that are not valid DICOM files will raise an exception.
            raise ValueError("No DICOM files found in the directory.")

        # A volume should contain images from one DICOM series only.
        series_instance_uid = [image.SeriesInstanceUID for image in dicom_images]
        if len(set(series_instance_uid)) != 1:
            raise ValueError("DICOM file(s) found with a different Series Instance UID")

        # Determine the in-plane and between-slice spacing. Decode and rescale each slice,
        # then stack the slices into a single 3D NumPy array.
        spacing = _get_spacing(dicom_images)  # Calculate the spacing.
        hu_values_images = [apply_rescale(image.pixel_array, image) for image in dicom_images]
        hu_values_images = np.array(hu_values_images)

        metadata = {item.keyword: item.value for item in dicom_images[0] if item.keyword and item.keyword != 'PixelData'}
        dicom_image = DicomImage(hu_values_images, spacing, metadata)
        return dicom_image

    else:

        # A single image provides only in-plane spacing. Apply the DICOM rescale
        # parameters to the stored pixel values.
        dicom_image = dcmread(file_path)  # Read the image.
        spacing = _get_spacing([dicom_image])  # Calculate the spacing.
        hu_values_images = apply_rescale(dicom_image.pixel_array, dicom_image)  # Convert from stored pixel values to real values.
        metadata = {img.keyword: img.value for img in dicom_image if img.keyword and img.keyword != 'PixelData'}
        dicom_image = DicomImage(hu_values_images, spacing, metadata)
        return dicom_image


def read_nifti(file_path):
    """
    Load a NIfTI image and return its voxel data and spatial spacing.

    Args:
        file_path (str): Path to the input NIfTI file.

    Returns:
        tuple containing:
            - data (numpy.ndarray): The image voxel data after the
              axis transformations.
            - spacing (tuple): The voxel dimensions obtained from
              the NIfTI header, in millimetres for spatial dimensions.
    """
    # Note that nibabel uses RAS orientation and column-major ordering. It is needed to convert the image to row-major
    # ordering and LPS orientation.
    nifti_image = nib.load(file_path)  # Load the image, including its header and spatial metadata.
    data = np.transpose(nifti_image.get_fdata())  # Convert from XYZ (column-major) to ZYX (row-major) ordering.
    data = np.flip(data, (-1, -2))  # Convert from RAS to LPS: mirror the last two axes (Y and X).
    spacing = tuple(float(s) for s in nifti_image.header.get_zooms())
    img = Image(data, spacing)
    return img


def write_nifti(img: Image, file_path):
    """
    Save a 2D or 3D image array as a compressed NIfTI-1 file.

    Args:
        image (numpy.ndarray): The 2D or 3D image array to save.
        spacing (sequence): Voxel spacing in millimetres
        file_path (str): Output path ending in '.nii.gz'.

    Returns:
        None
    """

    # Validate the required inputs before processing the image.
    image = np.asarray(img)
    spacing = img.spacing

    if image is None or spacing is None or file_path is None:
        raise ValueError("Input cannot be None.")
    # Require a compressed NIfTI output file.
    if not file_path.endswith(".nii.gz"):
        raise ValueError("File path should be nifti, end with .nii.gz.")

    image = np.asarray(image)
    # Only two-dimensional images and three-dimensional volumes are supported by this function.
    if image.ndim not in (2, 3):
        raise ValueError("Image should have 2 or 3 dimensions.")
    # Each image dimension must have a corresponding spacing value.
    if len(spacing) != image.ndim:
        raise ValueError("Image and spacing dimensions must be the same.")

    # Nifti does not support the 'bool' datatype. We need to convert it to e.g. 8-bit int (np.int8).
    image = image.astype(np.int16)

    # Note that nibabel uses RAS orientation and column-major ordering. We need to convert from LPS orientation and
    # row-major ordering.
    image = np.flip(image, (-1, -2))
    image = np.transpose(image)

    # Construct an affine transformation matrix.
    spacing_array = np.eye(4)  # 4×4 identity matrix
    for i, dim in enumerate(spacing):
        spacing_array[i, i] = dim  # Set diagonal value (i, i) to spacing[i].

    # Create a Nifti1Image image and save it.
    new_image = nib.nifti1.Nifti1Image(image, spacing_array)
    nib.nifti1.save(new_image, file_path)


@click.command()
@click.argument(
    "file_path_dicom",
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    required=True)
@click.argument("file_path_nifti", required=True)
def dicom_to_nifti(file_path_dicom, file_path_nifti):
    """
    Convert a DICOM image or series into a compressed NIfTI file.

    Args:
        file_path_dicom (str): Path to a DICOM file or series directory.
        file_path_nifti (str): Destination path ending in '.nii.gz'.
    """

    try:
        dicom_img = read_dicom(file_path_dicom)  # Load the DICOM data and its voxel spacing.
        write_nifti(dicom_img, file_path_nifti)  # Save the data as a compressed NIfTI image.
        click.echo("Conversion successful.")

    except (OSError, ValueError) as e:
        # Report expected input, file-access, or validation errors.
        click.echo(f"Error during conversion: {e}", err=True)

    except Exception as e:
        # Report unexpected errors without displaying a full traceback.
        click.echo(f"Unexpected error: {e}", err=True)


def masked_gaussian_filter(img: Image, boolean_mask, sd_gaussian_kernel):
    """
    Apply Gaussian smoothing to image data within a binary mask.

    Args:
        pixel_data (numpy.ndarray): Input image data
        boolean_mask (numpy.ndarray): Boolean mask with the
            same shape as pixel_data.
        sd_gaussian_kernel (sequence): Gaussian standard deviation for
            each image axis, in pixels.

    Returns:
        numpy.ndarray: Smoothed image data as floating-point values,
            with pixels outside the mask set to zero.
    """
    pixel_data = np.asarray(img)
    spacing = img.spacing

    if (pixel_data.shape != boolean_mask.shape or
            # sd_gaussian_kernel can be a single value, in this condition, len(sd_gaussian_kernel) can cause an error,
            # so, np.isscalar(sd_gaussian_kernel) is essential
            (not np.isscalar(sd_gaussian_kernel) and pixel_data.ndim != len(sd_gaussian_kernel))):
        raise ValueError("Image, mask and standard deviation have incompatible dimensions.")

    # Use floating-point values to support smoothing and normalization.
    pixel_data = np.asarray(pixel_data, dtype=np.float32)
    boolean_mask = np.asarray(boolean_mask, dtype=np.float32)

    sigma_pixels = np.asarray(sd_gaussian_kernel, dtype=np.float32) / np.asarray(spacing)

    numerator = gaussian_filter(boolean_mask * pixel_data, sigma_pixels)  # Smooth the masked image.
    denominator = gaussian_filter(boolean_mask, sigma_pixels)  # Smooth the mask to estimate overlap

    # Normalize by the local mask response and exclude pixels outside the original mask.
    result = boolean_mask * (numerator / denominator)
    return np.nan_to_num(result)


def test(file_path):
    """
    Run a basic end-to-end demonstration of the image-processing functions.

    Reads a DICOM image or series, writes it to NIfTI, reads the generated
    file back, runs the conversion command, and applies masked Gaussian
    smoothing.

    Args:
        file_path (str): Path to a DICOM file or series directory.
    """

    # Read the input image and its voxel spacing.
    img = read_dicom(file_path)
    img_as_array = np.asarray(img)

    # Save a NIfTI copy and check that it can be read back.
    nifti_path = "test_only_def.nii.gz"
    write_nifti(img, nifti_path)
    read_nifti(nifti_path)

    # Click commands take an argument list; keep running after conversion.
    dicom_to_nifti(
        args=[file_path, "test_whole_module.nii.gz"],
        standalone_mode=False,
    )
    
    # Create and apply  mask to the image.
    mask = np.ones(img_as_array.shape, dtype=bool)
    sd = tuple(1.0 for _ in range(img_as_array.ndim))  # Use a Gaussian standard deviation of one voxel along every axis.
    masked_gaussian_filter(img, mask, sd)


if __name__ == "__main__":
    # Expose the DICOM-to-NIfTI converter as a command-line application.
    test("ct_jaw")
