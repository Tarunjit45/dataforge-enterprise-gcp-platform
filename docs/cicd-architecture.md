# Enterprise GCP Data Platform CI/CD & DevSecOps Architecture

The Enterprise CI/CD & DevSecOps Platform automates infrastructure provisioning, application testing, security vulnerability scanning, software packaging, zero-downtime deployment, post-deployment smoke testing, and automated rollback across `dev`, `staging`, and `prod` environments on Google Cloud Platform.

---

## 🏛 1. CI/CD Architecture & Pipeline Flow

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 GITHUB REPOSITORY & EVENT TRIGGERS                                │
│  Push to [develop, main] / Pull Requests / Tag Releases (v*)                                      │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               STAGE 1 - 3: CHECKOUT & CODE LINTING                                │
│  ├── Stage 1: Checkout repository code                                                            │
│  ├── Stage 2: Install Python dependencies (requirements.txt & requirements-dev.txt)              │
│  └── Stage 3: Python Linting (flake8, black --check, isort --check)                               │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            STAGE 4 - 6: AUTOMATED TESTING SUITES                                  │
│  ├── Stage 4: Unit Testing (pytest tests/unit/)                                                  │
│  ├── Stage 5: Integration Testing (pytest tests/integration/)                                     │
│  ├── Stage 6: PySpark Local Tests (pytest -m spark)                                              │
│  └── Quality Gate 1: Code Coverage >= 85% (--cov-fail-under=85)                                   │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           STAGE 7 - 9: IAC VALIDATION & DEVSECOPS SCANS                           │
│  ├── Stage 7: Terraform Formatting & Module Validation (terraform fmt & validate)                │
│  ├── Stage 8: Terraform Non-Applying Execution Plan (terraform plan)                              │
│  ├── Stage 9A: Bandit SAST Scan (Python static security analysis)                                 │
│  ├── Stage 9B: Semgrep SAST Scan (Hardcoded secrets & SQL injection rules)                        │
│  ├── Stage 9C: Trivy Vulnerability & Secret Scan (OS/Library CVEs & Secrets)                      │
│  ├── Stage 9D: tfsec IaC Security Scan (GCP terraform misconfigurations)                          │
│  └── Quality Gate 2: Zero High/Critical Security Vulnerabilities Allowed                          │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            STAGE 10 - 11: BUILD & ARTIFACT PACKAGING                              │
│  ├── Stage 10: Build Python Distribution Wheels & Tarballs (scripts/build.sh)                     │
│  ├── Stage 11: Package Release Artifacts (scripts/package.sh)                                     │
│  └── Upload immutable release bundle to GitHub Actions Artifacts / GCS Release Buckets             │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      STAGE 12 - 13: ZERO-TRUST CONTINUOUS DEPLOYMENT (CD)                          │
│  ├── Workload Identity Federation: Keyless GCP Auth (google-github-actions/auth)                 │
│  ├── Stage 12: Deploy Infrastructure via Terraform (scripts/deploy.sh)                            │
│  └── Stage 13: Deploy PySpark Jobs & BigQuery DDLs to Target GCP Environment                      │
└──────────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           STAGE 14 - 15: SMOKE TESTING & AUTOMATED ROLLBACK                       │
│  ├── Stage 14: Post-Deployment Infrastructure Smoke Tests (scripts/smoke_tests.sh)               │
│  └── Stage 15: Automated Rollback on Failure (scripts/rollback.sh)                                │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔒 2. Zero-Trust Authentication Architecture

The CI/CD platform strictly prohibits long-lived service account keys (`.json` keyfiles). All GCP authentication utilizes **Google Cloud Workload Identity Federation**:

```
GitHub Actions Runner  ──► OIDC Token Exchange ──► GCP Workload Identity Pool
                                                            │
                                                            ▼
                                                Impersonates GCP Service Account
                                                (Short-lived OAuth 2.0 Access Token)
```

- **GitHub Action**: `google-github-actions/auth@v2`
- **Identity Pool**: `projects/<PROJECT_NUM>/locations/global/workloadIdentityPools/github-actions-pool`
- **Attribute Mapping**: `google.subject=assertion.sub, attribute.repository=assertion.repository`

---

## 🛑 3. DevSecOps Quality Gates

Deployment pipelines automatically abort and fail if any of the following quality gates are breached:

1. **Unit & Integration Tests**: 100% test suite pass rate required.
2. **Code Coverage**: Overall test coverage must meet or exceed **85%** (`pytest --cov=src --cov-fail-under=85`).
3. **High/Critical Vulnerabilities**: Zero High or Critical CVEs allowed in dependency libraries or container/filesystem scans (`Trivy`, `Bandit`, `Semgrep`, `tfsec`).
4. **Terraform Validation**: `terraform fmt` and `terraform validate` must complete cleanly with zero errors.
5. **Post-Deployment Smoke Tests**: Automated infrastructure and application smoke tests (`scripts/smoke_tests.sh`) must pass 100%.

---

## 📁 4. Package & Configuration Structure

```
.github/workflows/
├── ci.yml            # Continuous Integration pipeline (Linting, Tests, Coverage, Scans, Build)
├── cd.yml            # Continuous Deployment pipeline with Workload Identity & Automated Rollback
├── terraform.yml     # Infrastructure validation and plan generation workflow
├── quality-gates.yml # Compliance audit enforcing 85% coverage & zero security vulnerabilities
└── release.yml       # Release tag packaging and GitHub Release artifact generation

scripts/
├── build.sh          # Compiles Python bytecode and builds wheel/tarball distributions
├── package.sh        # Packages PySpark jobs, SQL scripts, and migration engines into release archives
├── deploy.sh         # Executes Terraform IaC apply and syncs application binaries to GCP
├── smoke_tests.sh    # Executes post-deployment infrastructure verification and smoke suites
└── rollback.sh       # Automatically triggers Terraform state rollback and staging reversion on failure

devsecops/
├── trivy/trivy.yaml  # Trivy scanner configuration (HIGH/CRITICAL severity enforcement)
├── tfsec/tfsec.yaml  # tfsec IaC security scanner rule configuration
├── bandit/bandit.yaml# Bandit SAST security analyzer configuration
└── semgrep/semgrep.yaml # Semgrep rules for hardcoded secrets and SQL injection prevention
```

---

## 🔄 5. Automated Rollback & Recovery Strategy

If `scripts/deploy.sh` or `scripts/smoke_tests.sh` fails during a deployment run:
1. GitHub Actions step `Stage 15: Automatic Rollback on Failure` triggers automatically via `if: failure()`.
2. `scripts/rollback.sh` refreshes and reverts Terraform state to the previous stable revision.
3. Application binaries staged in GCS deployment buckets are reverted to the last known good release tag.
4. Alerts are generated and deployment status is flagged as failed.
