# Catálogo de Leituras por ISBN

> Este projeto foi gerado automaticamente por IA e revisado por um agente automatizado, nao por uma pessoa. Leia o codigo antes de usar.

## Descrição

Ferramenta de linha de comando em Python que lê ISBNs de um arquivo texto, consulta a API pública Open Library e grava um documento JSON com os livros encontrados e os códigos não localizados.

## Objetivo

Automatizar a consulta de metadados bibliográficos a partir de uma lista de ISBNs, produzindo uma saída estruturada com título, autores, ano de publicação, capas disponíveis e a relação de ISBNs sem registro retornado pela API.

## Como funciona

1. O programa lê um arquivo UTF-8 com um ISBN por linha.
2. Remove espaços e hífens dos valores, ignora linhas vazias e elimina ISBNs repetidos, mantendo a primeira ocorrência.
3. Para cada ISBN normalizado, faz uma consulta à Open Library no endpoint de livros.
4. Quando há registro, extrai `title`, `authors`, `publication_year` e `covers`.
5. Quando a resposta não contém a chave do ISBN consultado, inclui o código em `not_found`.
6. Grava um único arquivo JSON, com as chaves `catalog` e `not_found`.

O ano de publicação é o primeiro trecho de quatro dígitos encontrado em `publish_date`. Campos ausentes ou incompletos podem resultar em `null`, listas vazias ou objetos vazios, conforme o campo.

## Arquitetura

- `requirements.txt`: arquivo de dependências do experimento.
- `src/catalogo_leituras_isbn/__init__.py`: expõe as funções públicas de normalização, montagem de catálogo e consulta.
- `src/catalogo_leituras_isbn/__main__.py`: implementa a interface de linha de comando, leitura da entrada e gravação do JSON.
- `src/catalogo_leituras_isbn/catalog.py`: contém as regras de normalização de ISBNs e montagem do documento final.
- `src/catalogo_leituras_isbn/client.py`: contém o cliente HTTP da Open Library e a conversão da resposta para os metadados usados pelo catálogo.
- `tests/conftest.py`: configuração compartilhada dos testes.
- `tests/test_catalog.py`: testes das regras de catálogo.
- `tests/test_cli.py`: testes da interface de linha de comando.
- `tests/test_client.py`: testes do cliente da Open Library.

## Tecnologias

- Python 3.11+
- `httpx`, para consultas HTTP à API Open Library
- Biblioteca padrão do Python: `argparse`, `json`, `pathlib`, `re` e `os`
- `pytest`, fornecido pelo ambiente de execução, para rodar os testes

## Instalação

Use Python 3.11 ou superior. Instale as dependências do experimento com:

```bash
python -m pip install -r requirements.txt
```

O pacote está em `src/` e o projeto não possui arquivo de instalação. Portanto, é necessário incluir `src/` em `PYTHONPATH` ao executar o módulo.

## Configuração

A consulta usa a API pública Open Library e não requer credencial.

Variável de ambiente lida pelo código:

- `OPEN_LIBRARY_API_URL`: sobrescreve a URL da API consultada. Valor padrão: `https://openlibrary.org/api/books`.

## Uso

O comando recebe dois argumentos posicionais:

1. o caminho para o arquivo de entrada com ISBNs;
2. o caminho para o arquivo JSON de saída.

O diretório pai do arquivo de saída precisa existir previamente.

Linux/macOS:

```bash
PYTHONPATH=src python -m catalogo_leituras_isbn entrada.txt catalogo.json
```

Windows (PowerShell):

```powershell
$env:PYTHONPATH="src"; python -m catalogo_leituras_isbn entrada.txt catalogo.json
```

Em caso de arquivo de entrada inexistente, conteúdo que não esteja em UTF-8, diretório de saída inexistente ou falha na consulta, o programa escreve uma mensagem em português no erro padrão e encerra com código diferente de zero.

## Exemplos

Um arquivo de entrada pode conter ISBNs com espaços, hífens, linhas vazias ou repetições:

```text
978-0-000-00000-0
978 0 000 00000 0

9780000000001
```

Após a normalização, o primeiro e o segundo valores representam o mesmo ISBN e somente a primeira ocorrência é consultada.

O JSON gerado segue esta estrutura:

```json
{
  "catalog": [
    {
      "isbn": "9780000000000",
      "title": "Título retornado pela Open Library",
      "authors": [
        "Autora ou autor retornado pela Open Library"
      ],
      "publication_year": "2000",
      "covers": {
        "medium": "https://..."
      }
    }
  ],
  "not_found": [
    "9780000000001"
  ]
}
```

Os valores bibliográficos dependem da resposta da Open Library. `title` e `publication_year` podem ser `null`; `authors` e `covers` podem estar vazios.

## Testes

Execute os testes com:

```bash
python -m pytest
```

Os testes não acessam a rede: as respostas HTTP são dubladas.

## Limitações

- A consulta é feita individualmente para cada ISBN, sem processamento em lote, paralelismo, cache ou tentativas automáticas.
- A disponibilidade e a qualidade dos metadados dependem da Open Library.
- A normalização remove apenas espaços e hífens; não valida checksum e não converte ISBN-10 para ISBN-13, ou vice-versa.
- O relatório de itens ausentes está no campo `not_found` do mesmo JSON, sem arquivo de relatório separado.
- Não há interface web, banco de dados, autenticação, edição manual de metadados ou validação bibliográfica adicional.
- O programa exige que o diretório pai do arquivo de saída já exista.

## O que foi aprendido

O experimento demonstra como separar regras puras de normalização e montagem de dados da camada de I/O e da integração HTTP. Também exercita o tratamento de respostas incompletas, erros HTTP, falhas de transporte e JSON inválido com mensagens seguras para a pessoa usuária. A possibilidade de fornecer um cliente `httpx.Client` ao consultor permite testar a integração sem chamadas reais à rede.

## Possível aplicação na FOX

Pode apoiar a conferência de acervos, listas de livros para campanhas e inventários editoriais. O JSON gerado oferece uma base reproduzível para etapas posteriores de curadoria ou publicação.

## Status

O relatório de testes recebido informa que a execução passou: 7 testes foram coletados e os 7 testes passaram.
