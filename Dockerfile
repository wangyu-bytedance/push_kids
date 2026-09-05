FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev
COPY apps/api/src ./apps/api/src
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/data /app/uploads \
    && chown -R appuser:appuser /app/data /app/uploads
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app/apps/api/src"
EXPOSE 8000
USER 10001
CMD ["sh", "-c", "exec uvicorn push_kids.bootstrap.app:create_app --factory --host 0.0.0.0 --port ${PORT:-8000}"]
