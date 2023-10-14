import datetime
import enum
from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from pyluach.dates import HebrewDate


class Gender(str, enum.Enum):
    """Gender"""

    FEMALE = "F"
    MALE = "M"


@dataclass_json
@dataclass
class Casualty:
    """Casualty data"""

    degree: str
    full_name: str
    department: str | None
    living_city: str | None
    grave_city: str | None
    age: int | None
    gender: Gender | None
    date_of_death_str: str | None  # Required format: %Y-%m-%d
    img_path: str | None
    data_url: str
    post_path: str | None = None
    post_caption: str | None = None
    post_images: List[str] | None = None
    post_published: bool | str = False

    def __str__(self) -> str:
        return f'"{self.full_name}"'

    @property
    def date_of_death(self):
        """Casualty date of death, as a date object"""
        if self.date_of_death_str:
            return datetime.datetime.strptime(self.date_of_death_str, "%Y-%m-%d")

    @property
    def date_of_death_en(self):
        """Casualty date of death, in Gregorian format"""
        if self.date_of_death_str:
            self.date_of_death.strftime("%d/%m/%Y")

    @property
    def date_of_death_he(self):
        """Casualty date of death, in Jewish format"""
        if self.date_of_death_str:
            hebrew_date = HebrewDate.from_pydate(self.date_of_death)
            return f"{hebrew_date:%*d %*B %*y}"
