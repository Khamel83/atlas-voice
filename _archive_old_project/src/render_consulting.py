#!/usr/bin/env python3
"""
OOS Consultant Rendering System
Jinja2-based rendering for consulting artifacts
"""

import csv
import yaml
from typing import Dict, Any, List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
import logging

logger = logging.getLogger(__name__)

class ConsultingRenderer:
    """Render consulting artifacts using Jinja2 templates"""

    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    async def render_a3(self, a3_data: Dict[str, Any], output_path: Path) -> Path:
        """Render A3 problem-solving framework"""
        try:
            template = self.env.get_template("a3.md.j2")
            content = template.render(**a3_data)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"A3 rendered to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to render A3: {e}")
            raise

    async def render_issue_tree(self, issue_tree: Dict[str, Any], output_path: Path) -> Path:
        """Render MECE issue tree"""
        try:
            # For issue tree, we output YAML directly
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(issue_tree, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Issue tree rendered to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to render issue tree: {e}")
            raise

    async def render_ost(self, ost_data: Dict[str, Any], output_path: Path) -> Path:
        """Render Opportunity Solution Tree as Mermaid"""
        try:
            template = self.env.get_template("ost.mmd.j2")
            content = template.render(**ost_data)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"OST rendered to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to render OST: {e}")
            raise

    async def render_impact_effort(self, matrix_data: List[Dict[str, Any]], output_path: Path) -> Path:
        """Render Impact/Effort matrix as CSV"""
        try:
            template = self.env.get_template("impact_effort.csv.j2")
            content = template.render(matrix=matrix_data)

            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)

            logger.info(f"Impact/Effort matrix rendered to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to render Impact/Effort matrix: {e}")
            raise

    async def render_rice(self, rice_data: List[Dict[str, Any]], output_path: Path) -> Path:
        """Render RICE scores as CSV"""
        try:
            template = self.env.get_template("rice.csv.j2")
            content = template.render(scores=rice_data)

            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)

            logger.info(f"RICE scores rendered to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to render RICE scores: {e}")
            raise

    async def render_plan(self, plan_data: Dict[str, Any], output_path: Path) -> Path:
        """Render execution plan"""
        try:
            template = self.env.get_template("plan.md.j2")
            content = template.render(**plan_data)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Plan rendered to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to render plan: {e}")
            raise

    async def render_all_artifacts(self, artifacts_data: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
        """Render all consulting artifacts"""
        rendered = {}

        # Render A3
        if "a3_data" in artifacts_data:
            a3_path = output_dir / "a3.md"
            rendered["a3"] = await self.render_a3(artifacts_data["a3_data"], a3_path)

        # Render issue tree
        if "issue_tree" in artifacts_data:
            issues_path = output_dir / "issues.yaml"
            rendered["issue_tree"] = await self.render_issue_tree(artifacts_data["issue_tree"], issues_path)

        # Render OST
        if "ost_data" in artifacts_data:
            ost_path = output_dir / "ost.mmd"
            rendered["ost"] = await self.render_ost(artifacts_data["ost_data"], ost_path)

        # Render Impact/Effort
        if "ie_matrix" in artifacts_data:
            ie_path = output_dir / "impact_effort.csv"
            rendered["impact_effort"] = await self.render_impact_effort(artifacts_data["ie_matrix"], ie_path)

        # Render RICE
        if "rice_scores" in artifacts_data:
            rice_path = output_dir / "rice.csv"
            rendered["rice"] = await self.render_rice(artifacts_data["rice_scores"], rice_path)

        # Render plan
        if "plan_data" in artifacts_data:
            plan_path = output_dir / "plan.md"
            rendered["plan"] = await self.render_plan(artifacts_data["plan_data"], plan_path)

        return rendered

# Template filters
def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.1%}"

def format_currency(value: float) -> str:
    """Format value as currency"""
    return f"${value:,.0f}"

