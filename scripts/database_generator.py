import json
import os
import logging
import argparse
import re
import math
from dataclasses import dataclass
from typing import Optional
import xml.etree.ElementTree as ET
import datetime

import git
import yaml

TAGS_PATH = "tags.yaml"
# Index file is used to specify tags for all entries in a directory,
# unless they are specified in the entry file
DEFAULT_FILE_NAME = "__default.yaml"
# Special entry that is used to link to the github file of the entry.
URL_ENTRY_NAME = "__url"
LAST_MOD_ENTRY_NAME = "__last_mod"
SITE_URL_ENTRY_NAME = "__site_url"
SITE_URL_PREFIX = "https://unify.ai/database/"
strict = False
warnings = 0


def log_warning(msg: str, exception_class: Exception = Exception):
    logging.warning(msg)
    global warnings  # pylint: disable=global-statement
    warnings += 1
    if strict:
        raise exception_class(msg)  # pylint: disable=broad-exception-raised


@dataclass(frozen=True)
class DependencyRestriction:
    tags: tuple[str] = tuple()
    groups: tuple[str] = tuple()

    @staticmethod
    def from_yml(obj: Optional[dict[str, list[str]]]):
        if obj is None:
            return DependencyRestriction()

        tags = obj.get("tags", [])
        groups = obj.get("groups", [])

        return DependencyRestriction(tags, groups)

    def empty(self):
        return len(self.tags) == 0 and len(self.groups) == 0


@dataclass(frozen=True)
class TagGroup:
    name: str = ""
    description: str = ""
    visible: bool = True
    tags: tuple[str] = tuple()
    min: int = 0
    max: int = math.inf
    depends_on: DependencyRestriction = DependencyRestriction()

    @staticmethod
    def from_dict(obj: dict[str, dict[str, dict | list | str]]) -> list["TagGroup"]:
        ret: list["TagGroup"] = []

        for key, value in obj.items():
            name = key
            description = value.get("description", "")
            visible = value.get("visible", True)
            tags = value.get("tags", [])
            min_items = value.get("min", 0)
            max_items = value.get("max", math.inf)
            depends_on = DependencyRestriction.from_yml(value.get("depends_on"))

            ret.append(
                TagGroup(
                    name, description, visible, tags, min_items, max_items, depends_on
                )
            )

        return ret

    def __hash__(self) -> int:
        return hash(self.name)


def load_tags_groups() -> list[TagGroup]:
    with open(TAGS_PATH, "r", encoding="utf-8") as f:
        tags = yaml.safe_load(f)
    tags = TagGroup.from_dict(tags["tags"])

    logging.info("Loaded tag groups")

    return tags


def load_tags(tag_groups: list[TagGroup]) -> list[str]:
    ret = []

    for group in tag_groups:
        ret.extend(group.tags)

    logging.info("Loaded tags")

    return list(set(ret))


def check_tags(tags_groups: list[TagGroup], entry_tags: list[str]):
    tag_set = set(entry_tags)
    if len(tag_set) != len(entry_tags):
        log_warning("Duplicate tags found", ValueError)
        entry_tags = list(tag_set)

    # 1: Get all active groups
    active_groups = {group for group in tags_groups if group.depends_on.empty()}
    for tag in tag_set:
        tag_group = None
        for group in tags_groups:
            if tag in group.tags:
                tag_group = group
                break

        if tag_group is None:
            log_warning(f"Can't find '{tag}' tag. Skipping..", ValueError)
            continue

        for group in tags_groups:
            if tag_group.name in group.depends_on.groups:
                active_groups.add(group)
                continue
            if tag in group.depends_on.tags:
                active_groups.add(group)

    # 2: Check tags are not outside of group
    for tag in tag_set:
        exists = False
        for group in active_groups:
            if tag in group.tags:
                exists = True
                break

        if not exists:
            log_warning(
                f"Tag '{tag}' couldn't be found in the current scope. "
                "Are you sure you enabled the scope for this tag? (i.e. added "
                f"tags that '{tag}' is dependant on)"
            )

    # 3: Check if min/max constraints are met
    for group in active_groups:
        count = 0
        for tag in tag_set:
            if tag in group.tags:
                count += 1

        if count < group.min:
            log_warning(
                f"Minimum tags for group '{group.name}' is not met, required "
                f"{group.min} and found {count}"
            )

        if count > group.max:
            log_warning(
                f"Maximum tags for group '{group.name}' is not met, required "
                f"{group.max} and found {count}"
            )


