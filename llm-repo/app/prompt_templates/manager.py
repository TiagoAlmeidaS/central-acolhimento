"""Prompt templates for entity extraction."""

from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any
import os

from app.core.config import settings


class PromptTemplateManager:
    """Manager for prompt templates."""

    def __init__(self, template_path: str = None):
        # Use absolute path for templates
        if template_path:
            self.template_path = template_path
        else:
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.template_path = current_dir
        
        self.env = Environment(
            loader=FileSystemLoader(self.template_path),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_template(self, template_name: str) -> Any:
        """Get a template by name."""
        return self.env.get_template(template_name)

    def render_entity_extraction(self, text: str) -> str:
        """Render entity extraction prompt."""
        template = self.get_template("entity_extraction.jinja2")
        return template.render(text=text)

    def render_validation(self, data: Dict[str, Any]) -> str:
        """Render validation prompt."""
        template = self.get_template("validation.jinja2")
        return template.render(data=data)
