# How to contribute to our database

## Adding a new entry

1. Fork this repository
2. Create a `.yaml` file in the appropriate folder (e.g. `orchestration/`), to know the structure of the file, please refer to the [_sample.yaml](_sample.yaml) file.
3. Create a pull request

### Add a new image

Currently, we host the images on our servers to avoid broken links. To add a new image, there are 2 options:

1. Put a link to the image in the `image_url` field of the `.yaml` file.
2. Upload the image in the PR description.

In both cases, we will upload the image to our servers and update the link in the `.yaml` file.

## Updating an existing entry

1. Fork this repository
2. Update the `.yaml` file
3. Create a pull request detailing the changes

## Removing an entry

1. Create an issue detailing the reason for the removal
2. We will evaluate the request and remove the entry if needed

## Report an issue

1. Create an issue detailing the issue
2. Please include the link to the entry, as well as the reason for the issue
3. We will look into it!
