import time
import os
import random
import instagrapi
import instagrapi.types
import instagrapi.exceptions
import instaloader
import instaloader.structures
from pathlib import Path
from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from singleton_decorator import singleton

from utils.paths import is_image_file


@dataclass_json
@dataclass
class PostContent:
    """Represention of a single Instagram post -"""

    text: str
    images_paths: List[str]


@singleton
class InstagramScraper:
    """Instagram scraper for downloading posts from public accounts"""

    def __init__(self) -> None:
        self.loader = instaloader.Instaloader()

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
        return PostContent(text=text, images_paths=images_paths)

    def download_posts(self, account: str, target_dir: str) -> List[PostContent]:
        """Download all the post from the given Instagram account"""
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        wd = os.getcwd()
        os.chdir(target_dir)

        profile = instaloader.Profile.from_username(self.loader.context, account)
        posts = []
        for i, post in enumerate(profile.get_posts()):
            for _ in range(2):
                try:
                    target_sub_dir = f"{account}_{i}"
                    posts.append(self._download_post(post, target_sub_dir))
                    time.sleep(1)
                    break
                except instaloader.ConnectionException:
                    pass  # try again
        os.chdir(wd)
        return posts


@singleton
class InstagramClient:
    """Instagram client for publishing posts to the user account"""

    class LoginException(Exception):
        """Login related exception"""

    SESSION_FILE = "instagram_session.json"

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
                    self.SESSION_FILE
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
                self.instagram_client.dump_settings(self.SESSION_FILE)

    def _login(self) -> None:
        self.instagram_client.login(self.instagram_user, self.intagram_password)

    def _is_logged_in(self) -> bool:
        try:
            self.instagram_client.get_timeline_feed()
            return True
        except instagrapi.exceptions.LoginRequired:
            return False

    def publish_post(
        self, post_cation: str, post_images_paths: List[str]
    ) -> instagrapi.types.Media:
        """Publish an Instagram post"""
        print(f"\nGoing to publish a post:\n{post_cation}\n{post_images_paths}")
        self._init_instagram_session()
        sleep_seconds = random.randint(1 * 60, 3 * 60)
        print(f"Going to sleep for {sleep_seconds} seconds before publishing...")
        time.sleep(sleep_seconds)  # Wait 1 to 3 minutes between posts
        return (
            self.instagram_client.album_upload(post_images_paths, caption=post_cation)
            if 1 < len(post_images_paths)
            else self.instagram_client.photo_upload(
                post_images_paths[0], caption=post_cation
            )
        )
