import os
from typing import List
from utils.paths import EXTERNAL_IMAGES_DIR, is_image_file


def find_images_in_external_images_pool(full_name: str) -> List[str]:
    """Collect the paths of all the images in the pool matching the given name"""
    images_paths = []
    for file_name in os.listdir(EXTERNAL_IMAGES_DIR):
        file_path = os.path.join(os.getcwd(), EXTERNAL_IMAGES_DIR, file_name)
        if is_image_file(file_path) and full_name in file_name:
            images_paths.append(file_path)
    return images_paths