def fix_image_url(image_url: str):
    if not image_url.startswith("http") and not image_url.startswith("data:image"):
        image_url = "https://cdn.saas.unify.ai/" + image_url

    return image_url


def fix_entry_image(entry: dict[str, list[str]]):
    key = list(entry.keys())[0]
    if "image_url" not in entry[key]:
        return

    entry[key]["image_url"] = fix_image_url(entry[key]["image_url"])


def load_database(tag_groups: list[TagGroup]) -> dict[str, list[str]]:
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
                    check_tags(tag_groups, defaults["tags"])

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
                    check_tags(tag_groups, list(entry.values())[0]["tags"])
                    fix_entry_image(entry)
                    entry_key = list(entry.keys())[0]
                    entry[entry_key] = {**defaults, **entry[entry_key]}

                    # Add url entry
                    url = (
                        "https://github.com/unifyai/database/blob/"
                        f"main/{os.path.join(root, file)}"
                    )
                    url = url.replace("\\", "/")
                    if "./" in url:
                        url = url.replace("./", "")
                    entry[entry_key][URL_ENTRY_NAME] = url

                    # Add last mod entry
                    repo = git.Repo(search_parent_directories=True)
                    file_path = os.path.join(root, file)
                    last_mod = repo.git.log("-1", "--format=%at", "--", file_path)
                    entry[entry_key][LAST_MOD_ENTRY_NAME] = last_mod

                    # Add site url entry
                    site_url = SITE_URL_PREFIX + entry_key
                    entry[entry_key][SITE_URL_ENTRY_NAME] = site_url

                    database.update(entry)

    logging.info("Loaded database")
    return database


def sort_tags(tags: list[str], database: dict[str, list[str]]) -> list[str]:
    tags_count = {tag: 0 for tag in tags}
    for entry in database.values():
        for tag in entry["tags"]:
            if tag in tags_count:
                tags_count[tag] += 1

    tags = sorted(tags, key=lambda tag: tags_count[tag], reverse=True)
    tags = [tag for tag in tags if tags_count[tag] > 0]

    logging.info("Sorted tags")
    return tags


def generate_sitemap(database: dict[str, list[str]]):
    root = ET.Element("urlset")
    root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    url = ET.SubElement(root, "url")
    ET.SubElement(url, "loc").text = SITE_URL_PREFIX

    # for entry in database.values():
    #     url = ET.SubElement(root, "url")
    #     ET.SubElement(url, "loc").text = entry[SITE_URL_ENTRY_NAME]
    #     ET.SubElement(url, "lastmod").text = (
    #         datetime.datetime.fromtimestamp(int(entry[LAST_MOD_ENTRY_NAME])).isoformat()
    #         + "+00:00"
    #     )

    tree = ET.ElementTree(root)
    tree.write("build/sitemap.xml", encoding="utf-8", xml_declaration=True)

    logging.info("Generated sitemap")


def main():
    tag_groups = load_tags_groups()
    tags = load_tags(tag_groups)
    database = load_database(tag_groups)
    tags = sort_tags(tags, database)

    os.makedirs("build", exist_ok=True)
    with open("build/database.json", "w", encoding="utf-8") as f:
        json.dump(database, f)
    with open("build/tags.json", "w", encoding="utf-8") as f:
        json.dump(tags, f)
    with open("build/tag-groups.json", "w", encoding="utf-8") as f:
        filtered_groups = [group for group in tag_groups if group.visible]

        def default(o):
            if isinstance(o, set):
                return list(o)

            allowed_keys = ["name", "description", "tags"]

            return {k: v for k, v in o.__dict__.items() if k in allowed_keys}

        json.dump(filtered_groups, f, default=default)
    generate_sitemap(database)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--strict", action="store_true", help="Fail in case of warnings"
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Print all warnings but fail after running",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()
    strict = args.strict
    test = args.test

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    main()

    if warnings > 0 and test:
        exit(1)
