import datetime
from typing import List
from utils.casualty import Casualty, Gender
from utils.paths import *
from instagrapi import Client

# TODO

updated_casualties_data = []


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
        casualty.date_of_death_en,
        f"והותיר{gender_suffix}",
        f"אחרי{gender_suffix or 'ו'}",
        "חיים שלמים וזכרונות!",
    ]
    return " ".join(text)


def _prepare_post_hashtags(casualty: Casualty) -> str:
    """Prepare to text description for the given casualty post"""
    hashtags = [
        casualty.full_name,
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
    return " ".join(hashtags)


def _publish_casualties_post(casualty_data: dict, instagram_client: Client) -> dict:
    casualty: Casualty = Casualty.from_dict(casualty_data)
    if not casualty.published:
        if casualty.post_path:
            post_text = _prepare_post_text(casualty)
            post_hashtags = _prepare_post_hashtags(casualty)
            post_cation = f"{post_text}\n{post_hashtags}"
            post_image = casualty.post_path
            media = instagram_client.photo_upload(post_image, post_cation)
            print(f"The following post was published:\n{media}")
            casualty.published = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            print(f"No post to publish for {casualty}")
    return casualty.to_dict()


def publish_casualties_posts(
    given_casualties_data: List[dict], instagram_user: str, intagram_password: str
) -> List[dict]:
    instagram_client = init_instagram_client(instagram_user, intagram_password)
    for casualty_data in given_casualties_data:
        updated_casualties_data.append(
            _publish_casualties_post(casualty_data, instagram_client)
        )
    return updated_casualties_data
