# mini-conta-digital

API REST de conta digital feita **para estudo** (não é um sistema bancário real).
README completo será escrito na etapa final.

## Rodar local

```bash
python3 -m venv .venv
source .venv/bin/activate          # fish: source .venv/bin/activate.fish
pip install -r requirements-dev.txt
uvicorn app.main:app --reload      # docs interativas em http://127.0.0.1:8000/docs
```

## Rodar com Docker

```bash
docker build -t mini-conta-digital:dev .
docker run --rm -p 8000:8000 mini-conta-digital:dev
# docs interativas em http://127.0.0.1:8000/docs  (Ctrl+C para parar)
```

Ou, com docker compose:

```bash
docker compose up --build
```

## Testes e lint

```bash
pytest
ruff check . && ruff format --check .
```
