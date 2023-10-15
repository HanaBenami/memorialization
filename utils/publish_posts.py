import os
import datetime
from collections import defaultdict
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
    ]
    if casualty.date_of_death:
        text.extend(
            [
                f"נפל{gender_suffix}",
                "בתאריך",
                f"{casualty.date_of_death_en},",
            ]
        )
    if casualty.grave_city:
        text.extend(
            [
                f"מקום מנוחת{gender_suffix or 'ו'}",
                f"{casualty.grave_city},",
            ]
        )
    text.extend(
        [
            f"הותיר{gender_suffix}",
            f"אחרי{gender_suffix or 'ו'}",
            "חלל מלא בזכרונות! 🕯️",
        ]
    )
    return " ".join(text)


def _prepare_post_hashtags(casualty: Casualty) -> str:
    """Prepare to text description for the given casualty post"""
    hashtags = [
        casualty.full_name.replace(" ", ""),
        "לזכרם",
        "חרבותברזל",
        "יוםהזיכרון",
        "יוםהזכרוןהתשפד",
        "יוםהזיכרון2023",
        "חללזכרונות",
        "lezichram",
        "YomHazikaron",
        "lsraelRemembers",
        "memorialday",
        "standwithisrael",
    ]
    return " ".join([f"#{hashtag}" for hashtag in hashtags])


def _publish_casualties_post(casualty: Casualty, instagram_client: Client) -> Casualty:
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
                    path for path in casualty.post_images[1:] if os.path.isfile(path)
                )

                publish_post(post_cation, post_images_paths, instagram_client)
                print(f"The post about {casualty} was published successfully.")
                casualty.post_published = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            else:
                print(f"No post to publish for {casualty}")

    except Exception as e:
        print(f"\nCouldn't publish the post for {casualty}:\n{e}\n\nGoing to stop...")
        STOP_PUBLISHING = True

    return casualty


def publish_casualties_posts(
    given_casualties_data: List[dict],
    instagram_user: str,
    intagram_password: str,
    posts_limit: int,
    min_images: int,
) -> List[dict]:
    """Publish posts about all the casualties, one per each"""

    updated_casualties_data = []
    instagram_client = init_instagram_client(instagram_user, intagram_password)
    posts = 0
    images_per_posts = defaultdict(lambda: 0)

    for casualty_data in given_casualties_data:
        casualty: Casualty = Casualty.from_dict(casualty_data)
        if not casualty.post_published:
            if min_images and len(casualty.post_images) < min_images:
                print(
                    f"Not enough images - the post about {casualty} won't be published."
                )
            else:
                casualty = _publish_casualties_post(
                    casualty,
                    instagram_client=instagram_client,
                )
                posts += 1
                images_per_posts[len(casualty.post_images)] += 1

        updated_casualties_data.append(casualty.to_dict())
        if posts_limit == posts:
            break

    print(f"{posts} posts were published. Number of images in exah posts:")
    print(
        "\n".join(
            f"{images}: {posts} posts" for images, posts in images_per_posts.items()
        )
    )

    return updated_casualties_data
