FROM python:3.11-slim

WORKDIR /app

# Poetry 2.x: requerido por el pyproject PEP 621 ([project]) y el formato de poetry.lock.
RUN pip install poetry==2.2.1 && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi

COPY . .

RUN if [ -f scripts/entrypoint.sh ]; then \
      sed -i 's/\r$//' scripts/entrypoint.sh && chmod +x scripts/entrypoint.sh; \
    fi

EXPOSE 8000

# src-layout ejecutado con --app-dir src (D-a).
CMD ["uvicorn", "osiris.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src", "--reload"]
