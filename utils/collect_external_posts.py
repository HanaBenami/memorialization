from functools import reduce
import os
from typing import List

from utils.instagram import InstagramScraper, PostContent
from utils.json_storage import reload_data, write_data
from utils.paths import EXTERNAL_POSTS_DIR


def _download_external_posts(instagram_accounts: List[str]) -> List[PostContent]:
    """Download posts from other Instagram accounts, in order to look for additional related images"""
    external_posts = []
    for account in instagram_accounts:
        target_dir = f"{EXTERNAL_POSTS_DIR}/{account}"
        json_path = f"{target_dir}/{account}.json"
        if os.path.isfile(json_path):
            account_external_posts_data = reload_data(json_path)
            account_external_posts = [
                PostContent.from_dict(post_data)
                for post_data in account_external_posts_data
            ]
            external_posts.extend(account_external_posts)
        else:
            account_external_posts = InstagramScraper().download_posts(
                account, target_dir
            )
            account_external_posts_data = [
                post.to_dict() for post in account_external_posts
            ]
            write_data(account_external_posts_data, json_path)
            external_posts.extend(account_external_posts)
    return external_posts


def find_images_in_external_posts(
    full_name: str, instagram_accounts: List[str]
) -> List[str]:
    """Find posts with the given name and return list of all the images it contains"""
    external_posts = _download_external_posts(instagram_accounts)
    images_paths = reduce(
        lambda a, b: a + b,
        [post.images_paths for post in external_posts if full_name in post.text],
        [],
    )
    return images_paths
