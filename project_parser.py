"""
project_parser.py — Backward-compatible wrapper.
Project parsing is now handled fully inside entity_extractor.py → parse_projects().
This file re-exports parse_projects so any existing import still works.
"""

from entity_extractor import parse_projects

__all__ = ["parse_projects"]
