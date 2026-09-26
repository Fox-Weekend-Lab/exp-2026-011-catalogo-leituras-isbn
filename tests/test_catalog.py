from catalogo_leituras_isbn.catalog import build_catalog, normalize_isbns


def test_normalize_isbns_removes_whitespace_hyphens_and_duplicates():
    lines = [" 978-0-123 ", "", "9780123", "  0-321 ", "\t"]

    assert normalize_isbns(lines) == ["9780123", "0321"]


def test_build_catalog_separates_found_and_missing_isbns():
    records = {
        "111": {
            "title": "Livro A",
            "authors": ["Autora"],
            "publication_year": "2020",
            "covers": {"medium": "https://covers.example/a.jpg"},
        }
    }

    document = build_catalog(["111", "222"], records.get)

    assert document == {
        "catalog": [{"isbn": "111", **records["111"]}],
        "not_found": ["222"],
    }
