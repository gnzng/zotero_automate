import plotly.graph_objects as go
from typing import Dict, List
import re


class ZoteroVisualizer:
    """Simple visualization class for Zotero data using Plotly."""

    def __init__(self):
        """Initialize the visualizer."""
        pass

    def parse_categorized_tags(self, categorized_content: str) -> Dict[str, List[str]]:
        """
        Parse the categorized tags content into a structured format.

        :param categorized_content: String content from categorize_tags method
        :return: Dictionary with categories as keys and lists of tags as values
        """
        categories = {}
        current_category = None

        # Split by lines and process
        lines = categorized_content.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a category header (starts with #)
            if line.startswith("#"):
                current_category = line.lstrip("#").strip()
                categories[current_category] = []
            elif current_category and line:
                # Extract tags from the line (anything in [[...]])
                tags = re.findall(r"\[\[(.*?)\]\]", line)
                categories[current_category].extend(tags)

        return categories

    def create_category_radar(
        self, categories: Dict[str, List[str]], save_path: str = "category_radar.html"
    ) -> str:
        """
        Create a simple radar chart showing categories and their tag counts.

        :param categories: Dictionary with categories and their tags
        :param save_path: Path to save the HTML file
        :return: Path to the saved HTML file
        """
        # Prepare data for radar chart
        category_names = list(categories.keys())
        tag_counts = [len(tags) for tags in categories.values()]

        # Create radar chart
        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=tag_counts,
                theta=category_names,
                fill="toself",
                name="Tag Count",
                line_color="rgb(32, 201, 151)",
                fillcolor="rgba(32, 201, 151, 0.3)",
            )
        )

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(tag_counts) + 2])),
            showlegend=True,
            title="Zotero Categories - Tag Distribution",
            title_x=0.5,
            font=dict(size=14),
        )

        # Save to HTML file
        fig.write_html(save_path)
        return save_path

    def create_simple_network(
        self,
        categories: Dict[str, List[str]],
        tag_to_titles: Dict[str, List[str]] = None,
        save_path: str = "category_network.html",
    ) -> str:
        """
        Create a simple network visualization showing categories and tags, with paper titles on hover
        and node size by paper count.

        :param categories: Dictionary with categories and their tags
        :param tag_to_titles: Dictionary mapping tag names to lists of paper titles
        :param save_path: Path to save the HTML file
        :return: Path to the saved HTML file
        """
        if tag_to_titles is None:
            tag_to_titles = {}
        nodes = []
        edges = []

        # Build category to paper titles mapping
        category_to_titles = {}
        for category, tags in categories.items():
            paper_set = set()
            for tag in tags:
                paper_set.update(tag_to_titles.get(tag, []))
            category_to_titles[category] = sorted(paper_set)

        # Add category nodes
        for i, category in enumerate(categories.keys()):
            paper_titles = category_to_titles[category]
            nodes.append(
                {
                    "id": category,
                    "label": category,
                    "group": "category",
                    "size": 20 + 5 * len(paper_titles),
                    "hovertext": (
                        "<br>".join(paper_titles) if paper_titles else "No papers"
                    ),
                }
            )

        # Add tag nodes and edges
        tag_id = 0
        for category, tags in categories.items():
            for tag in tags:
                tag_name = f"tag_{tag_id}"
                tag_papers = tag_to_titles.get(tag, [])
                nodes.append(
                    {
                        "id": tag_name,
                        "label": tag,
                        "group": "tag",
                        "size": 10 + 2 * len(tag_papers),
                        "hovertext": (
                            "<br>".join(tag_papers) if tag_papers else "No papers"
                        ),
                    }
                )
                edges.append({"from": category, "to": tag_name})
                tag_id += 1

        # Create network using plotly
        fig = go.Figure()

        # Add edges
        for edge in edges:
            fig.add_trace(
                go.Scatter(
                    x=[],
                    y=[],
                    mode="lines",
                    line=dict(width=0.5, color="#888"),
                    hoverinfo="none",
                    showlegend=False,
                )
            )

        # Add nodes
        category_nodes = [n for n in nodes if n["group"] == "category"]
        tag_nodes = [n for n in nodes if n["group"] == "tag"]

        # Position nodes in a circle
        import math

        # Position categories in outer circle
        category_positions = {}
        for i, node in enumerate(category_nodes):
            angle = 2 * math.pi * i / len(category_nodes)
            x = 2 * math.cos(angle)
            y = 2 * math.sin(angle)
            category_positions[node["id"]] = (x, y)

        # Position tags around their categories
        tag_positions = {}
        for edge in edges:
            if edge["to"] not in tag_positions:
                cat_x, cat_y = category_positions[edge["from"]]
                import random

                angle = random.uniform(0, 2 * math.pi)
                radius = 0.8
                x = cat_x + radius * math.cos(angle)
                y = cat_y + radius * math.sin(angle)
                tag_positions[edge["to"]] = (x, y)

        # Add category nodes
        cat_x = [category_positions[n["id"]][0] for n in category_nodes]
        cat_y = [category_positions[n["id"]][1] for n in category_nodes]
        cat_labels = [n["label"] for n in category_nodes]
        cat_sizes = [n["size"] for n in category_nodes]
        cat_hover = [n["hovertext"] for n in category_nodes]

        fig.add_trace(
            go.Scatter(
                x=cat_x,
                y=cat_y,
                mode="markers+text",
                marker=dict(size=cat_sizes, color="red"),
                text=cat_labels,
                textposition="middle center",
                name="Categories",
                textfont=dict(size=12, color="white"),
                hovertext=cat_hover,
                hoverinfo="text",
            )
        )

        # Add tag nodes
        tag_x = [tag_positions[n["id"]][0] for n in tag_nodes]
        tag_y = [tag_positions[n["id"]][1] for n in tag_nodes]
        tag_labels = [n["label"] for n in tag_nodes]
        tag_sizes = [n["size"] for n in tag_nodes]
        tag_hover = [n["hovertext"] for n in tag_nodes]

        fig.add_trace(
            go.Scatter(
                x=tag_x,
                y=tag_y,
                mode="markers+text",
                marker=dict(size=tag_sizes, color="blue"),
                text=tag_labels,
                textposition="middle center",
                name="Tags",
                textfont=dict(size=8),
                hovertext=tag_hover,
                hoverinfo="text",
            )
        )

        # Update layout
        fig.update_layout(
            title="Zotero Categories and Tags Network",
            title_x=0.5,
            showlegend=True,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )

        # Save to HTML file
        fig.write_html(save_path)
        return save_path
