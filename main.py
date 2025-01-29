import os
from dotenv import load_dotenv

from zoteroanalyzer import ZoteroAnalyzer

load_dotenv()

ZOTERO_DB_PATH = os.getenv("ZOTERO_DB_PATH")
CBORG_API_KEY = os.getenv("CBORG_API_KEY")
CBORG_BASE_URL = os.getenv("CBORG_BASE_URL")
CBORG_MODEL = os.getenv("CBORG_MODEL")

analyzer = ZoteroAnalyzer(ZOTERO_DB_PATH, CBORG_API_KEY, CBORG_BASE_URL, CBORG_MODEL)


# categorize the tags using the chat completions API
analyzer.categorize_tags(save=True, for_obsidian_mardown=True)

# visualize the tags words in a word cloud
analyzer.create_word_cloud(width=800, height=400, max_words=100, background_color='black', colormap='turbo')

# save the unique tags in a text file for further analysis
analyzer.unique_tags(save=True)
