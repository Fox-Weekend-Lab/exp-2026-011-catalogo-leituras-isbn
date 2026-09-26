"""Interface de linha de comando do catálogo de leituras."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import httpx

from .catalog import build_catalog, normalize_isbns
from .client import OpenLibraryError, fetch_book

Lookup = Callable[[str], dict[str, Any] | None]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera um catálogo JSON a partir de ISBNs em um arquivo texto."
    )
    parser.add_argument("input_file", metavar="entrada.txt", help="arquivo com um ISBN por linha")
    parser.add_argument("output_file", metavar="catalogo.json", help="arquivo JSON de saída")
    return parser


def _read_isbns(path: Path) -> list[str]:
    try:
        return normalize_isbns(path.read_text(encoding="utf-8").splitlines())
    except FileNotFoundError as exc:
        raise ValueError(f"O arquivo de entrada não foi encontrado: {path}.") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"O arquivo de entrada deve estar codificado em UTF-8: {path}.") from exc
    except OSError as exc:
        raise ValueError(f"Não foi possível ler o arquivo de entrada: {path}.") from exc


def _write_catalog(path: Path, document: dict[str, list[Any]]) -> None:
    if not path.parent.is_dir():
        raise ValueError(
            f"O diretório de saída não existe: {path.parent}. Crie-o antes de executar o comando."
        )
    try:
        with path.open("w", encoding="utf-8") as output:
            json.dump(document, output, ensure_ascii=False, indent=2)
            output.write("\n")
    except OSError as exc:
        raise ValueError(f"Não foi possível gravar o arquivo de saída: {path}.") from exc


def main(argv: Sequence[str] | None = None, lookup: Lookup | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        isbns = _read_isbns(Path(args.input_file))
        if lookup is None:
            with httpx.Client() as client:
                document = build_catalog(isbns, lambda isbn: fetch_book(isbn, client))
        else:
            document = build_catalog(isbns, lookup)
        _write_catalog(Path(args.output_file), document)
    except (ValueError, OpenLibraryError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
