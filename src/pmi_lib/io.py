import os

import nibabel as nib
import numpy as np
import pydicom
from pydicom import dcmread
from pydicom.pixels import apply_rescale

from .classes import DicomImage, Image


def read_dicom(file_path: str) -> DicomImage:
    """
    Read a DICOM file or directory of DICOM files.

    :param file_path: path to the DICOM file or directory
    :return: a DicomImage object containing the image data, metadata, and spacing
    """
    # check if the file or directory exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file or directory {file_path} does not exist.")

    # check if the path is a directory
    elif os.path.isdir(file_path):
        dicom_images = []
        # read all DICOM files in the directory.
        for file_name in os.listdir(file_path):
            full_path = os.path.join(file_path, file_name)
            if os.path.isfile(full_path):
                slice_img = dcmread(full_path)
                # check if Series Instance UID of current DICOM matches that of first file
                if (
                    len(dicom_images) != 0
                    and slice_img.SeriesInstanceUID != dicom_images[0].SeriesInstanceUID
                ):
                    raise ValueError(
                        f"DICOM file {file_name} has a different Series Instance UID than the first file/other files."
                    )
                dicom_images.append(slice_img)

        # sort the files by spatial position
        sorted_images = sorted(dicom_images, key=_get_z_position)

        # calculate the spacing
        spacing = _get_spacing(sorted_images)

        # convert from stored pixel values to real values
        slices = []
        for dicom_image in sorted_images:
            slices.append(apply_rescale(dicom_image.pixel_array, dicom_image))

        # return the image (array) and spacing (tuple)
        dcm_img = np.array(slices)
        spacing = tuple(spacing)

        # build metadata from the DICOM dataset, excluding the pixel data itself
        metadata = {
            elem.keyword: elem.value
            for elem in slice_img
            if elem.keyword and elem.keyword != "PixelData"
        }

        return DicomImage(dcm_img, metadata, spacing)

    # check if the path is a file
    elif os.path.isfile(file_path):
        # read the DICOM file
        dicom_image = dcmread(file_path)

        # calculate the spacing (tuple)
        spacing = _get_spacing([dicom_image])
        spacing = tuple(spacing)

        # convert from stored pixel values to real values (array)
        dcm_img = apply_rescale(dicom_image.pixel_array, dicom_image)

        # build metadata from the DICOM dataset, excluding the pixel data itself
        metadata = {
            elem.keyword: elem.value
            for elem in dicom_image
            if elem.keyword and elem.keyword != "PixelData"
        }

        return DicomImage(dcm_img, metadata, spacing)


def read_nifti(file_path: str) -> Image:
    """
    Read a NIfTI file.

    :param file_path: path to the NIfTI file
    :return: an Image object containing the image data and spacing
    """
    # check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file or directory {file_path} does not exist.")

    # read the image
    nifti_image = nib.load(file_path)

    # get the pixel data
    data = nifti_image.get_fdata()

    # convert from column-major (XYZ) to row-major ordering (ZYX) and from RAS to LPS orientation (mirror Y and X)
    nii_img = np.transpose(data)
    nii_img = np.flip(nii_img, (-1, -2))

    # get the spacing from the header
    spacing = nifti_image.header.get_zooms()

    return Image(nii_img, spacing)


def write_nifti(image: Image, file_path: str) -> None:
    """
    Write a NIfTI file.

    :param data: image data
    :param spacing: voxel spacing
    :param file_path: path to save the NIfTI file"""
    # convert data to array
    data = np.array(image._data)
    spacing = image.spacing

    # NIfTI does not support 'bool' datatype, convert it to uint8
    if data.dtype == bool:
        data = data.astype(np.uint8)

    # check if spacing is compatible with given data
    if len(spacing) != data.ndim:
        raise ValueError(
            f"Spacing length {len(spacing)} does not match data dimensions {data.ndim}."
        )

    # construct an affine transformation matrix (matrix with spacing on diagonal)
    affine = np.eye(4)
    for i, s in enumerate(spacing):
        affine[i, i] = s

    # create a nifti image and save it
    nii_image = nib.nifti1.Nifti1Image(data, affine)

    nib.nifti1.save(nii_image, file_path)


def _get_z_position(dicom_image: pydicom.dataset.Dataset) -> float:
    """
    Get the Z position of a DICOM image.

    :param dicom_image: a DICOM image
    :return: the Z position of the image
    """
    return dicom_image.ImagePositionPatient[2]


def _get_spacing(dicom_list: list[pydicom.dataset.Dataset]) -> list[float]:
    """
    Get the spacing of a list of DICOM images.

    :param dicom_list: a list of DICOM images
    :return: a list of spacing values [dx, dy, dz]
    """
    n = len(dicom_list)  # number of slices
    dx, dy = dicom_list[0].PixelSpacing  # x, y pixel spacing

    # check if there are multiple slices
    if n > 1:
        # calculate z spacing as total distance / number of slices
        z_first = np.array(dicom_list[0].ImagePositionPatient)  # first slice position
        z_last = np.array(dicom_list[-1].ImagePositionPatient)  # last slice position
        dz = np.linalg.norm(z_last - z_first) / (n - 1)  # z spacing
        return [dz, dx, dy]
    else:
        # there is just one slice, so no slice spacing
        return [dx, dy]
