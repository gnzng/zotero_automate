import os
from dotenv import load_dotenv

from zoteroanalyzer import ZoteroAnalyzer
from visualizer import ZoteroVisualizer


def load_config():
    """Load configuration from environment variables."""
    load_dotenv()

    config = {
        "ZOTERO_DB_PATH": os.getenv("ZOTERO_DB_PATH"),
        "CBORG_API_KEY": os.getenv("CBORG_API_KEY"),
        "CBORG_BASE_URL": os.getenv("CBORG_BASE_URL"),
        "CBORG_MODEL": os.getenv("CBORG_MODEL"),
    }

    # Validate configuration
    missing_vars = [key for key, value in config.items() if not value]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    return config


def create_analyzer(config):
    """Create and return a ZoteroAnalyzer instance."""
    return ZoteroAnalyzer(
        config["ZOTERO_DB_PATH"],
        config["CBORG_API_KEY"],
        config["CBORG_BASE_URL"],
        config["CBORG_MODEL"],
    )


def run_analysis(analyzer):
    """Run the main analysis workflow."""
    # Categorize the tags using the chat completions API
    categorized_content = analyzer.categorize_tags(save=True, for_obsidian_mardown=True)

    # Visualize the tags words in a word cloud
    analyzer.create_word_cloud(
        width=800, height=400, max_words=100, background_color="black", colormap="turbo"
    )

    # Save the unique tags in a text file for further analysis
    analyzer.unique_tags(save=True)

    # Get tag-to-titles mapping
    tag_to_titles = analyzer.get_tag_to_titles()

    # Create interactive visualizations
    visualizer = ZoteroVisualizer()
    categories = visualizer.parse_categorized_tags(categorized_content)

    # Create radar chart (still just tag counts)
    radar_path = visualizer.create_category_radar(categories)
    print(f"Radar chart saved to: {radar_path}")

    # Create enhanced network visualization with paper titles
    network_path = visualizer.create_simple_network(
        categories, tag_to_titles=tag_to_titles
    )
    print(f"Network visualization saved to: {network_path}")


def main():
    """Main entry point for the application."""
    try:
        # Load configuration
        config = load_config()

        # Create analyzer
        analyzer = create_analyzer(config)

        # Run analysis
        run_analysis(analyzer)

        print("Analysis completed successfully!")

    except Exception as e:
        print(f"Error during analysis: {e}")
        raise


if __name__ == "__main__":
    main()
