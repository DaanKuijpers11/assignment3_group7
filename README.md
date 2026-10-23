# PMI Library - Group 5

`pmi-lib` is a Python library for reading medical images, converting DICOM
data to NIfTI, and applying Gaussian filtering inside a boolean mask.

The library uses NumPy arrays internally and stores image data together with
voxel spacing in `Image` objects. DICOM images are represented by
`DicomImage`, which also contains the image metadata.

## Functions

- Read a single DICOM file or a directory containing one DICOM series.
- Read a NIfTI file.
- Write a NIfTI file.
- Convert DICOM files or directories to NIfTI (from the command line).
- Apply a Gaussian filter (inside a boolean mask).
- Test the full pipeline.
- Calculate pixel areas and voxel volumes from image spacing.

When a DICOM directory is read, its slices are checked for a matching series,
sorted by spatial position, and combined into one image. Pixel values are
rescaled using the DICOM metadata. DICOM-to-NIfTI conversion changes the
orientation from LPS to RAS and the array order from ZYX to XYZ.

## Requirements

- Python 3.14 (or newer)
- NumPy
- SciPy
- pydicom
- NiBabel
- Click

## Installation

From the project directory, install the package:

```bash
python -m pip install -e .
```

This installs the `pmi_lib` package and the `dicom-to-nifti` command-line
executable. You can then convert DICOM images into NIfTI images from your
terminal.

## Command-line usage

Convert a DICOM file or directory to a NIfTI file:

```bash
dicom-to-nifti path/to/input.dcm path/to/output.nii.gz
```

The input may also be a directory containing DICOM slices:

```bash
dicom-to-nifti path/to/dicom_directory path/to/output.nii.gz
```

Use the help option to see the command arguments:

```bash
dicom-to-nifti --help
```

The command reports input, conversion, and output errors as readable Click
errors. The output path may use any filename supported by NiBabel, including
`.nii` and `.nii.gz`.

## Pipeline test

The package exposes a small pipeline test that reads DICOM data, converts it
to NIfTI, reads the result, and applies the masked Gaussian filter:

```python
from pmi_lib import test

test("path/to/dicom_file_or_directory")
```

This creates `test_output.nii.gz` in the current directory. Remove that file
after the check if it is no longer needed.

## Folder structure

```text
PMI-assignment-2/
├── src/
│   └── pmi_lib/
│       ├── __init__.py
│       ├── classes.py
│       ├── cli.py
│       ├── io.py
│       ├── processing.py
│       └── testing.py
├── pyproject.toml
├── README.md
├── setup.py
├── MANIFEST.in
└── LICENSE.md
```
