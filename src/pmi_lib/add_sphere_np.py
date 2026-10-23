
import numpy as np

from .classes import Image


def add_sphere_np(
    image: Image, radius: float, value: float = 1.0
) -> None:
    """Add value to all pixels inside a centered sphere using NumPy."""
    if image._data.ndim not in (1, 2, 3):
        raise ValueError("The image must be 1D, 2D, or 3D.")

    if radius < 0:
        raise ValueError("radius must be non-negative.")

    # Create a 3D view while keeping changes connected to the original data.
    if image._data.ndim == 1:
        data = image._data[None, None, :]
        spacing = (1.0, 1.0, image.spacing[0])
    elif image._data.ndim == 2:
        data = image._data[None, :, :]
        spacing = (1.0, image.spacing[0], image.spacing[1])
    else:
        data = image._data
        spacing = image.spacing

    center = [(size - 1) / 2 for size in data.shape]

    # Generate coordinate arrays without explicit Python loops.
    i, j, k = np.indices(data.shape)

    distance_squared = (
        ((i - center[0]) * spacing[0]) ** 2
        + ((j - center[1]) * spacing[1]) ** 2
        + ((k - center[2]) * spacing[2]) ** 2
    )

    # Add value only where the distance from the center is within the radius.
    data[distance_squared <= radius**2] += value
