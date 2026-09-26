import httpx
import pytest

from catalogo_leituras_isbn.client import OpenLibraryError, fetch_book


def test_fetch_book_extracts_open_library_metadata():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["bibkeys"] == "ISBN:9780123"
        return httpx.Response(
            200,
            json={
                "ISBN:9780123": {
                    "title": "Livro de Teste",
                    "authors": [{"name": "Ana"}, {"name": "Beto"}],
                    "publish_date": "Publicado em 1999",
                    "cover": {"small": "https://covers.example/s.jpg"},
                }
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = fetch_book("9780123", client, endpoint="https://api.example/books")

    assert result == {
        "title": "Livro de Teste",
        "authors": ["Ana", "Beto"],
        "publication_year": "1999",
        "covers": {"small": "https://covers.example/s.jpg"},
    }


def test_fetch_book_returns_none_when_isbn_key_is_absent():
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}))) as client:
        result = fetch_book("9780123", client, endpoint="https://api.example/books")

    assert result is None


def test_fetch_book_converts_http_and_json_errors_to_domain_error():
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(503))) as client:
        with pytest.raises(OpenLibraryError, match="HTTP 503"):
            fetch_book("9780123", client, endpoint="https://api.example/books")

    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=b"not json"))) as client:
        with pytest.raises(OpenLibraryError, match="JSON inválida"):
            fetch_book("9780123", client, endpoint="https://api.example/books")
