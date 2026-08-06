# Developer Contributing Guidelines

Thank you for contributing to the Enterprise GCP Data Platform!

## Contribution Workflow

1. Create a feature branch from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/JIRA-1234-description
   ```
2. Make your modular changes.
3. Ensure local tests pass (`pytest`).
4. Run pre-commit hooks (`pre-commit run --all-files`).
5. Push to remote and open a Pull Request against `develop`.
6. Acquire approval from code owners designated in `.github/CODEOWNERS`.
