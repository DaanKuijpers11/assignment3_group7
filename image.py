import numpy as np
import warnings
from typing import Any

class Image:
    """Represent an N-dimensional image and its physical spacing.
    """
    def __init__(self, data: np.ndarray, spacing:tuple[float, ...] | None = None) -> None:
        """Initialize an image with pixel data and optional spacing.

        Args:
            data: NumPy array containing the image data.
            spacing: Physical spacing in millimeters for each dimension.
                If omitted, a spacing of 1.0 mm is used for every dimension.

        Raises:
            TypeError: If data is not a NumPy array or spacing is not
                a tuple of numeric values.
            ValueError: If the number of spacing values does not match
                the number of image dimensions.
        """
        if spacing is None:
            # Use unit spacing when no physical spacing is provided.
            warnings.warn("spacing is not specified. Using default spacing.", UserWarning)
            spacing = (1.0,) * data.ndim
            
        if not isinstance(data, np.ndarray):
            raise TypeError("data must be NumPy array.")
        
        if not isinstance(spacing, tuple) or not all(
        isinstance(x, float) for x in spacing):           
            raise TypeError("spacing must be tuple of floats.")
        
        if data.ndim not in (2, 3):
            raise ValueError("Image should have 2 or 3 dimensions.")

        # Each image dimension must have a corresponding spacing value.
        if len(spacing) != data.ndim:
            raise ValueError("Image and spacing dimensions must be the same.")
        
        self._data = data
        self.spacing = spacing
    
    
    def __repr__(self) -> str:
        """Return a readable description of the image.
        """
        return f"A {self._data.dtype} image with shape {self._data.shape} and a spacing of {self.spacing} mm."
    
    
    def get_pixel_area(self) -> float:
        """Calculate the area of a pixel in mm².

        Returns:
            The product of the first two spacing values.

        Raises:
            ValueError: If the image does not have two dimensions.
        """
        if self._data.ndim != 2:
            raise ValueError("Image dimensionality is insufficient for the requested calculation. It should be 2D.")
        return self.spacing[0] * self.spacing[1]

    def get_voxel_volume(self) -> float:
        """Calculate the volume of a voxel in mm³.

        Returns:
            The product of the first three spacing values.

        Raises:
            ValueError: If the image does not have three dimensions.
        """
        if self._data.ndim != 3:
            raise ValueError("Image dimensionality is insufficient for the requested calculation. It should be 3D.")
        return self.spacing[0] * self.spacing[1] * self.spacing[2]
    
    
    def __len__(self) -> int:
        # Allow len(image) to return the size of the outer dimension.
        return len(self._data) 
    
    
    def __array__(
        self,
        dtype: np.typing.DTypeLike | None = None,
        *,
        copy: bool | None = None
    ) -> np.ndarray:
        # Allow NumPy to convert the Image object into an array,
        # optionally converting its data type or making a copy.
        if copy is None:
            copy = False

        if dtype is None:
            dtype = self._data.dtype

        return self._data.astype(dtype, copy=copy)
        
        
    def __getitem__(self, key: Any) -> np.ndarray:
        # Allow the image to be indexed or sliced like a NumPy array.
        return self._data[key]