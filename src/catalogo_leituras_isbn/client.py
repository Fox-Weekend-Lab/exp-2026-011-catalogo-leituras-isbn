"""Cliente HTTP para a API pública Open Library."""

from __future__ import annotations

import os
import re
from typing import Any

import httpx

OPEN_LIBRARY_API_URL = "https://openlibrary.org/api/books"


class OpenLibraryError(RuntimeError):
    """Erro operacional seguro ao consultar a Open Library."""


def _publication_year(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = re.search(r"\b\d{4}\b", value)
    return match.group(0) if match else None


def _record_from_response(data: dict[str, Any], isbn: str) -> dict[str, Any] | None:
    item = data.get(f"ISBN:{isbn}")
    if not isinstance(item, dict):
        return None

    authors = [
        author["name"]
        for author in item.get("authors", [])
        if isinstance(author, dict) and isinstance(author.get("name"), str)
    ]
    cover = item.get("cover", {})
    covers = {
        size: url
        for size, url in cover.items()
        if isinstance(cover, dict) and isinstance(size, str) and isinstance(url, str)
    }

    return {
        "title": item.get("title") if isinstance(item.get("title"), str) else None,
        "authors": authors,
        "publication_year": _publication_year(item.get("publish_date")),
        "covers": covers,
    }


def fetch_book(
    isbn: str,
    client: httpx.Client | None = None,
    endpoint: str | None = None,
) -> dict[str, Any] | None:
    """Busca um ISBN e retorna seus metadados, ou ``None`` quando ausente."""
    api_url = endpoint or os.getenv("OPEN_LIBRARY_API_URL", OPEN_LIBRARY_API_URL)
    params = {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}
    owns_client = client is None
    active_client = client or httpx.Client()

    try:
        try:
            response = active_client.get(api_url, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise OpenLibraryError(
                f"A Open Library respondeu com erro HTTP {status}. Tente novamente mais tarde."
            ) from exc
        except httpx.HTTPError as exc:
            raise OpenLibraryError(
                "Não foi possível consultar a Open Library. Verifique sua conexão e tente novamente."
            ) from exc

        try:
            payload = response.json()
        except (ValueError, TypeError) as exc:
            raise OpenLibraryError(
                "A Open Library retornou uma resposta JSON inválida. Tente novamente mais tarde."
            ) from exc

        if not isinstance(payload, dict):
            raise OpenLibraryError(
                "A Open Library retornou uma resposta JSON inválida. Tente novamente mais tarde."
            )
        return _record_from_response(payload, isbn)
    finally:
        if owns_client:
            active_client.close()
