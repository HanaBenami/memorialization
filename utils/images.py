from typing import List, Sequence, Tuple
from PIL import Image
import imagehash
import cv2
import cv2.typing


def detect_faces(image_path: str) -> Sequence[cv2.typing.Rect]:
    """
    Trys to deteced faces in the image
    """
    faces = []
    for xml in [
        "opencv_frontalface_detection",
        "haarcascade_frontalface_default",
        "haarcascade_frontalface_alt",
        "haarcascade_frontalface_alt2",
        "haarcascade_frontalface_alt_tree",
        "haarcascade_profileface_detection",
        "haarcascade_mcs_eyepair_big",
        "haarcascade_mcs_eyepair_small",
        "haarcascade_smile",
        "haarcascade_mcs_nose",
        "haarcascade_mcs_mouth",
    ]:
        face_cascade = cv2.CascadeClassifier(f"utils/face_detection/{xml}.xml")
        faces = face_cascade.detectMultiScale(cv2.imread(image_path), 1.1, 4)
        if len(faces) == 1:
            break
    return faces


def convert_to_rgb(img: Image) -> Image:
    """
    Convert the image to RGB mode
    """
    if img.mode in ["RGBA", "P"]:
        img = img.convert("RGB")
    return img


def cut_face(image_path: str, margin: float = 0.1) -> Image:
    """
    Return an image with only the first detected face.
    """
    faces = detect_faces(image_path)
    if 0 < len(faces):
        img = Image.open(image_path)
        img = convert_to_rgb(img)
        face_left, face_top, face_width, face_hieght = faces[0]
        margin_x, margin_y = face_width * margin, face_hieght * margin
        face_left, face_top, face_right, face_botton = (
            face_left - margin_x,
            face_top - margin_y,
            face_left + face_width + margin_x,
            face_top + face_hieght + margin_y,
        )
        return img.crop((face_left, face_top, face_right, face_botton))


def square_crop_coordinations(
    img: Image, face: cv2.typing.Rect, new_size: int
) -> cv2.typing.Rect:
    """
    Returns the crop coordinations required in order to make the image a square,
    without resizing it, with the face (or any other fiven rectangle) in the middle, if possible
    """
    face_left, face_top, face_width, face_hieght = face
    face_center_x, face_center_y = (
        face_left + face_width / 2,
        face_top + face_hieght / 2,
    )
    left, top, right, bottom = (
        face_center_x - new_size / 2,
        face_center_y - new_size / 2,
        face_center_x + new_size / 2,
        face_center_y + new_size / 2,
    )
    if left < 0:
        right -= left
        left = 0
    if img.width < right:
        left -= right - img.width
        right = img.width
    if top < 0:
        bottom -= top
        top = 0
    if img.width < right:
        top -= bottom - img.width
        bottom = img.width
    return (left, top, right, bottom)


def resize(img: Image, new_width: int) -> Image:
    """
    Resize the image while keeping in proportions
    """
    return img.resize((new_width, round(img.height * new_width / img.width)))


def is_duplication(img1_path: str, img2_path: str) -> bool:
    """Determine if the images were originally the same, ignoring their size, resolution and crop"""
    faces = [cut_face(img_path) for img_path in (img1_path, img2_path)]
    if all(faces):
        width = min([face.width for face in faces])
        faces = [resize(face, width) for face in faces]
        hashes = [imagehash.average_hash(face) for face in faces]
        hash_diff = abs(hashes[0] - hashes[1])
        return hash_diff < 10


def remove_duplicates_images(images_paths: List[str]) -> Tuple[List[str], List[str]]:
    """
    Check for similarity among the images and return list of unique images only.
    Return values:
    - List of unique images
    - List of removed images
    """
    if not images_paths:
        return [], []
    unique_images, removed = [images_paths[0]], []
    for i, current_image_path in enumerate(images_paths[1:]):
        similar = False
        for previous_image_path in images_paths[: i + 1]:
            if is_duplication(current_image_path, previous_image_path):
                similar = True
        if not similar:
            unique_images.append(current_image_path)
        else:
            removed.append(current_image_path)
    return unique_images, removed
