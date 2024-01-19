# The Database

Unify database is a collection of curated YAML files that hold a description of different algorithms, tools, repos, products, related to different layers of the ML deployment stack, mainly: serving, compression, compilers, hardware.

**[Website](https://unify.ai/database)** - **[Contribute](CONTRIBUTING.md)**

## How to access the database

You can offer the database through:

- [The website](https://unify.ai/database).
- Programmatically with [our endpoint](docs/endpoint.md).

## Database Structure

The database tree looks like this:

```
tool-category-1/
    ├─ tool.yaml
tool-category-2/
    ├─ __default.yaml
    ├─ tool.yaml
scripts/
    ├─ script.py
_sample.yaml
tags.yaml

```

- Tool category folders: For each tool a category is assigned, this is only organizational and doesn't reflect in the user interface.
- `tool.yaml`: Actual database entries, they should follow the format found in [`_sample.yaml`](_sample.yaml). Note that files that starts with `.` or `_` won't be rendered (e.g. `_sample.yaml`).
- `__default.yaml`: A special file that holds placeholder values for entries in the same folder, unless overridden by the actual entry. This is useful for assigning placeholder images, descriptions for entries that miss them.
- [`_sample.yaml`](_sample.yaml): A sample yaml file explaining the current schema of entries.
- [`tags.yaml`](tags.yaml): List of currently available tags, if you introducted new tags you should add them in this file.
