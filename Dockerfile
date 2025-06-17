# Multi-stage build for efficient container size
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create non-root user for security
RUN groupadd -r mcp && useradd -r -g mcp -d /app -s /bin/bash mcp

# Set working directory
WORKDIR /app

# Copy application source code
COPY --chown=mcp:mcp src/ ./src/
COPY --chown=mcp:mcp pyproject.toml ./
COPY --chown=mcp:mcp uv.lock ./
COPY --chown=mcp:mcp README.md ./
COPY --chown=mcp:mcp LICENSE ./
RUN uv sync --locked
RUN mkdir /app/.cache
RUN mkdir /app/.cache/uv
RUN chown -R mcp:mcp ./.cache/uv
RUN chown -R mcp:mcp ./.venv
# Switch to non-root user
USER mcp

# Expose the default HTTP port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - can be overridden
CMD ["uv", "run", "mistmcp", "--transport", "http", "--mode", "managed"]
