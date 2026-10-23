
from .classes import Image


def add_sphere_py(
    image: Image, radius: float, value: float = 1.0
) -> None:
    """Add value to all pixels inside a centered sphere."""
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

    # Iterate over every voxel using for-loops.
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            for k in range(data.shape[2]):
                distance_squared = (
                    ((i - center[0]) * spacing[0]) ** 2
                    + ((j - center[1]) * spacing[1]) ** 2
                    + ((k - center[2]) * spacing[2]) ** 2
                )

                if distance_squared <= radius**2:
                    data[i, j, k] += value
