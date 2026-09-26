"""Ferramentas para gerar catálogos de leituras por ISBN."""

from .catalog import build_catalog, normalize_isbns
from .client import OpenLibraryError, fetch_book

__all__ = ["OpenLibraryError", "build_catalog", "fetch_book", "normalize_isbns"]
