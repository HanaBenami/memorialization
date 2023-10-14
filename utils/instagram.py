import time
import os
from pathlib import Path
from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from instagrapi import Client
from instagrapi.types import Media
from instaloader import ConnectionException, Instaloader, Profile
from instaloader.structures import Post


@dataclass_json
@dataclass
class PostContent:
    """Represention of a single Instagram post -"""

    text: str
    images_paths: List[str]


def init_instagram_loader() -> Instaloader:
    """Init an Instagram loader object"""
    return Instaloader()


def download_post(post: Post, target_dir: str, loader: Instaloader) -> PostContent:
    """Download a single Instagram post and return its text and its images paths"""
    loader.download_post(post, target_dir)
    text, images_paths = "", []
    for file_name in os.listdir(target_dir):
        file_path = os.path.join(os.getcwd(), target_dir, file_name)
        if file_name.endswith(".txt"):
            with open(file_path) as fp:
                text = fp.read()
        elif any(
            [
                file_name.endswith(f".{suffix}")
                for suffix in ["jpg", "jpeg", "png", "bmp"]
            ]
        ):
            images_paths.append(file_path)
    return PostContent(text=text, images_paths=images_paths)


def download_posts(account: str, target_dir: str) -> List[PostContent]:
    """Download all the post from the given Instagram account"""
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    wd = os.getcwd()
    os.chdir(target_dir)

    loader = init_instagram_loader()
    profile = Profile.from_username(loader.context, account)
    posts = []
    for i, post in enumerate(profile.get_posts()):
        for _ in range(2):
            try:
                target_sub_dir = f"{account}_{i}"
                posts.append(download_post(post, target_sub_dir, loader))
                time.sleep(2)
                break
            except ConnectionException:
                loader = init_instagram_loader()
    os.chdir(wd)
    return posts


def init_instagram_client(instagram_user: str, intagram_password: str) -> Client:
    """Init an Instagram client object"""
    instagram_client = Client()
    instagram_client.login(instagram_user, intagram_password)
    return instagram_client


def publish_post(
    post_cation: str, post_images_paths: List[str], instagram_client: Client
) -> Media:
    """Publish an Instagram post"""
    print(f"\nGoing to publish a post:\n{post_cation}\n{post_images_paths}")
    return instagram_client.album_upload(post_images_paths, caption=post_cation)
