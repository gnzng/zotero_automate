import pytest
import sqlite3
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from zoteroanalyzer import ZoteroAnalyzer


class TestZoteroAnalyzer:
    """Test the ZoteroAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create a ZoteroAnalyzer instance for testing."""
        return ZoteroAnalyzer(
            db_path="/test/path/db.sqlite",
            api_key="test-api-key",
            base_url="https://api.test.com",
            model="test-model",
        )

    @pytest.fixture
    def temp_db(self):
        """Create a temporary SQLite database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = f.name

        # Create test database with sample data
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Create tables
        cur.execute(
            """
            CREATE TABLE tags (
                tagID INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """
        )

        cur.execute(
            """
            CREATE TABLE itemTags (
                tagID INTEGER,
                itemID INTEGER,
                FOREIGN KEY (tagID) REFERENCES tags (tagID)
            )
        """
        )

        # Insert test data
        cur.execute(
            "INSERT INTO tags (tagID, name) VALUES (1, 'python'), (2, 'machine-learning'), (3, 'data-science')"
        )
        cur.execute(
            "INSERT INTO itemTags (tagID, itemID) VALUES (1, 1), (2, 1), (3, 2), (1, 3)"
        )

        conn.commit()
        conn.close()

        yield db_path

        # Cleanup
        os.unlink(db_path)

    def test_init(self, analyzer):
        """Test ZoteroAnalyzer initialization."""
        assert analyzer.db_path == "/test/path/db.sqlite"
        assert analyzer.api_key == "test-api-key"
        assert analyzer.base_url == "https://api.test.com"
        assert analyzer.model == "test-model"
        assert analyzer.client is not None

    def test_get_tags_with_tagid(self, temp_db):
        """Test getting tags with tagID from database."""
        analyzer = ZoteroAnalyzer(
            db_path=temp_db,
            api_key="test-api-key",
            base_url="https://api.test.com",
            model="test-model",
        )

        tags = analyzer.get_tags_with_tagid()

        expected = {1: "python", 2: "machine-learning", 3: "data-science"}
        assert tags == expected

    def test_get_item_tags(self, temp_db):
        """Test getting item tags from database."""
        analyzer = ZoteroAnalyzer(
            db_path=temp_db,
            api_key="test-api-key",
            base_url="https://api.test.com",
            model="test-model",
        )

        item_tags = analyzer.get_item_tags()

        # Should return tagIDs: [1, 2, 3, 1] (from the test data)
        assert item_tags == [1, 2, 3, 1]

    def test_unique_tags(self, temp_db):
        """Test getting unique tags."""
        analyzer = ZoteroAnalyzer(
            db_path=temp_db,
            api_key="test-api-key",
            base_url="https://api.test.com",
            model="test-model",
        )

        unique_tags = analyzer.unique_tags(save=False)

        # Should return unique tag names: ['python', 'machine-learning', 'data-science']
        expected = ["python", "machine-learning", "data-science"]
        assert sorted(unique_tags) == sorted(expected)

    @patch("builtins.open", new_callable=mock_open)
    def test_unique_tags_save(self, mock_file, temp_db):
        """Test saving unique tags to file."""
        analyzer = ZoteroAnalyzer(
            db_path=temp_db,
            api_key="test-api-key",
            base_url="https://api.test.com",
            model="test-model",
        )

        analyzer.unique_tags(save=True)

        mock_file.assert_called_once_with("unique_tags.txt", "w")
        mock_file().write.assert_called_once()

    def test_all_tags(self, temp_db):
        """Test getting all tags (including duplicates)."""
        analyzer = ZoteroAnalyzer(
            db_path=temp_db,
            api_key="test-api-key",
            base_url="https://api.test.com",
            model="test-model",
        )

        all_tags = analyzer.all_tags()

        # Should return all tag names including duplicates: ['python', 'machine-learning', 'data-science', 'python']
        expected = ["python", "machine-learning", "data-science", "python"]
        assert all_tags == expected

    def test_categorize_tags_obsidian(self, analyzer):
        """Test categorizing tags for Obsidian markdown."""
        with patch.object(
            analyzer,
            "unique_tags",
            return_value=["python", "machine-learning", "data-science"],
        ):
            with patch.object(
                analyzer.client.chat.completions, "create"
            ) as mock_create:
                mock_response = MagicMock()
                mock_response.choices[0].message.content = (
                    "# AI/ML\n[[python]]|[[machine-learning]]\n# Data Science\n[[data-science]]"
                )
                mock_create.return_value = mock_response

                result = analyzer.categorize_tags(save=False, for_obsidian_mardown=True)

                assert (
                    result
                    == "# AI/ML\n[[python]]|[[machine-learning]]\n# Data Science\n[[data-science]]"
                )
                mock_create.assert_called_once()

                # Check that the correct prompt was used
                call_args = mock_create.call_args
                assert "for_obsidian_mardown" in str(
                    call_args
                ) or "format as an output" in str(call_args)

    def test_categorize_tags_regular(self, analyzer):
        """Test categorizing tags for regular format."""
        with patch.object(
            analyzer,
            "unique_tags",
            return_value=["python", "machine-learning", "data-science"],
        ):
            with patch.object(
                analyzer.client.chat.completions, "create"
            ) as mock_create:
                mock_response = MagicMock()
                mock_response.choices[0].message.content = (
                    "Category 1: python, machine-learning\nCategory 2: data-science"
                )
                mock_create.return_value = mock_response

                result = analyzer.categorize_tags(
                    save=False, for_obsidian_mardown=False
                )

                assert (
                    result
                    == "Category 1: python, machine-learning\nCategory 2: data-science"
                )
                mock_create.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    def test_categorize_tags_save(self, mock_file, analyzer):
        """Test saving categorized tags to file."""
        with patch.object(
            analyzer,
            "unique_tags",
            return_value=["python", "machine-learning", "data-science"],
        ):
            with patch.object(
                analyzer.client.chat.completions, "create"
            ) as mock_create:
                mock_response = MagicMock()
                mock_response.choices[0].message.content = "Test categorization"
                mock_create.return_value = mock_response

                result = analyzer.categorize_tags(save=True, for_obsidian_mardown=False)

                assert result == "Test categorization"
                mock_file.assert_called_once_with("categorized_tags.md", "w")
                mock_file().write.assert_called_once_with("Test categorization")

    def test_create_word_cloud(self, analyzer):
        """Test creating word cloud."""
        with patch.object(
            analyzer,
            "all_tags",
            return_value=["python", "machine-learning", "data-science"],
        ):
            with patch("zoteroanalyzer.WordCloud") as mock_wordcloud:
                with patch("zoteroanalyzer.plt") as mock_plt:
                    mock_wc_instance = MagicMock()
                    mock_wordcloud.return_value = mock_wc_instance

                    analyzer.create_word_cloud(width=400, height=300, max_words=50)

                    analyzer.all_tags.assert_called_once()
                    mock_wordcloud.assert_called_once()
                    mock_plt.figure.assert_called_once()
                    # The WordCloud.generate() method is called, so we need to check for that
                    mock_plt.imshow.assert_called_once()
                    # Check that imshow was called with the generated wordcloud
                    call_args = mock_plt.imshow.call_args
                    assert len(call_args[0]) > 0  # Should have at least one argument
                    mock_plt.axis.assert_called_once_with("off")
                    mock_plt.tight_layout.assert_called_once_with(pad=0)
                    mock_plt.show.assert_called_once()

    def test_database_connection_error(self):
        """Test handling of database connection errors."""
        analyzer = ZoteroAnalyzer(
            db_path="/nonexistent/path/db.sqlite",
            api_key="test-api-key",
            base_url="https://api.test.com",
            model="test-model",
        )

        with pytest.raises(sqlite3.OperationalError):
            analyzer.get_tags_with_tagid()
