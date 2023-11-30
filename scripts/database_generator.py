import yaml
import json
import os
import logging
import argparse
import re

TAGS_PATH = "tags.yaml"
# Index file is used to specify tags for all entries in a directory,
# unless they are specified in the entry file
DEFAULT_FILE_NAME = "__default.yaml"
# Special entry that is used to link to the github file of the entry.
URL_ENTRY_NAME = "__url"
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


def fix_image_url(image_url: str):
    if not image_url.startswith("http") and not image_url.startswith("data:image"):
        image_url = "https://cdn.saas.unify.ai/" + image_url

    return image_url


def fix_entry_image(entry: dict[str, list[str]]):
    key = list(entry.keys())[0]
    if "image_url" not in entry[key]:
        return

    entry[key]["image_url"] = fix_entry_image(entry[key]["image_url"])


def load_database(tags: list[str]) -> dict[str, list[str]]:
    database = {}
    for root, _, files in os.walk("."):
        # Load index file
        defaults = {}
        if DEFAULT_FILE_NAME in files:
            logging.debug("Loading %s defaults", root)
            with open(
                os.path.join(root, DEFAULT_FILE_NAME), "r", encoding="utf-8"
            ) as f:
                defaults = yaml.safe_load(f)
                if "tags" in defaults:
                    check_tags(tags, defaults["tags"])

                if "image_url" in defaults:
                    defaults["image_url"] = fix_image_url(defaults["image_url"])

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
                    entry_key = list(entry.keys())[0]
                    entry[entry_key] = {**defaults, **entry[entry_key]}

                    # Add url entry
                    url = "https://github.com/unifyai/database/blob/" \
                        f"main/{os.path.join(root, file)}"
                    url = url.replace("\\", "/")
                    if './' in url:
                        url = url.replace("./", "")
                    entry[entry_key][URL_ENTRY_NAME] = url

                    database.update(entry)

    logging.info("Loaded database")
    return database


def sort_tags(tags: list[str], database: dict[str, list[str]]) -> list[str]:
    tags_count = {tag: 0 for tag in tags}
    for entry in database.values():
        for tag in entry["tags"]:
            tags_count[tag] += 1

    tags = sorted(tags, key=lambda tag: tags_count[tag], reverse=True)

    logging.info("Sorted tags")
    return tags


def main():
    tags = load_tags()
    database = load_database(tags)
    tags = sort_tags(tags, database)

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
