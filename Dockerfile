FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

LABEL io.modelcontextprotocol.server.name="io.github.aahl/mcp-aktools"

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    TRANSPORT=http \
    PORT=80

WORKDIR /app
COPY . .

RUN apt update && apt install -y --no-install-recommends netcat-openbsd
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

CMD ["uv", "run", "-m", "mcp_aktools"]
HEALTHCHECK --interval=1m --start-period=30s CMD nc -zn 0.0.0.0 $PORT || exit 1
