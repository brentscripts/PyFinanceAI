# Pinned to match local dev (see README) so behavior is consistent across environments.
FROM python:3.12-alpine

WORKDIR /app

# curl is needed for the healthcheck in docker-compose.yml; alpine doesn't ship it.
RUN apk add --no-cache curl

# Copy only what's needed to resolve dependencies first, so this layer is
# cached and doesn't rebuild just because application code changed.
COPY pyproject.toml ./

# Copy source before installing, since pyproject.toml declares real packages
# (database, importers, webapp) that setuptools needs present at install time.
COPY webapp/ webapp/
COPY database/ database/
COPY importers/ importers/
COPY main.py init_db.py schema.sql __init__.py ./

# Toggle to "true" to also install dev/test dependencies (pytest, etc.)
ARG DEV_INSTALL=false
RUN if [ "$DEV_INSTALL" = "true" ]; then \
      pip install --no-cache-dir -e ".[dev]"; \
    else \
      pip install --no-cache-dir -e .; \
    fi

ENV FLASK_APP=webapp/app.py
ENV FLASK_ENV=production

EXPOSE 5000

# Use Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "webapp.app:app"]
