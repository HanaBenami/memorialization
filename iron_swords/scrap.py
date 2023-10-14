import enum
import os
import json
from pathlib import Path
import re
import time
from datetime import datetime
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from iron_swords.paths import IMAGES_DIR


from utils.casualty import Casualty, Gender


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")


def collect_casualties_urls(main_url: str, page_limit: int | None) -> List[str]:
    """Return a list with the URLs of all the casualties pages"""
    urls = []
    pages = 1
    with webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=chrome_options
    ) as driver:
        # Collect links to all the casualties pages
        driver.get(main_url)
        while True:
            try:
                # Wait until the page is ready
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "casualty-item"))
                )

                # Collect data
                casualty_items = driver.find_elements(By.CLASS_NAME, "casualty-item")
                for casualty_item in casualty_items:
                    urls.append(
                        casualty_item.find_element(
                            By.CLASS_NAME, "btn-link-text"
                        ).get_attribute("href")
                    )

                print(f"{len(urls)} URLs were collected")

                pages += 1

                if page_limit and page_limit < pages:
                    break

                # Go to the next page
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "page-item-next"))
                ).click()

            # Expection will be raised when no pages left
            except Exception:
                break

    return urls


def re_search(pattern: str, txt: str) -> str | None:
    """Search for a match and return it."""
    match = re.search(pattern, txt)
    return match.group(1) if match else None


def collect_casualty(url: str) -> Casualty:
    """Scrap the casualty page, parse his data and return it"""
    with webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=chrome_options
    ) as driver:
        driver.get(url)
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "soldier-image"))
        )

        section = (
            driver.find_element(By.CLASS_NAME, "share-section")
            .get_attribute("innerText")
            .replace("\n\n", "\n")
        )

        full_name = section.split("\n")[0].replace(' ז"ל', "")
        degree, full_name = full_name.split(" ", 1)
        if full_name[0] == "(":
            degree_cont, full_name = full_name.split(" ", 1)
            degree = degree + " " + degree_cont

        img_url = (
            driver.find_element(By.CLASS_NAME, "soldier-image")
            .find_element(By.CLASS_NAME, "img-fluid")
            .get_attribute("src")
        )
        if "candle" in img_url:
            img_path = None
        else:
            img_path = f"{IMAGES_DIR}/{full_name}.jpg"
            Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)
            img = driver.find_element(By.CLASS_NAME, "soldier-image").find_element(
                By.CLASS_NAME, "img-fluid"
            )
            img.screenshot(img_path)

        date_of_death_str = re_search("(?:נפל.? ביום .*?)(\d+\.\d+\.\d+)", section)
        date_of_death_str = (
            datetime.strptime(date_of_death_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            if date_of_death_str
            else None
        )

        age = re_search("(?:בן|בת) (\d+)", section)
        age = int(age) if age else None

        gender = (
            Gender.MALE
            if "בן" in section
            else Gender.FEMALE
            if "בת" in section
            else None
        )

        casualty = Casualty(
            degree=degree,
            full_name=full_name,
            department=section.split("\n")[1],
            living_city=re_search("(?:, מ)(.*?)(?:,)", section),
            grave_city=re_search("(בית העלמין.*?)(?:\\.)", section),
            age=age,
            gender=gender,
            date_of_death_str=date_of_death_str,
            img_path=img_path,
            post_path=None,
            published=False,
            data_url=url,
        )

    return casualty


def collect_casualties_data(
    casualties_data: List[dict], page_limit: int | None
) -> List[dict]:
    """Collect casualties data from the IDF website"""
    exist_urls = [
        Casualty.from_dict(casualty_data).data_url for casualty_data in casualties_data
    ]
    new_urls_counter = 0

    urls = collect_casualties_urls(
        "https://www.idf.il/%D7%A0%D7%95%D7%A4%D7%9C%D7%99%D7%9D/%D7%97%D7%9C%D7%9C%D7%99-%D7%97%D7%A8%D7%91%D7%95%D7%AA-%D7%91%D7%A8%D7%96%D7%9C/",
        page_limit,
    )
    for url in urls:
        if url not in exist_urls:
            casualty_data = collect_casualty(url).to_dict()
            casualties_data.append(casualty_data)
            new_urls_counter += 1

    print(f"\n{new_urls_counter} URLs are new")

    return casualties_data
