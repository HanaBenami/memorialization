import os
from typing import List
from utils.paths import EXTERNAL_IMAGES_DIR, is_image_file


def find_images_in_external_images_pool(
    full_name: str, path: str = os.path.join(os.getcwd(), EXTERNAL_IMAGES_DIR)
) -> List[str]:
    """Collect the paths of all the images in the pool matching the given name"""
    images_paths = []
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if is_image_file(file_path) and full_name in file_name:
            images_paths.append(file_path)
        elif os.path.isdir(file_path):
            images_paths.extend(
                find_images_in_external_images_pool(full_name, file_path)
            )
    return images_paths
