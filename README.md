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

## Testes e lint

```bash
pytest
ruff check . && ruff format --check .
```
