# Utahx SOTA Web Engine — stateless container image
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    UTAHX_STATELESS=1 \
    UTAHX_PORT=8080

WORKDIR /app

COPY requirements.txt pyproject.toml README.md ./
COPY fluid_dynamics.py utahx_core.py utahx_auto.py utahx_secure.py \
     utahx_cli.py utahx_cache.py utahx_prefetch.py utahx_registry.py \
     utahx_ports.py utahx_launcher.py ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

# Stateless zero-config; bind port via UTAHX_PORT (K8s Service maps 80→8080)
CMD ["python", "-m", "utahx_cli", "start", "--port", "8080"]
