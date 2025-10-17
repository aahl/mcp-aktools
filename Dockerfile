FROM ghcr.io/astral-sh/uv:python3.13-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

RUN uv sync

CMD ["uv", "run", "-m", "mcp_aktools", "--http", "--host", "0.0.0.0", "--port", "80"]
HEALTHCHECK --interval=1m --start-period=30s CMD nc -zn 0.0.0.0 80 || exit 1
