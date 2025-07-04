import pytest
import os
from unittest.mock import patch, MagicMock
from main import load_config, create_analyzer, run_analysis, main


class TestLoadConfig:
    """Test the load_config function."""

    @patch.dict(
        os.environ,
        {
            "ZOTERO_DB_PATH": "/test/path/db.sqlite",
            "CBORG_API_KEY": "test-api-key",
            "CBORG_BASE_URL": "https://api.test.com",
            "CBORG_MODEL": "test-model",
        },
    )
    def test_load_config_success(self):
        """Test successful configuration loading."""
        config = load_config()

        assert config["ZOTERO_DB_PATH"] == "/test/path/db.sqlite"
        assert config["CBORG_API_KEY"] == "test-api-key"
        assert config["CBORG_BASE_URL"] == "https://api.test.com"
        assert config["CBORG_MODEL"] == "test-model"

    @patch("main.load_dotenv")
    def test_load_config_missing_variables(self, mock_load_dotenv):
        """Test configuration loading with missing environment variables."""
        # Mock load_dotenv to do nothing, then clear environment variables
        mock_load_dotenv.return_value = None
        original_env = os.environ.copy()
        try:
            os.environ.clear()
            with pytest.raises(
                ValueError, match="Missing required environment variables"
            ):
                load_config()
        finally:
            os.environ.update(original_env)

    def test_load_config_empty_variable(self):
        """Test configuration loading with empty environment variable."""
        with patch.dict(
            os.environ,
            {
                "ZOTERO_DB_PATH": "/test/path/db.sqlite",
                "CBORG_API_KEY": "",
                "CBORG_BASE_URL": "https://api.test.com",
                "CBORG_MODEL": "test-model",
            },
        ):
            with pytest.raises(
                ValueError, match="Missing required environment variables"
            ):
                load_config()


class TestCreateAnalyzer:
    """Test the create_analyzer function."""

    def test_create_analyzer(self):
        """Test analyzer creation."""
        config = {
            "ZOTERO_DB_PATH": "/test/path/db.sqlite",
            "CBORG_API_KEY": "test-api-key",
            "CBORG_BASE_URL": "https://api.test.com",
            "CBORG_MODEL": "test-model",
        }

        analyzer = create_analyzer(config)

        assert analyzer.db_path == "/test/path/db.sqlite"
        assert analyzer.api_key == "test-api-key"
        assert analyzer.base_url == "https://api.test.com"
        assert analyzer.model == "test-model"


class TestRunAnalysis:
    """Test the run_analysis function."""

    def test_run_analysis(self):
        """Test the analysis workflow."""
        mock_analyzer = MagicMock()

        run_analysis(mock_analyzer)

        # Verify all expected methods were called
        mock_analyzer.categorize_tags.assert_called_once_with(
            save=True, for_obsidian_mardown=True
        )
        mock_analyzer.create_word_cloud.assert_called_once_with(
            width=800,
            height=400,
            max_words=100,
            background_color="black",
            colormap="turbo",
        )
        mock_analyzer.unique_tags.assert_called_once_with(save=True)


class TestMain:
    """Test the main function."""

    @patch("main.load_config")
    @patch("main.create_analyzer")
    @patch("main.run_analysis")
    def test_main_success(
        self, mock_run_analysis, mock_create_analyzer, mock_load_config
    ):
        """Test successful main execution."""
        mock_config = {"test": "config"}
        mock_analyzer = MagicMock()

        mock_load_config.return_value = mock_config
        mock_create_analyzer.return_value = mock_analyzer

        main()

        mock_load_config.assert_called_once()
        mock_create_analyzer.assert_called_once_with(mock_config)
        mock_run_analysis.assert_called_once_with(mock_analyzer)

    @patch("main.load_config")
    def test_main_config_error(self, mock_load_config):
        """Test main function with configuration error."""
        mock_load_config.side_effect = ValueError("Config error")

        with pytest.raises(ValueError, match="Config error"):
            main()

    @patch("main.load_config")
    @patch("main.create_analyzer")
    def test_main_analyzer_error(self, mock_create_analyzer, mock_load_config):
        """Test main function with analyzer creation error."""
        mock_load_config.return_value = {"test": "config"}
        mock_create_analyzer.side_effect = Exception("Analyzer error")

        with pytest.raises(Exception, match="Analyzer error"):
            main()
