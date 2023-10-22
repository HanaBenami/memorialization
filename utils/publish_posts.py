import os
import datetime
from collections import defaultdict
from typing import List, Tuple
from functools import reduce
import signal
import instagrapi.types

from utils.casualty import Casualty, Gender
from utils.images import remove_duplicates_images
from utils.instagram import InstagramClient
from utils.paths import *
from utils.instagram import InstagramClient


STOP_PUBLISHING = False
BAD_ATTEMPTS = 0


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


def _prepare_post_images(casualty: Casualty) -> List[str]:
    """Prepare list of images to publish, without duplications"""
    post_images_paths, removed = remove_duplicates_images(
        casualty.post_additional_images
    )
    if removed:
        print(f"{len(removed)} duplicates images were removed")
    return post_images_paths


def _publish_casualty_post(
    casualty: Casualty,
    instagram_client: InstagramClient,
    test: bool = False,
    dry_run: bool = False,
) -> Tuple[Casualty, instagrapi.types.Media | bool | None, int]:
    """Publish a post about the casualty"""
    global STOP_PUBLISHING
    global BAD_ATTEMPTS
    published, post_images_paths = None, []
    try:
        if not STOP_PUBLISHING:
            if casualty.post_path:
                post_text = _prepare_post_text(casualty)
                post_hashtags = _prepare_post_hashtags(casualty)
                post_cation = f"{post_text}\n{post_hashtags}"
                casualty.post_caption = post_cation
                post_images_paths = _prepare_post_images(casualty)
                published = instagram_client.publish_post(
                    post_cation,
                    casualty.post_path,
                    post_images_paths,
                    dry_run,
                )
                if published and not dry_run:
                    print(f"The post about {casualty} was published' successfully.")
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
        if 2 < BAD_ATTEMPTS:
            STOP_PUBLISHING = True
        else:
            BAD_ATTEMPTS += 1

    return casualty, published, len(post_images_paths)


def publish_casualties_posts(
    given_casualties_data: List[dict],
    instagram_user: str,
    intagram_password: str,
    posts_limit: int,
    min_images: int,
    names: List[str],
    test: bool = False,
    dry_run: bool = False,
) -> List[dict]:
    """Publish posts about all the casualties, one per each"""
    signal.signal(signal.SIGINT, signal_handler)

    updated_casualties_data = []
    instagram_client = InstagramClient(instagram_user, intagram_password)
    posts = 0
    images_per_posts = defaultdict(lambda: [])

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
                casualty, published, num_of_images = _publish_casualty_post(
                    casualty,
                    instagram_client=instagram_client,
                    test=test,
                    dry_run=dry_run,
                )
                if published:
                    posts += 1
                    images_per_posts[num_of_images].append(casualty)

        updated_casualties_data.append(casualty.to_dict())

    print(
        f"\n{posts} posts were {'prepared' if dry_run else 'published'}. Number of images in each posts:"
    )
    print(
        "\n".join(
            f"{images}: {len(posts)} posts ({[casualty.full_name for casualty in posts] if 1 < images else ''})"
            for images, posts in images_per_posts.items()
        )
    )

    return updated_casualties_data
