# Developer Onboarding & Local Development Guide

## Environment Prerequisites
* Python 3.11+
* Docker Desktop / Container Runtime
* OpenJDK 11 / 17 (Required for local PySpark unit tests)
* Google Cloud SDK (`gcloud`)

## Local Workspace Initialization

```bash
# 1. Clone repository
git clone https://github.com/enterprise/gcp-data-platform.git
cd gcp-data-platform

# 2. Run developer environment setup script
bash scripts/setup_dev_env.sh

# 3. Verify test suite execution
pytest
```

## Running Static Checks & PySpark Unit Tests

```bash
# Code formatting & static checks
black --check src tests
isort --check src tests
flake8 src tests
mypy src

# Execute full PyTest suite (including PySpark local mode tests)
python -m pytest
```

For detailed ETL architecture and performance optimization specifications, see [`docs/etl-architecture.md`](etl-architecture.md).

## Working with Local Configurations
Configurations are loaded based on the `ENVIRONMENT` environment variable (`dev`, `test`, `prod`).

```bash
export ENVIRONMENT=dev
python -m src.common.config.settings
```
