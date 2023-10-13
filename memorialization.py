import argparse
import getpass
import importlib

from utils.json_storage import reload_casualties_data, write_casualties_data
from utils.build_posts import create_casualties_posts
from utils.publish_posts import publish_casualties_posts


class Password(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        values = getpass.getpass()
        setattr(namespace, self.dest, values)


def args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Insta Memorialization",
        description="Tool for publishing personal posts describing the war casualties",
    )
    parser.add_argument(
        "-pkg",
        "--package",
        required=True,
        help="""
            Relative python package path, e.g. "iron_swords", which includes:
            - scrap.py: collect_casualties_data function
            - paths.py: JSON_FILE path
        """,
    )
    parser.add_argument("-user", "--instagram_username", required=True)
    parser.add_argument(
        "-pass",
        "--instagram_password",
        action=Password,
        nargs="?",
        dest="instagram_password",
        required=True,
    )
    return parser


if __name__ == "__main__":
    args = args_parser().parse_args()

    collect_casualties_data = importlib.import_module(
        f"{args.package}.scrap"
    ).collect_casualties_data
    JSON_FILE = importlib.import_module(f"{args.package}.paths").JSON_FILE

    instagram_username = args.instagram_username
    instagram_password = args.instagram_password

    collect_casualties_data("https://www.idf.il/59780")
    casualties_data = reload_casualties_data(JSON_FILE)
    casualties_data = create_casualties_posts(casualties_data)
    casualties_data = publish_casualties_posts(
        casualties_data, instagram_username, instagram_password
    )
    write_casualties_data(casualties_data, JSON_FILE)
