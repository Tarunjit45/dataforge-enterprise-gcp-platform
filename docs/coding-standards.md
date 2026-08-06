# Enterprise Coding & Style Standards

## Python & PySpark Guidelines
* **Python Version**: Target Python 3.11+.
* **Code Formatting**: Enforced via **Black** (100 character line length limit) and **isort**.
* **Type Annotations**: Mandatory type hints on all public functions, methods, and classes (`mypy --disallow-untyped-defs`).
* **Docstrings**: Google-style docstrings required for all modules, classes, and public functions.
* **Logging**: Use central `src.common.logging.logger` structured logger. Never use `print()` statements.

## Git & Commit Conventions
* Conventional Commits: `<type>(<scope>): <short description>`
* Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`

Example: `feat(ingestion): add schema drift validation helper`
