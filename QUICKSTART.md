# Quick Start Guide

Get the Enterprise GCP Data Platform running locally in under 5 minutes.

---

## ⚡ 5-Minute Quick Start

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-org/gcp-data-platform.git
cd gcp-data-platform
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

### 2. Run Test Suite
Verify that all 58 unit tests pass cleanly:
```bash
pytest
```

### 3. Generate Operational Reports & Scorecard
Generate production readiness, health, cost, and SLA reports:
```bash
python -c "from src.operations.reports import OperationalReportConsolidator; OperationalReportConsolidator(output_dir='examples/sample_outputs').generate_all_operational_reports()"
```

Inspect the generated `production_readiness.json` in `examples/sample_outputs/`!
