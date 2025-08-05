from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import re
import ast
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class LanguageHandler(ABC):
    """
    Strategy interface for language-specific implementations.
    """

    @abstractmethod
    def extract_functions_from_diff(self, diff: str, file_map: Dict[str, str]) -> List[Dict[str, str]]:
        """Return list of {"filename": ..., "function_name": ...} for functions touched by the diff."""

    @abstractmethod
    def get_call_graph(self, file_map: Dict[str, str]) -> Dict[str, List[str]]:
        """Return a mapping full_fn_name -> list of called function names."""

    @abstractmethod
    def fetch_function_context(self, fn: Dict[str, str], file_map: Dict[str, str], call_graph: Dict[str, List[str]]) -> str:
        """Return source + context string for the given function reference."""