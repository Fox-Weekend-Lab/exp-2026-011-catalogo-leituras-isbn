"""Regras puras para normalização e montagem do catálogo."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping
from typing import Any

BookLookup = Callable[[str], Mapping[str, Any] | None]


def normalize_isbns(lines: Iterable[str]) -> list[str]:
    """Remove espaços, hífens, linhas vazias e duplicatas, mantendo a ordem."""
    normalized: list[str] = []
    seen: set[str] = set()

    for line in lines:
        isbn = re.sub(r"[\s-]+", "", line)
        if isbn and isbn not in seen:
            normalized.append(isbn)
            seen.add(isbn)

    return normalized


def build_catalog(isbns: Iterable[str], lookup: BookLookup) -> dict[str, list[Any]]:
    """Consulta ISBNs normalizados e separa registros encontrados dos ausentes."""
    catalog: list[dict[str, Any]] = []
    not_found: list[str] = []

    for isbn in isbns:
        book = lookup(isbn)
        if book is None:
            not_found.append(isbn)
            continue

        catalog.append(
            {
                "isbn": isbn,
                "title": book["title"],
                "authors": book["authors"],
                "publication_year": book["publication_year"],
                "covers": book["covers"],
            }
        )

    return {"catalog": catalog, "not_found": not_found}
