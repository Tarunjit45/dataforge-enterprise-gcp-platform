# Security Policy

## Reporting Vulnerabilities

The maintainers of the Enterprise GCP Data Platform take security issues seriously. If you discover a security vulnerability in this repository, please notify the security team by emailing `security@gcp-data-platform.org` instead of opening a public issue.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## DevSecOps Security Controls

This repository incorporates automated DevSecOps security scanning in CI/CD pipelines:
- **Trivy**: Scans filesystems and libraries for High/Critical CVEs and exposed secret keys.
- **tfsec**: Scans Terraform HCL files for cloud infrastructure misconfigurations.
- **Bandit**: Static security analyzer for Python AST vulnerabilities.
- **Semgrep**: Rule-based SAST scanner for secret patterns and SQL injection risks.
- **Google Workload Identity**: Keyless authentication prohibiting static GCP service account keys.
