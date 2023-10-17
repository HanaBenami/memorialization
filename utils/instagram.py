from datetime import datetime
from re import S
import time
import os
import random
import instagrapi
import instagrapi.types
import instagrapi.exceptions
import instaloader
import instaloader.structures
import cv2
from pathlib import Path
from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from singleton_decorator import singleton
from PIL import Image

from utils.paths import is_image_file


@dataclass_json
@dataclass
class PostContent:
    """Represention of a single Instagram post -"""

    DATETIME_FORMAT = "%Y%m%d_%H%M%S"

    text: str
    images_paths: List[str]
    date_str: str

    @property
    def date(self):
        return datetime.strptime(self.date_str, self.DATETIME_FORMAT)


def _random_sleep(max_minutes: float):
    """Random sleep for up to <max_minutes> minutes"""
    sleep_seconds = random.randint(0, round(max_minutes * 60))
    print(f"Going to sleep for {sleep_seconds} seconds before publishing...")
    time.sleep(sleep_seconds)


@singleton
class InstagramScraper:
    """Instagram scraper for downloading posts from public accounts"""

    def __init__(self, instagram_user: str, intagram_password: str) -> None:
        self.loader = instaloader.Instaloader()
        self.loader.login(instagram_user, intagram_password)

    def _download_post(
        self, post: instaloader.structures.Post, target_dir: str
    ) -> PostContent:
        """Download a single Instagram post and return its text and its images paths"""
        self.loader.download_post(post, target_dir)
        text, images_paths = "", []
        for file_name in os.listdir(target_dir):
            file_path = os.path.join(os.getcwd(), target_dir, file_name)
            if file_name.endswith(".txt"):
                with open(file_path) as fp:
                    text = fp.read()
            elif is_image_file(file_path):
                images_paths.append(file_path)
        return PostContent(
            text=text,
            images_paths=images_paths,
            date_str=post.date.strftime(PostContent.DATETIME_FORMAT),
        )

    def download_posts(
        self, account: str, target_dir: str, starting_date: datetime | None = None
    ) -> List[PostContent]:
        """Download all the post from the given Instagram account"""
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        wd = os.getcwd()
        os.chdir(target_dir)
        profile = instaloader.Profile.from_username(self.loader.context, account)
        page_posts = profile.get_posts()
        downloaded_posts = []
        for post in page_posts:
            if not starting_date or starting_date < post.date:
                timestamp = post.date.strftime(PostContent.DATETIME_FORMAT)
                target_sub_dir = f"{account}_{timestamp}"
                downloaded_posts.append(self._download_post(post, target_sub_dir))
                _random_sleep(0.1)
        os.chdir(wd)
        return downloaded_posts


@singleton
class InstagramClient:
    """Instagram client for publishing posts to the user account"""

    class LoginException(Exception):
        """Login related exception"""

    def __init__(self, instagram_user: str, intagram_password: str) -> None:
        self.instagram_user = instagram_user
        self.intagram_password = intagram_password
        self.instagram_client = instagrapi.Client()
        self.instagram_session = None
        self._init_instagram_client()

    def _init_instagram_client(self) -> None:
        """Init an Instagram client object"""
        self.instagram_client.delay_range = [1, 3]

    def _init_instagram_session(self) -> None:
        """Init an Instagram session"""
        if not self._is_logged_in():
            try:
                self.instagram_session = self.instagram_client.load_settings(
                    self._session_file_name
                )
                if self.instagram_session:
                    self.instagram_client.set_settings(self.instagram_session)
                    self._login()
                    if not self._is_logged_in():
                        old_instagram_session = self.instagram_client.get_settings()
                        self.instagram_client.set_settings({})
                        self.instagram_client.set_uuids(old_instagram_session["uuids"])
                        raise self.LoginException(
                            "Couldn't logged in using session information"
                        )
                    else:
                        print("\nLogged in to Instagram using session information\n")
                else:
                    raise self.LoginException(
                        "No previous session information is avilable"
                    )

            except Exception:
                self._login()
                if not self._is_logged_in():
                    raise self.LoginException(
                        "Couldn't logged in using username and password"
                    )
                else:
                    print("\nLogged in to Instagram using username and password\n")

            finally:
                self.instagram_client.dump_settings(self._session_file_name)

    def _login(self) -> None:
        self.instagram_client.login(self.instagram_user, self.intagram_password)

    def _is_logged_in(self) -> bool:
        try:
            self.instagram_client.get_timeline_feed()
            return True
        except instagrapi.exceptions.LoginRequired:
            return False

    @property
    def _session_file_name(self) -> str:
        return f"instagram_session_{self.instagram_user}.json"

    @staticmethod
    def prepare_image_for_instagram(path: str) -> str:
        """Modify the image to make it ready for Instagram standard"""
        img = Image.open(path)
        # RGB
        if img.mode == "RGBA":
            img = img.convert("RGB")
        # Aspect ratio
        if img.height != img.width:
            new_size = min(img.height, img.width)
            # Face recognition in order to center the image around the face
            face_cascade = cv2.CascadeClassifier(
                "utils/opencv_frontalface_detection.xml"
            )
            faces = face_cascade.detectMultiScale(cv2.imread(path), 1.1, 4)
            if len(faces) == 1:
                face_left, face_top, face_width, face_hieght = faces[0]
                face_center_x, face_center_y = (
                    face_left + face_width / 2,
                    face_top + face_hieght / 2,
                )
                left, top = face_center_x - new_size / 2, face_center_y - new_size / 2
                left = 0 if left < 0 else left
                top = 0 if top < 0 else top
            else:
                left, top = 0, 0
            img = img.crop((left, top, new_size, new_size))
        # Save
        new_path = f"{path}.jpg"
        img.save(new_path)
        return new_path

    def publish_post(
        self, post_cation: str, post_images_paths: List[str]
    ) -> instagrapi.types.Media:
        """Publish an Instagram post"""
        print(f"\nGoing to publish a post:\n{post_cation}\n{post_images_paths}")
        post_images_paths = [
            self.prepare_image_for_instagram(path) for path in post_images_paths
        ]
        _random_sleep(2)
        self._init_instagram_session()
        published = (
            self.instagram_client.album_upload(post_images_paths, caption=post_cation)
            if 1 < len(post_images_paths)
            else self.instagram_client.photo_upload(
                post_images_paths[0], caption=post_cation
            )
        )
        for path in post_images_paths:
            os.remove(path)
        return published
