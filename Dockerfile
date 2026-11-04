# Imagem base "slim": Python oficial sem as ferramentas extras do Debian (bem menor).
FROM python:3.12-slim

# PYTHONDONTWRITEBYTECODE: não gera arquivos .pyc dentro da imagem.
# PYTHONUNBUFFERED: logs saem na hora no `docker logs`, sem ficar presos em buffer.
# PIP_NO_CACHE_DIR: o cache do pip não serve de nada dentro da imagem final.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Usuário sem privilégios: se alguém invadir a aplicação, não ganha root no container.
RUN useradd --system --uid 10001 --no-create-home appuser

# 1) Copia SÓ a lista de dependências e instala.
#    Cada instrução vira uma "camada" em cache. Enquanto requirements.txt não mudar,
#    o Docker reaproveita esta camada e não reinstala tudo a cada alteração no código.
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2) Só depois copia o código (que muda o tempo todo). Ordem importa para o cache.
COPY app ./app

USER appuser

EXPOSE 8000

# 0.0.0.0 = aceitar conexões de fora do container. Com 127.0.0.1 a porta publicada
# com -p não alcançaria a aplicação.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
