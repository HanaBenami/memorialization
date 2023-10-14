import os
import datetime
from typing import List
from functools import reduce
from instagrapi import Client

from utils.casualty import Casualty, Gender
from utils.json_storage import reload_data, write_data
from utils.paths import *
from utils.instagram import (
    init_instagram_client,
    publish_post,
    download_posts,
    PostContent,
)


STOP_PUBLISHING = False


def _prepare_post_text(casualty: Casualty) -> str:
    """Prepare to text description for the given casualty post"""
    gender_suffix = "ה" if casualty.gender == Gender.FEMALE else ""
    text = [
        casualty.full_name,
        'ז"ל,',
        casualty.degree,
        f"ב{casualty.department}",
        ", ",
        f"נפל{gender_suffix}",
        "בתאריך",
        f"{casualty.date_of_death_en},",
        f"מקום מנוחת{gender_suffix or 'ו'}",
        f"{casualty.grave_city},",
        f"הותיר{gender_suffix}",
        f"אחרי{gender_suffix or 'ו'}",
        "חיים שלמים וזכרונות! 🕯️",
    ]
    return " ".join(text)


def _prepare_post_hashtags(casualty: Casualty) -> str:
    """Prepare to text description for the given casualty post"""
    hashtags = [
        casualty.full_name.replace(" ", ""),
        "לזכרם",
        "חרבותברזל",
        "יוםהזיכרון",
        "יוםהזכרוןהתשפד",
        "יוםהזיכרון2024",
        "חללזכרונות",
        "lezichram",
        "YomHazikaron",
        "lsraelRemembers",
        "memorialday",
    ]
    return " ".join([f"#{hashtag}" for hashtag in hashtags])


def _publish_casualties_post(
    casualty: Casualty, additional_images_paths: List[str], instagram_client: Client
) -> Casualty:
    """Publish a post about the casualty"""
    global STOP_PUBLISHING
    try:
        if not STOP_PUBLISHING:
            if casualty.post_path:
                post_text = _prepare_post_text(casualty)
                post_hashtags = _prepare_post_hashtags(casualty)
                post_cation = f"{post_text}\n{post_hashtags}"
                casualty.post_caption = post_cation

                post_images_paths = [
                    casualty.post_path,
                ]
                post_images_paths.extend(
                    [path for path in additional_images_paths if os.path.isfile(path)]
                )
                casualty.post_images = additional_images_paths

                print(publish_post(post_cation, post_images_paths, instagram_client))
                print(f"The post was published successfully.")
                casualty.post_published = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            else:
                print(f"No post to publish for {casualty}")

    except Exception as e:
        print(f"\nCouldn't publish the post for {casualty}:\n{e}\n\nGoing to stop...")
        STOP_PUBLISHING = True

    return casualty


def _download_external_posts() -> List[PostContent]:
    """Download posts from other Instagram accounts, in order to look for additional related images"""
    external_accounts = ["remember_haravot_barzel"]
    external_posts = []
    for account in external_accounts:
        target_dir = f"external_posts/{account}"
        json_path = f"{target_dir}/{account}.json"
        if os.path.isfile(json_path):
            account_external_posts_data = reload_data(json_path)
            account_external_posts = [
                PostContent.from_dict(post_data)
                for post_data in account_external_posts_data
            ]
            external_posts.extend(account_external_posts)
        else:
            account_external_posts = download_posts(account, target_dir)
            account_external_posts_data = [
                post.to_dict() for post in account_external_posts
            ]
            write_data(account_external_posts_data, json_path)
            external_posts.extend(account_external_posts)
    return external_posts


def publish_casualties_posts(
    casualties_data: List[dict],
    instagram_user: str,
    intagram_password: str,
    posts_limit: int,
) -> List[dict]:
    """Publish posts about all the casualties, one per each"""

    external_posts = _download_external_posts()

    instagram_client = init_instagram_client(instagram_user, intagram_password)

    posts, posts_with_additional_images = 0, 0

    for i, casualty_data in enumerate(casualties_data):
        casualty = Casualty.from_dict(casualty_data)
        if not casualty.post_published:
            # Look for additional images
            additional_images_paths = reduce(
                lambda a, b: a + b,
                [
                    post.images_paths
                    for post in external_posts
                    if casualty.full_name in post.text
                ],
                [],
            )

            # Publish the post
            casualty = _publish_casualties_post(
                casualty,
                additional_images_paths=additional_images_paths,
                instagram_client=instagram_client,
            )

            posts += 1
            if additional_images_paths:
                posts_with_additional_images += 1

            if posts_limit and casualty.post_published:
                posts_limit -= 1
                if posts_limit == 0:
                    break

        casualties_data[i] = casualty.to_dict()

    print(
        f"""
        {posts} were published.
        {posts_with_additional_images} posts includes additional images.
    """
    )

    return casualties_data
