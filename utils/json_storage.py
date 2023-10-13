import json
from typing import List


def write_casualties_data(data: List[dict], json_path: str) -> None:
    """Dump the data into a file"""
    with open(json_path, "w+") as fp:
        json.dump(data, fp, indent=4, ensure_ascii=False)


def reload_casualties_data(json_path: str) -> List[dict]:
    """Reload the data from the file"""
    try:
        with open(json_path, "r") as fp:
            casualties_data = json.load(fp)
        return casualties_data
    except:
        return []
