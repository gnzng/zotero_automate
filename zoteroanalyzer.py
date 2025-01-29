import sqlite3
import openai
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random


class ZoteroAnalyzer:
    def __init__(self, db_path, api_key, base_url, model):
        self.db_path = db_path
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = openai.Client(api_key=self.api_key, base_url=self.base_url)

    def get_tags_with_tagid(self):
        """
        Returns a dictionary of tags with their tagID
        eg. {1: 'tag1', 2: 'tag2'}
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT name, tagID FROM tags")
        tags = {tag[1]: tag[0] for tag in cur.fetchall()}
        conn.close()
        return tags

    def get_item_tags(self):
        """
        Returns a list of tags for each item
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT tagID, itemID FROM itemTags")
        item_tags = [tag[0] for tag in cur.fetchall()]
        conn.close()
        return item_tags

    def unique_tags(self, save=True):
        tags = self.get_tags_with_tagid()
        item_tags = self.get_item_tags()
        non_empty_tags = set(item_tags)
        unique_tags = [tags.get(i, 'Unknown') for i in non_empty_tags]
        if save:
            with open('unique_tags.txt', 'w') as f:
                f.write('\n'.join(unique_tags))
        return unique_tags

    def all_tags(self):
        tags = self.get_tags_with_tagid()
        item_tags = self.get_item_tags()
        all_tags = [tags.get(i, 'Unknown') for i in item_tags]
        return all_tags

    def categorize_tags(self, save=True, for_obsidian_mardown=True):
        """
        Categorize the tags using the chat completions API and saves it as a markdown file.
        """
        tags = self.unique_tags(save=False)
        if for_obsidian_mardown:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Categorize the following tags for my publication collection: " +
                            str(tags) + " One tag can belong to multiple categories. "
                            "Do not change the format of the tags." +
                            "Use the following format as an output:" +
                            "# category 1 \n [[tag-1]]|[[tag-2]] \n # category 2 \n [[tag-2]]|[[tag-3]]"
                        )
                    }
                ],
                temperature=0.5
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Categorize the following tags for my publication collection: " +
                            str(tags) + " One tag can belong to multiple categories. "
                            "Do not change the format of the tags."
                        )
                    }
                ],
                temperature=0.5
            )
        responded = response.choices[0].message.content
        if save:
            with open('categorized_tags.md', 'w') as f:
                f.write(response.choices[0].message.content)
        return responded

    def create_word_cloud(self, **kwargs):
        tags = self.all_tags()
        tags = [tag.replace(" ", "-") for tag in tags]
        random.shuffle(tags)  # shuffle the tags to get a random word cloud
        wordcloud = WordCloud(regexp=r"\w[\w'-]*", **kwargs).generate(' '.join(tags))
        plt.figure()
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.show()
