# Landscape Database

Landscape is a collection of curated YAML files that hold a description of different algorithms, tools, repos, products, related to different layers of the ML deployment stack, mainly: orchestration, compression, compilers, hardware.

## Database Structure

The database tree looks like this:

```
tool-category-1/
    ├─ tool.yaml
tool-category-2/
    ├─ tool.yaml
scripts/
    ├─ script.py
_sample.yaml
tags.yaml

```

- Tool category folders: For each tool a category is assigned, this is only organizational and doesn't reflect in the user interface.
- `tool.yaml`: Actual database entries, they should follow the format found in [`_sample.yaml`](_sample.yaml). Note that files that starts with `.` or `_` won't be rendered (e.g. `_sample.yaml`).
- [`_sample.yaml`](_sample.yaml): A sample yaml file explaining the current schema of entries.
- [`tags.yaml`](tags.yaml): List of currently available tags, if you introducted new tags you should add them in this file.
