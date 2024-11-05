# Zotero Analyzer
================

A Python class for analyzing Zotero databases and generating word clouds.

## Installation
---------------

To use this class, you'll need to install the following libraries:

* `sqlite3`
* `openai`
* `wordcloud`
* `matplotlib`

You can install these libraries using pip:
```bash
pip install sqlite3 openai wordcloud matplotlib
```
## Usage
-----

To use the Zotero Analyzer class, you'll need to create an instance of the class and pass in the following arguments:

* `db_path`: The path to your Zotero database file.
* `api_key`: Your API key.
* `base_url`: The base URL for the API.
* `model`: The name of the OpenAI model you want to use.

## Methods
-------

The Zotero Analyzer class has the following methods:

### `create_word_cloud(**kwargs)`

Creates a word cloud using the `wordcloud` library and displays it using `matplotlib`. You can pass in additional arguments to customize the word cloud.

![wordcloud](example_imgs/example_wordcloud.png)

### `categorize_tags()`

Uses the OpenAI API to categorize the tags and returns the categorized tags as a string. And saves it to `categorized_tags.md`. 

eg:

### `plane_tags(save=True)`

Returns a list of unique tags and saves them to a file called `plane_tags.txt` if `save` is `True`.


### `get_tags_with_tagid()`

Returns a dictionary of tags with their tagID.

### `get_item_tags()`

Returns a list of tags for each item.


### `all_tags()`

Returns a list of all tags.



## Example Use Cases
--------------------

See `main.py` fore some example use cases for the Zotero Analyzer class. 

