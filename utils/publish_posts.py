import os
import datetime
from collections import defaultdict
from typing import List, Tuple
from functools import reduce
import signal
from instagrapi.utils import string

from utils.casualty import Casualty, Gender
from utils.instagram import InstagramClient
from utils.paths import *
from utils.instagram import InstagramClient


STOP_PUBLISHING = False


def signal_handler(_sig, _frame):
    """Signal handler for stopping publishment in the middle, without losing data"""
    global STOP_PUBLISHING
    print("A signal was recieved - Going to stop publishing posts...")
    STOP_PUBLISHING = True


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
    spaces = "\n".join([".", "", ".", "", ".", "", ".", "", ""])

    hashtags = [
        casualty.full_name.replace(" ", ""),
        "לזכרם",
        "חרבותברזל",
        "נופליחרבותברזל",
        "haravotbarzel",
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
    hashtags = " ".join([f"#{hashtag}" for hashtag in hashtags])

    return f"{spaces}\n{hashtags}"


def _publish_casualty_post(
    casualty: Casualty, instagram_client: InstagramClient, test: bool
) -> Tuple[Casualty, bool]:
    """Publish a post about the casualty"""
    global STOP_PUBLISHING
    published = None
    try:
        if not STOP_PUBLISHING:
            if casualty.post_path:
                post_text = _prepare_post_text(casualty)
                post_hashtags = _prepare_post_hashtags(casualty)
                post_cation = f"{post_text}\n{post_hashtags}"
                casualty.post_caption = post_cation
                published = instagram_client.publish_post(
                    post_cation, casualty.post_path, casualty.post_additional_images
                )
                if published:
                    print(f"The post about {casualty} was published successfully.")
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if test:
                        casualty.post_tested = timestamp
                    else:
                        casualty.post_published = timestamp

            else:
                print(f"No post to publish for {casualty}")

    except Exception as e:
        print(
            f"Couldn't publish the post for {casualty}:\n{e}\n\nGoing to stop publishing posts..."
        )
        STOP_PUBLISHING = True

    return casualty, published


def publish_casualties_posts(
    given_casualties_data: List[dict],
    instagram_user: str,
    intagram_password: str,
    posts_limit: int,
    min_images: int,
    test: bool,
    names: List[str],
) -> List[dict]:
    """Publish posts about all the casualties, one per each"""
    signal.signal(signal.SIGINT, signal_handler)

    updated_casualties_data = []
    instagram_client = InstagramClient(instagram_user, intagram_password)
    posts = 0
    images_per_posts = defaultdict(lambda: 0)

    for casualty_data in given_casualties_data:
        casualty: Casualty = Casualty.from_dict(casualty_data)
        if (
            (
                (
                    test
                    and (
                        (not casualty.post_tested and not casualty.post_published)
                        or names
                    )
                )
                or (not test and casualty.post_tested and not casualty.post_published)
            )
            and (not names or any([name in casualty.full_name for name in names]))
            and (posts_limit is None or posts < posts_limit)
        ):
            casualty.post_additional_images = [
                path for path in casualty.post_additional_images if os.path.isfile(path)
            ]
            if min_images and (
                not casualty.post_additional_images
                or len(casualty.post_additional_images) < min_images
            ):
                print(
                    f"\nNot enough images - the post about {casualty} won't be published."
                )
            else:
                casualty, published = _publish_casualty_post(
                    casualty,
                    instagram_client=instagram_client,
                    test=test,
                )
                if published:
                    posts += 1
                    images_per_posts[
                        len(casualty.post_additional_images)
                        if casualty.post_additional_images
                        else 0
                    ] += 1

        updated_casualties_data.append(casualty.to_dict())

    print(f"\n{posts} posts were published. Number of images in each posts:")
    print(
        "\n".join(
            f"{images}: {posts} posts" for images, posts in images_per_posts.items()
        )
    )

    return updated_casualties_data
