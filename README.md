# Welcome to The Database!

Brought to you by [Unify](https://unify.ai/). The Database is a collection of different algorithms, tools, repos, and products related to different layers of the ML deployment stack, namely: serving, compression, compilers, hardware.

<p align="center">
<a href="https://unify.ai/database">The Database</a> - <a href="CONTRIBUTING.md">Contribute</a>
</p>

![database](https://github.com/nassimberrada/database/blob/main/database.png)

## Why the database?

AI deployment is fragmented, with multiple layers of serving, compression, compiler and hardware tools. Combined, these layers create a combinatorial explosion of possible deployment pathways, making optimizing models for production complex and confusing. 

Every week, new tools and SOTA algorithms are released to push the limits of performance and cater to different needs. From accelerating throughput, cutting down latency or compression models to run on resource constrained devices, keeping up with changed in the deployment landscape is difficult for industry practitioners.

The Database groups together all these tools into a single interface to help you stay sharp with the latest bleeding-edge, to help you make your models fly! 🚀

You can read more about the fragmented AI stack through our [blog posts](https://unify.ai/blog).

## How to access the database

You can offer the database through:

- [The website](https://unify.ai/database).
- Programmatically with [our endpoint](docs/endpoint.md).

## Folder Structure

The database is structured as follows:

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
- `_sample.yaml`: A sample yaml file explaining the current schema of entries.
- `tags.yaml`: List of currently available tags, if you introducted new tags you should add them in this file.
