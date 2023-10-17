from functools import reduce
import os
from typing import List

from utils.instagram import InstagramScraper, PostContent
from utils.json_storage import reload_data, write_data
from utils.paths import EXTERNAL_POSTS_DIR


def _download_external_posts(
    instagram_accounts: List[str],
    instagram_user: str,
    intagram_password: str,
    redownload: bool = True,
) -> List[PostContent]:
    """Download posts from other Instagram accounts, in order to look for additional related images"""
    external_posts = []
    for account in instagram_accounts:
        target_dir = f"{EXTERNAL_POSTS_DIR}/{account}"
        json_path = f"{target_dir}/{account}.json"
        account_posts = []
        # Posts that were already download
        if os.path.isfile(json_path):
            account_posts_data = reload_data(json_path)
            account_posts.extend(
                [PostContent.from_dict(post_data) for post_data in account_posts_data]
            )
        # New posts
        if redownload or not account_posts:
            print(f'Looking for new posts in the instagram page "{account}"')
            new_account_posts = InstagramScraper(
                instagram_user, intagram_password
            ).download_posts(
                account,
                target_dir,
                starting_date=(
                    max([post.date for post in account_posts])
                    if account_posts
                    else None
                ),
            )
            print(f"{len(new_account_posts)} posts were download from {account}")
            account_posts.extend(new_account_posts)
            account_posts_data = [post.to_dict() for post in account_posts]
            write_data(account_posts_data, json_path)
        external_posts.extend(account_posts)

    return external_posts


def find_images_in_external_posts(
    full_name: str,
    instagram_accounts: List[str],
    instagram_user: str,
    intagram_password: str,
    redownload: bool = True,
) -> List[str]:
    """Find posts with the given name and return list of all the images it contains"""
    external_posts = _download_external_posts(
        instagram_accounts, instagram_user, intagram_password, redownload
    )
    images_paths = reduce(
        lambda a, b: a + b,
        [post.images_paths for post in external_posts if full_name in post.text],
        [],
    )
    return images_paths
