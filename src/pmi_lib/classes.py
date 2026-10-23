from numbers import Real
from typing import Any

import numpy as np


class Image:
    def __init__(
        self, data: np.ndarray, spacing: tuple[float, ...] | None = None
    ) -> None:
        """
        Initialize an Image object.
        :param data: The image data as a numpy array.
        :param spacing: The spacing of the image in each dimension. Default is None, which will be set to 1.0 for each dimension.
        """
        if type(data) is not np.ndarray:
            raise TypeError(
                f"Data must be a numpy array, got {type(data).__name__} instead."
            )
        if spacing is not None and not isinstance(spacing, tuple):
            raise TypeError(
                f"Spacing must be a tuple or None, got {type(spacing).__name__} instead."
            )

        # default spacing to 1.0 for each dimension if not provided
        if spacing is None:
            spacing = (1.0,) * data.ndim
        # check if all elements of spacing are numeric (int or float, not boolean)
        elif any(
            isinstance(value, bool) or not isinstance(value, Real) for value in spacing
        ):
            raise TypeError("All elements of spacing must be numeric.")
        # convert spacing values to a tuple of floats
        else:
            spacing = tuple(float(value) for value in spacing)

        if data.ndim != len(spacing):
            raise ValueError(
                f"Data dimensions {data.ndim} do not match spacing dimensions {len(spacing)}."
            )

        self._data = data
        self.spacing = spacing

    def __repr__(self) -> str:
        """
        Return a string representation of the Image object.
        """
        return f"A {self._data.dtype} image with shape {self._data.shape} and a spacing of {self.spacing} mm."

    def __len__(self) -> int:
        """
        Return the length of the outer dimension of the image data (number of slices).
        """
        # allow len(image) to match the outer data dimension
        return self._data.shape[0]

    def __array__(
        self, dtype: np.typing.DTypeLike | None = None, *, copy: bool | None = None
    ) -> np.ndarray:
        """
        Return the image data as a numpy array, optionally converting to a specified dtype.
        """
        # if dtype and copy are both None, return self.data directly
        if dtype is None and copy is None:
            return self._data
        # if copy is None, let NumPy use its default for copy
        elif copy is None:
            return self._data.astype(dtype)
        # if dtype is None, return a copy of the data with the same dtype
        elif dtype is None:
            return self._data.astype(self._data.dtype, copy=copy)

        # let NumPy convert the image while respecting dtype and copy options
        return self._data.astype(dtype, copy=copy)

    def __getitem__(self, key: Any) -> np.ndarray:
        """
        Return the image data at the specified index.
        """
        # forward indexing operations directly to the underlying data
        return self._data[key]

    def get_pixel_area(self) -> float:
        """
        Calculate the pixel area for 2D images.
        """
        if self._data.ndim < 2:
            raise ValueError("Data must be at least 2D to calculate pixel area.")

        return self.spacing[0] * self.spacing[1]

    def get_voxel_volume(self) -> float:
        """
        Calculate the voxel volume for 3D images.
        """
        if self._data.ndim < 3:
            raise ValueError("Data must be at least 3D to calculate voxel volume.")
        else:
            return self.spacing[0] * self.spacing[1] * self.spacing[2]


class DicomImage(Image):
    def __init__(
        self,
        data: np.ndarray,
        metadata: dict[str, Any],
        spacing: tuple[float, ...] | None = None,
    ) -> None:
        """
        Initialize a DicomImage object.
        :param data: The image data as a numpy array.
        :param metadata: The metadata of the DICOM image.
        :param spacing: The spacing of the image in each dimension. Default is None, which will be set to 1.0 for each dimension.
        """
        super().__init__(data, spacing)

        if type(metadata) is not dict:
            raise TypeError(
                f"Metadata must be a dictionary, got {type(metadata).__name__} instead."
            )

        self.metadata = metadata
