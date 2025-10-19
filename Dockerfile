FROM python:3.12-slim

WORKDIR /app

# ── Dépendances système (chromadb nécessite build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── UV (remplace poetry/pip, vitesse x10-100 sur install)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_SYSTEM_PYTHON=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ── Dépendances Python — couche séparée du code applicatif pour le cache Docker
COPY pyproject.toml .
RUN uv pip install --no-cache -e "."

# ── Code applicatif
COPY . .

# ── Utilisateur non-root pour la sécurité
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

# ── Variables d'environnement (surcharger via docker run -e ou compose)
ENV PORT=8080 \
    DEFAULT_REGION=Centre \
    DEFAULT_LANGUAGE=fr \
    RAG_PERSIST_DIR=/app/data/chroma

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8080/ready || exit 1

# ── FastAPI via uvicorn (ADK web accessible via adk web dans le dev)
CMD ["uvicorn", "agriculture_cameroun.api.main:app", \
     "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