def format_quadrant_color(quadrant: str) -> str:
    """Get color for quadrant"""
    colors = {
        "Quick Wins": "#22c55e",
        "Big Bets": "#3b82f6",
        "Fill-Ins": "#f59e0b",
        "Money Pits": "#ef4444"
    }
    return colors.get(quadrant, "#6b7280")

def format_priority_score(score: float) -> str:
    """Format priority score with color"""
    if score >= 8:
        return f"🟢 {score:.1f}"
    elif score >= 6:
        return f"🟡 {score:.1f}"
    else:
        return f"🔴 {score:.1f}"

# Register filters
def setup_template_filters(env: Environment):
    """Setup custom template filters"""
    env.filters['percentage'] = format_percentage
    env.filters['currency'] = format_currency
    env.filters['quadrant_color'] = format_quadrant_color
    env.filters['priority_score'] = format_priority_score

# Utility functions for template rendering
def create_template_context(additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create template context with common data"""
    context = {
        "current_date": "2025-09-28",
        "generated_by": "OOS Consultant",
        "version": "1.0"
    }

    if additional_data:
        context.update(additional_data)

    return context

def validate_template_data(template_name: str, data: Dict[str, Any]) -> bool:
    """Validate data for template rendering"""
    required_fields = {
        "a3.md.j2": ["title", "background", "current_state", "target_state"],
        "ost.mmd.j2": ["outcome", "opportunities"],
        "plan.md.j2": ["milestones", "portfolio"],
        "impact_effort.csv.j2": ["matrix"],
        "rice.csv.j2": ["scores"]
    }

    if template_name not in required_fields:
        return True

    fields = required_fields[template_name]
    return all(field in data for field in fields)

# CSV rendering utilities
def render_csv_row(data: Dict[str, Any], fieldnames: List[str]) -> str:
    """Render single CSV row"""
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writerow(data)
    return output.getvalue()

def render_csv_header(fieldnames: List[str]) -> str:
    """Render CSV header"""
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    return output.getvalue()

# YAML rendering utilities
def render_yaml_comment(comment: str) -> str:
    """Render YAML comment"""
    return f"# {comment}\n"

def render_yaml_section(title: str, data: Dict[str, Any]) -> str:
    """Render YAML section"""
    content = f"\n{title}:\n"
    for key, value in data.items():
        content += f"  {key}: {value}\n"
    return content

# Mermaid rendering utilities
def render_mermaid_header(title: str) -> str:
    """Render Mermaid diagram header"""
    return f"%% {title}\n"

def render_mermaid_node(node_id: str, label: str, style: str = "") -> str:
    """Render Mermaid node"""
    if style:
        return f"{node_id}[\"{label}\"]:::{style}\n"
    return f"{node_id}[\"{label}\"]\n"

def render_mermaid_edge(from_node: str, to_node: str, label: str = "") -> str:
    """Render Mermaid edge"""
    if label:
        return f"{from_node} -->|{label}| {to_node}\n"
    return f"{from_node} --> {to_node}\n"

def render_mermaid_styles(styles: Dict[str, str]) -> str:
    """Render Mermaid styles"""
    content = "\nclassDef "
    for style_class, properties in styles.items():
        content += f"{style_class} {properties}\n"
    return content

# Markdown rendering utilities
def render_markdown_header(title: str, level: int = 1) -> str:
    """Render markdown header"""
    return f"{'#' * level} {title}\n\n"

def render_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """Render markdown table"""
    # Header row
    table = "| " + " | ".join(headers) + " |\n"
    # Separator row
    table += "|" + "|".join(["---"] * len(headers)) + "|\n"
    # Data rows
    for row in rows:
        table += "| " + " | ".join(row) + " |\n"
    return table + "\n"

def render_markdown_list(items: List[str], ordered: bool = False) -> str:
    """Render markdown list"""
    if ordered:
        return "".join([f"{i+1}. {item}\n" for i, item in enumerate(items)])
    else:
        return "".join([f"- {item}\n" for item in items])

def render_markdown_code_block(code: str, language: str = "") -> str:
    """Render markdown code block"""
    return f"```{language}\n{code}\n```\n\n"