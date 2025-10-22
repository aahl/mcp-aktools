FROM ghcr.io/astral-sh/uv:python3.13-alpine

LABEL io.modelcontextprotocol.server.name="io.github.aahl/mcp-aktools"

ENV PYTHONUNBUFFERED=1 \
    PORT=80

WORKDIR /app
COPY . .

RUN uv sync

CMD uv run -m mcp_aktools --http --host 0.0.0.0 --port $PORT
HEALTHCHECK --interval=1m --start-period=30s CMD nc -zn 0.0.0.0 $PORT || exit 1
