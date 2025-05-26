"""
Configuration management for the Menu Planner application.

This module centralizes all configuration settings and provides
a single source of truth for application configuration.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR.parent.parent / "output"

class LLMConfig(BaseModel):
    """Configuration for language models used in the application."""
    model_name: str = Field(
        default="gpt-4.1-mini",
        description="Default model name for agents when not specified"
    )
    temperature: float = Field(
        default=0.7, 
        description="Default temperature for model generations"
    )
    timeout: int = Field(
        default=300,
        description="Default timeout for model calls in seconds"
    )

class FamilyConfig(BaseModel):
    """Configuration for family details used in menu planning."""
    adults: int = Field(
        default=int(os.getenv("ADULTS", "2")),
        description="Number of adults in the family"
    )
    children: int = Field(
        default=int(os.getenv("CHILDREN", "1")),
        description="Number of children in the family"
    )
    children_age: str = Field(
        default=os.getenv("CHILDREN_AGE", "10"),
        description="Age of the children"
    )
    email: str = Field(
        default=os.getenv("MAILTO", ""),
        description="Email address to send menu to"
    )

class AppConfig(BaseModel):
    """Main application configuration."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    family: FamilyConfig = Field(default_factory=FamilyConfig)
    single_recipe: Optional[str] = Field(
        default="",
        description="If set, generates only this single recipe instead of a full menu"
    )
    debug: bool = Field(
        default=bool(os.getenv("DEBUG", "False").lower() == "true"),
        description="Enable debug mode with additional logging"
    )

# Create and export the application configuration
config = AppConfig()
