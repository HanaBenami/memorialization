import datetime
from typing import List
from utils.casualty import Casualty, Gender
from utils.paths import *
from instagrapi import Client

stop_publishing = False


def init_instagram_client(instagram_user: str, intagram_password: str) -> Client:
    instagram_client = Client()
    instagram_client.login(instagram_user, intagram_password)
    return instagram_client


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


def _publish_casualties_post(casualty_data: dict, instagram_client: Client) -> dict:
    global stop_publishing
    casualty: Casualty = Casualty.from_dict(casualty_data)
    try:
        if not casualty.published and not stop_publishing:
            if casualty.post_path:
                post_text = _prepare_post_text(casualty)
                post_hashtags = _prepare_post_hashtags(casualty)
                post_cation = f"{post_text}\n{post_hashtags}"
                post_image = casualty.post_path
                media = instagram_client.photo_upload(post_image, post_cation)
                print(f"\nThe following post was published:\n{media}")
                casualty.published = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            else:
                print(f"No post to publish for {casualty}")
    except Exception as e:
        print(f"\nCouldn't publish the post for {casualty}:\n{e}\n\nGoing to stop...")
        stop_publishing = True
    return casualty.to_dict()


def publish_casualties_posts(
    casualties_data: List[dict], instagram_user: str, intagram_password: str
) -> List[dict]:
    instagram_client = init_instagram_client(instagram_user, intagram_password)
    casualties_data = [
        _publish_casualties_post(casualty_data, instagram_client)
        for casualty_data in casualties_data
    ]
    return casualties_data
