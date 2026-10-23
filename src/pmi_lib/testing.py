from .classes import DicomImage, Image
from .cli import dicom_to_nifti
from .io import read_dicom, read_nifti, write_nifti
from .processing import masked_gaussian_filter


def test(file_path: str) -> None:
    """
    Test the functions in the pmi_lib module.

    :param file_path: path to the DICOM file or directory
    """
    print(
        "-- initialize testing of functions --"
    )
    
    # read DICOM files
    dcm_image = read_dicom(file_path)
    dcm_img = dcm_image._data
    dcm_spacing = dcm_image.spacing
    print(
        f"1. read_dicom executed successfully: shape={dcm_img.shape}, spacing={dcm_spacing} \\n"
    )

    # convert DICOM to NIfTI
    nii_path = "test_output.nii.gz"
    dicom_to_nifti.callback(
        file_path, nii_path
    )  # uses write_nifti internally, callback handles click decorator
    print(
        f"2. dicom_to_nifti & write_nifti executed successfully: output file={nii_path}\\n"
    )

    # read NIfTI file
    nii_image = read_nifti(nii_path)
    nii_img = nii_image._data
    nii_spacing = nii_image.spacing
    print(
        f"3. read_nifti executed successfully: shape={nii_img.shape}, spacing={nii_spacing}\\n"
    )

    # apply masked Gaussian filter
    mask = dcm_img > 0
    std = tuple(0.8 for _ in range(dcm_img.ndim))
    mask_filt_img = masked_gaussian_filter(dcm_image, mask, std)
    print(
        f"4. masked_gaussian_filter executed successfully: shape={mask_filt_img._data.shape}\\n"
    )

    # write NIfTI file
    nii_output_path = "test_filter_output.nii.gz"
    write_nifti(mask_filt_img, nii_output_path)
    print(
        f"5. write_nifti executed successfully: output file={nii_output_path}\\n"
    )

    print(
        "-- successfully completed testing of functions --"
    )

    # ---

    print(
        "-- initialize testing of class attributes --"
    )

    # check Image attributes with NIfTI image
    image_nii = Image(nii_img) # use default spacing
    print(
        f"6. __repr__ executed successfully: {image_nii}"
    )

    # calculate outer dimension
    nr_slices = len(image_nii)
    print(
        f"7. __len__ executed successfully: number of slices={nr_slices}"
    )

    # convert to numpy array with int dtype
    nii_array = image_nii.__array__(dtype=int)
    print(
        f"8. __array__ executed successfully: array shape={nii_array.shape}, dtype={nii_array.dtype}"
    )

    # get element at index [0, 0, 0] (or any other valid ndim)
    item = image_nii[tuple(0 for _ in range(nii_img.ndim))]
    print(
        f"9. __getitem__ executed successfully: element at {tuple(0 for _ in range(nii_img.ndim))} = {item}"
    )

    # calculate pixel area
    pixel_area = image_nii.get_pixel_area()
    print(
        f"10. get_pixel_area executed successfully: pixel area={pixel_area} mm^2"
    )

    # calculate voxel volume
    voxel_volume = image_nii.get_voxel_volume()
    print(
        f"11. get_voxel_volume executed successfully: voxel volume={voxel_volume} mm^3"
    )

    # check DicomImage attributes with DICOM image
    # get metadata attribute
    image_dcm = DicomImage(dcm_img, dcm_image.metadata, dcm_spacing)
    metadata = image_dcm.metadata
    print(
        f"12. saving metadata executed successfully: {metadata}"
    )

    print(
        "-- successfully completed testing of class attributes --"
    )

    print(
        f"-- ALL TESTS COMPLETED SUCCESFULLY (dont forget to delete the output files, {nii_path} and {nii_output_path})--"
    )
