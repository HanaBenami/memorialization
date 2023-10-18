import os


EXTERNAL_IMAGES_DIR = "external_images"
EXTERNAL_POSTS_DIR = "external_posts"
GENERATED_POSTS_DIR = "generated_posts"


def is_image_file(path: str) -> bool:
    """Checks whether the given path represent an existing image file"""
    return any(
        [
            path.lower().endswith(f".{suffix}")
            for suffix in ["jpg", "jpeg", "png", "bmp"]
        ]
    ) and os.path.isfile(path)
