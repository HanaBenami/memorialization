from dataclasses import dataclass
from dataclasses_json import dataclass_json
from pyluach.dates import HebrewDate
import datetime
import enum


class Gender(str, enum.Enum):
    FEMALE = "F"
    MALE = "M"


@dataclass_json
@dataclass
class Casualty:
    degree: str
    full_name: str
    department: str | None
    living_city: str | None
    grave_city: str | None
    age: int | None
    gender: Gender | None
    date_of_death_str: str  # Required format: %Y-%m-%d
    img_path: str | None
    data_url: str
    post_path: str | None
    published: bool | str

    @property
    def date_of_death(self):
        return datetime.datetime.strptime(self.date_of_death_str, "%Y-%m-%d")

    @property
    def date_of_death_en(self):
        return self.date_of_death.strftime("%d/%m/%Y")

    @property
    def date_of_death_he(self):
        hebrew_date = HebrewDate.from_pydate(self.date_of_death)
        return f"{hebrew_date:%*d %*B %*y}"
