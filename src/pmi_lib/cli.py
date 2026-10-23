import click
import numpy as np

from .classes import Image
from .io import read_dicom, write_nifti


@click.command()
@click.argument(
    "dicom_path", type=click.Path(exists=True, file_okay=True), required=True
)
@click.argument("nifti_path", required=True)
def dicom_to_nifti(dicom_path: str, nifti_path: str) -> None:
    """
    Convert a DICOM file or directory to a NIfTI file.

    :param dicom_path: path to the DICOM file or directory
    :param nifti_path: path to the output NIfTI file
    """
    # don't bother CLI users with python exceptions
    try:
        dcm_image = read_dicom(dicom_path)
        dcm_img = dcm_image._data
        spacing = dcm_image.spacing
    except (FileNotFoundError, ValueError) as error:
        raise click.ClickException(error)
    except Exception:  # noqa: BLE001
        raise click.ClickException(
            "An unexpected error occurred while reading the DICOM input."
        )

    try:
        # convert from LPS to RAS orientation (mirror Y and X) and from row-major (ZYX) to column-major (XYZ) order
        data = np.flip(dcm_img, (-1, -2))
        nii_img = np.transpose(data)
    except Exception:  # noqa: BLE001
        raise click.ClickException(
            "An unexpected error occurred while converting the DICOM input."
        )

    try:
        write_nifti(Image(nii_img, spacing), nifti_path)
    except ValueError as error:
        raise click.ClickException(error)
    except Exception:  # noqa: BLE001
        raise click.ClickException(
            "An unexpected error occurred while writing the NIfTI output."
        )
