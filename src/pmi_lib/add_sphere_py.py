from .classes import Image

def add_sphere_py(image: Image, radius: float, value: float = 1.0) -> None:
"""

"""
    # Making the image 3D for the 2D images
    data = image._data
    if data.ndim == 2:
        data = data[None, :, :]

    # Determine the middle point of the image
    center = [(size - 1) / 2 for size in data.shape]

    # Loop through all the voxels of the 3D image
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            for k in range(data.shape[2]):
                # Compute the distance to the middle point in mm
                distance = (
                    ((i - center[0]) * image.spacing[0]) ** 2
                    + ((j - center[1]) * image.spacing[1]) ** 2
                    + ((k - center[2]) * image.spacing[2]) ** 2
                ) ** 0.5

                # Add the value when the voxel lays inside the sphere's radius
                if distance <= radius:
                    data[i, j, k] += value
