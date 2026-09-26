import json

from catalogo_leituras_isbn.__main__ import main


def test_cli_writes_catalog_with_injected_lookup(tmp_path):
    input_file = tmp_path / "isbns.txt"
    output_file = tmp_path / "catalog.json"
    input_file.write_text("978-0-123\n999\n9780123\n", encoding="utf-8")

    def lookup(isbn: str):
        if isbn == "9780123":
            return {
                "title": "Livro",
                "authors": [],
                "publication_year": None,
                "covers": {},
            }
        return None

    assert main([str(input_file), str(output_file)], lookup=lookup) == 0
    assert json.loads(output_file.read_text(encoding="utf-8")) == {
        "catalog": [
            {
                "isbn": "9780123",
                "title": "Livro",
                "authors": [],
                "publication_year": None,
                "covers": {},
            }
        ],
        "not_found": ["999"],
    }


def test_cli_reports_missing_input_file(tmp_path, capsys):
    missing = tmp_path / "ausente.txt"
    output_file = tmp_path / "catalog.json"

    assert main([str(missing), str(output_file)], lookup=lambda isbn: None) == 1
    assert "arquivo de entrada não foi encontrado" in capsys.readouterr().err
