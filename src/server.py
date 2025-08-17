# mcp server.py
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
import openai

from mcp.server.fastmcp import FastMCP

load_dotenv()

# Initialize FastMCP
mcp = FastMCP("zotero-mcp")


class ZoteroSearcher:
    def __init__(self):
        self.db_path = os.getenv("ZOTERO_DB_PATH")
        self.api_key = os.getenv("CBORG_API_KEY")
        self.base_url = os.getenv("CBORG_BASE_URL")
        self.model = os.getenv("CBORG_MODEL")
        self.zotero_storage_path = Path(self.db_path).parent / "storage"

        # Initialize OpenAI client for summaries
        self.client = openai.Client(api_key=self.api_key, base_url=self.base_url)


# Initialize the searcher
searcher = ZoteroSearcher()


@mcp.tool()
def get_all_tags() -> str:
    """
    Get all unique tags currently in the Zotero library.

    Returns:
        List of all unique tags
    """
    conn = sqlite3.connect(searcher.db_path)
    cur = conn.cursor()

    # Get only tags that are actually used by current items (not deleted)
    cur.execute(
        """
        SELECT DISTINCT tags.name, COUNT(DISTINCT itemTags.itemID) as count
        FROM tags
        JOIN itemTags ON tags.tagID = itemTags.tagID
        JOIN items ON itemTags.itemID = items.itemID
        WHERE items.itemID NOT IN (SELECT itemID FROM deletedItems)
            AND items.libraryID IS NOT NULL
        GROUP BY tags.name
        ORDER BY count DESC
    """
    )

    tags = cur.fetchall()
    conn.close()

    if not tags:
        return "No tags found in the library."

    result = "# All Tags in Zotero Library\n\n"
    result += f"Total unique tags: {len(tags)}\n\n"

    # Group by usage frequency
    high_use = [t for t in tags if t[1] >= 5]
    medium_use = [t for t in tags if 2 <= t[1] < 5]
    low_use = [t for t in tags if t[1] == 1]

    if high_use:
        result += "## Frequently Used Tags (5+ papers)\n"
        for tag, count in high_use:
            result += f"- {tag} ({count} papers)\n"
        result += "\n"

    if medium_use:
        result += "## Moderately Used Tags (2-4 papers)\n"
        for tag, count in medium_use:
            result += f"- {tag} ({count} papers)\n"
        result += "\n"

    if low_use:
        result += f"## Rarely Used Tags (1 paper) - {len(low_use)} tags\n"
        # Just show first 20 to avoid overwhelming output
        for tag, count in low_use[:20]:
            result += f"- {tag}\n"
        if len(low_use) > 20:
            result += f"... and {len(low_use) - 20} more\n"

    return result


@mcp.tool()
def search_by_tag(tag: str) -> str:
    """
    Find all papers with a specific tag.

    Args:
        tag: The tag to search for

    Returns:
        List of papers with the specified tag
    """
    conn = sqlite3.connect(searcher.db_path)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT DISTINCT
            items.key,
            title.value as title,
            abstract.value as abstract
        FROM items
        JOIN itemTags ON items.itemID = itemTags.itemID
        JOIN tags ON itemTags.tagID = tags.tagID
        LEFT JOIN itemData title_data ON items.itemID = title_data.itemID AND title_data.fieldID = 1
        LEFT JOIN itemDataValues title ON title_data.valueID = title.valueID
        LEFT JOIN itemData abstract_data ON items.itemID = abstract_data.itemID AND abstract_data.fieldID = 90
        LEFT JOIN itemDataValues abstract ON abstract_data.valueID = abstract.valueID
        WHERE LOWER(tags.name) = LOWER(?)
            AND items.itemID NOT IN (SELECT itemID FROM deletedItems)
            AND items.libraryID IS NOT NULL
    """,
        (tag,),
    )

    papers = cur.fetchall()
    conn.close()

    if not papers:
        return f"No papers found with tag: '{tag}'"

    result = f"# Papers with tag: {tag}\n\n"
    result += f"Found {len(papers)} papers\n\n"

    for i, (key, title, abstract) in enumerate(papers, 1):
        result += f"## {i}. {title or 'Untitled'}\n"
        result += f"**Key**: {key}\n"
        if abstract:
            abstract_preview = abstract[:200]
            if len(abstract) > 200:
                abstract_preview += "..."
            result += f"**Abstract**: {abstract_preview}\n"
        result += "\n"

    return result


if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()
