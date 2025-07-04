# Zotero Automation

A Python tool for analyzing Zotero library tags using AI categorization and visualization.

## Features

- Extract and analyze tags from Zotero SQLite database
- AI-powered tag categorization using OpenAI API
- Generate word clouds from tags
- Export categorized tags in Obsidian markdown format
- Save unique tags for further analysis

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd zotero_automate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env-example .env
# Edit .env with your actual values
```

## Usage

Run the main analysis:
```bash
python main.py
```

## Testing

The project includes comprehensive tests using pytest. Here's how to run them:

### Install test dependencies
```bash
pip install -r requirements.txt
```

### Run all tests
```bash
# Using pytest directly
pytest

# Using the test runner script
python run_tests.py
```

### Run specific tests
```bash
# Run only main module tests
pytest tests/test_main.py

# Run only ZoteroAnalyzer tests
pytest tests/test_zoteroanalyzer.py

# Run a specific test function
pytest tests/test_main.py::TestLoadConfig::test_load_config_success
```

### Run tests with coverage
```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html to view coverage report
```

### Test Features

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test database interactions with temporary SQLite databases
- **Mock Tests**: Test API calls without making actual network requests
- **Error Handling**: Test various error conditions and edge cases
- **Coverage Reporting**: Generate HTML coverage reports

### Test Structure

```
tests/
├── __init__.py
├── test_main.py          # Tests for main.py functions
└── test_zoteroanalyzer.py # Tests for ZoteroAnalyzer class
```

## Configuration

Create a `.env` file with the following variables:
- `ZOTERO_DB_PATH`: Path to your Zotero SQLite database
- `CBORG_API_KEY`: Your OpenAI API key
- `CBORG_BASE_URL`: OpenAI API base URL
- `CBORG_MODEL`: OpenAI model name to use

## Output Files

- `unique_tags.txt`: List of unique tags from your library
- `categorized_tags.md`: AI-categorized tags in markdown format
- Word cloud visualization (displayed)

## Contributing

1. Write tests for new features
2. Ensure all tests pass before submitting
3. Follow the existing code structure and style
