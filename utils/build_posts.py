import enum
import multiprocessing
from typing import List
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw, ImageOps

from utils.casualty import Casualty, Gender
from utils.paths import *


def get_font(size: int):
    return ImageFont.truetype(
        "resources/Rubik-Regular.ttf", size, layout_engine=ImageFont.Layout.RAQM
    )


def _get_background(casualty: Casualty):
    backgrounds = {
        Gender.FEMALE: "resources/female.png",
        Gender.MALE: "resources/male.png",
    }
    if casualty.gender not in backgrounds:
        raise Exception("Unknown gender")
    return backgrounds[casualty.gender]


def _get_image(casualty: Casualty) -> Image:
    casualty_img = Image.open(
        casualty.img_path if casualty.img_path else "resources/no_image_default.jpeg"
    )
    width, height = casualty_img.size
    ratio = height / width
    wanted_width = 300
    casualty_img = casualty_img.resize((wanted_width, int(wanted_width * ratio)))
    return casualty_img


def _add_text(
    text: str,
    font_size: int,
    bold: bool,
    increase_offset: int,
    draw: ImageDraw.Draw,
    y_axis_offset: int,
):
    font = get_font(font_size)
    left, top, right, bottom = font.getbbox(text)
    width, height = right - left, top - bottom
    draw.text(
        (630 - width, y_axis_offset),
        text,
        (255, 255, 255),
        direction="rtl",
        align="right",
        features="rtla",
        font=font,
        stroke_width=1 if bold else 0,
        stroke_fill="white",
    )
    y_axis_offset += increase_offset
    return draw, y_axis_offset


def _add_degree(
    casualty: Casualty, draw: ImageDraw.Draw, y_axis_offset: int
) -> ImageDraw.Draw:
    return _add_text(casualty.degree, 45, False, 50, draw, y_axis_offset)


def _add_name(
    casualty: Casualty, draw: ImageDraw.Draw, y_axis_offset: int
) -> ImageDraw.Draw:
    return _add_text(f'{casualty.full_name} ז"ל', 54, True, 65, draw, y_axis_offset)


def _add_dept(
    casualty: Casualty, draw: ImageDraw.Draw, y_axis_offset: int
) -> ImageDraw.Draw:
    if casualty.department:
        return _add_text(casualty.department, 45, False, 70, draw, y_axis_offset)
    else:
        return draw, y_axis_offset


def _add_details(
    casualty: Casualty, draw: ImageDraw.Draw, y_axis_offset: int
) -> ImageDraw.Draw:
    text = [
        f"נפל{'ה' if casualty.gender == Gender.FEMALE else ''} במלחמת חרבות ברזל",
        f"בתאריך {casualty.date_of_death_he} {casualty.date_of_death_en}",
    ]

    if casualty.age:
        text.append(
            f"בת {casualty.age} במותה"
            if casualty.gender == Gender.FEMALE
            else f"בן {casualty.age} במותו",
        )

    if casualty.living_city:
        text.append(
            f"התגורר{'ה' if casualty.gender == Gender.FEMALE else ''} ב{casualty.living_city}"
        )

    # if casualty.grave_city:
    #     text.append(
    #         f"מקום מנוחת{'ה' if casualty.gender == Gender.FEMALE else 'ו'} {casualty.grave_city}"
    #     )

    for i, line in enumerate(text):
        draw, y_axis_offset = _add_text(line, 32, False, 50, draw, y_axis_offset)

    return draw, y_axis_offset


def _create_casualty_post(casualty_data: dict) -> None:
    casualty: Casualty = Casualty.from_dict(casualty_data)
    try:
        if not casualty.published:
            background = _get_background(casualty)
            with Image.open(background) as post:
                image = _get_image(casualty)
                if image:
                    post.paste(image, (670, 140))
                draw = ImageDraw.Draw(post)
                y_axis_offset = 135
                draw, y_axis_offset = _add_degree(casualty, draw, y_axis_offset)
                draw, y_axis_offset = _add_name(casualty, draw, y_axis_offset)
                draw, y_axis_offset = _add_dept(casualty, draw, y_axis_offset)
                draw, y_axis_offset = _add_details(casualty, draw, y_axis_offset)
                post_dir = f"{POSTS_DIR}/{casualty.date_of_death.year}/{casualty.date_of_death.month}/{casualty.date_of_death.day}"
                Path(post_dir).mkdir(parents=True, exist_ok=True)
                casualty.post_path = f"{post_dir}/{casualty.full_name}.jpg"
                post.convert("RGB").save(casualty.post_path)
    except Exception as e:
        print(f"Failed to generate post for {casualty}: {e}")
    finally:
        return casualty.to_dict()


def create_casualties_posts(given_casualties_data: List[dict]) -> List[dict]:
    process_pool = multiprocessing.Pool()
    updated_casualties_data = process_pool.map(
        _create_casualty_post, given_casualties_data
    )
    process_pool.close()
    return updated_casualties_data
