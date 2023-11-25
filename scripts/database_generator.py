import yaml
import json
import os
import logging
import argparse
import re

TAGS_PATH = "tags.yaml"
strict = False


def log_warning(msg: str, exception_class: Exception = Exception):
    logging.warning(msg)
    if strict:
        raise exception_class(msg)  # pylint: disable=broad-exception-raised


def load_tags() -> list[str]:
    with open(TAGS_PATH, "r", encoding="utf-8") as f:
        tags = yaml.safe_load(f)
    tags = tags["tags"]

    logging.info("Loaded tags")

    # Find duplicate tags
    tags_set = set(tags)
    if len(tags_set) != len(tags):
        log_warning("Duplicate tags found", ValueError)
        tags = list(tags_set)

    return tags


def check_tags(tags: list[str], entry_tags: list[str]):
    tags_set = set(entry_tags)
    if len(tags_set) != len(entry_tags):
        log_warning("Duplicate tags found", ValueError)
        entry_tags = list(tags_set)

    for tag in entry_tags:
        if tag not in tags:
            log_warning(f"Tag {tag} not found", ValueError)


def fix_entry_image(entry: dict[str, list[str]]):
    key = list(entry.keys())[0]
    if "image_url" not in entry[key]:
        return

    image_url = entry[key]["image_url"]
    if not image_url.startswith("http") and not image_url.startswith("data:image"):
        image_url = "https://cdn.saas.unify.ai/" + image_url

    entry[key]["image_url"] = image_url


def load_database(tags: list[str]) -> dict[str, list[str]]:
    database = {}
    for root, _, files in os.walk("."):
        for file in files:
            if (
                file != TAGS_PATH
                and re.match(r"[^._].*\.ya?ml$", file)
                and re.match(r".[\\/][^.].*", root)
            ):
                logging.debug("Loading %s", os.path.join(root, file))
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    entry = yaml.safe_load(f)
                    check_tags(tags, list(entry.values())[0]["tags"])
                    fix_entry_image(entry)

                    database.update(entry)

    logging.info("Loaded database")
    return database


def main():
    tags = load_tags()
    database = load_database(tags)

    os.makedirs("build", exist_ok=True)
    with open("build/database.json", "w", encoding="utf-8") as f:
        json.dump(database, f)
    with open("build/tags.json", "w", encoding="utf-8") as f:
        json.dump(tags, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--strict", action="store_true", help="Fail in case of warnings"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()
    strict = args.strict

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    main()
