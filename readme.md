# Zotero Analyzer

A Python class for analyzing Zotero databases and generating word clouds.

## Installation

### Option 1: Using requirements.txt (Recommended)

```bash
pip install -r requirements.txt
```

### Option 2: Using setup.py

```bash
pip install -e .
```

### Option 3: Manual installation

Install the required dependencies:

```bash
pip install openai wordcloud matplotlib python-dotenv
```

Note: `sqlite3` is included in Python's standard library, so no additional installation is needed.

## Usage

To use the Zotero Analyzer class, create an instance of the class and pass in the following arguments:

* `db_path`: The path to your Zotero database file.
* `api_key`: Your API key.
* `base_url`: The base URL for the API.
* `model`: The name of the OpenAI model you want to use.

## Methods

The Zotero Analyzer class provides the following methods:

### `create_word_cloud(**kwargs)`

Creates a word cloud using the `wordcloud` library and displays it using `matplotlib`. Additional arguments can be passed to customize the word cloud.

![wordcloud](example_imgs/example_wordcloud.png)

### `categorize_tags()`

Uses the OpenAI API to categorize the tags and returns the categorized tags as a string. Saves the result to `categorized_tags.md`.

### `plane_tags(save=True)`

Returns a list of unique tags and saves them to `plane_tags.txt` if `save` is `True`.

### `get_tags_with_tagid()`

Returns a dictionary of tags with their tag IDs.

### `get_item_tags()`

Returns a list of tags for each item.

### `all_tags()`

Returns a list of all tags.

## Example Use Cases

See `main.py` for some example use cases of the Zotero Analyzer class.
