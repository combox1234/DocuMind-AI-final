"""Core package with lazy imports to avoid heavy side-effects on import.

Avoid importing heavy modules (like LLM/Ollama) at package import time.
This enables lightweight imports such as `from core.classifier import DocumentClassifier`
without initializing the LLM stack or other expensive dependencies.
"""

from typing import Any
import importlib

__all__ = ['DatabaseManager', 'LLMService', 'FileProcessor']

def __getattr__(name: str) -> Any:
	if name == 'DatabaseManager':
		return importlib.import_module('.database', __name__).DatabaseManager
	if name == 'LLMService':
		return importlib.import_module('.llm', __name__).LLMService
	if name == 'FileProcessor':
		return importlib.import_module('.processor', __name__).FileProcessor
	raise AttributeError(f"module 'core' has no attribute {name!r}")
