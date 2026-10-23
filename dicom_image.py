from typing import Any

import numpy as np

from .image import Image


class DicomImage(Image):
    """An Image that also stores DICOM metadata.

    Inherits the class atributes from Image.

    Attributes:
        metadata: Dictionary mapping DICOM keywords to their values.
    """

    def __init__(self, data: np.ndarray, spacing: tuple[float, ...] | float | None = None, metadata: dict[str, Any] | None = None,) -> None:
        """Create a DicomImage.

        Args:
            data: The image pixel data.
            spacing: Spacing in mm per dimension, a single float used for all
                dimensions, or None for the default of 1.0 mm.
            metadata: Dictionary with DICOM attributes. If None, an empty
                dictionary is used.

        Raises:
            TypeError: If metadata is not a dictionary (or None).
            ValueError: If data and spacing are incompatible (see Image).
        """
        # Let the parent class validate and store data and spacing.
        super().__init__(data, spacing)

        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        self.metadata = metadata
