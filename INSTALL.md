# Installation & Local Setup Guide

Detailed instructions for installing dependencies and configuring local development environments across Linux, macOS, and Windows.

---

## 📋 System Prerequisites

- **Python**: Version `3.12+`
- **Java JDK**: Version `11` or `17` (Required for local PySpark execution)
- **Terraform**: Version `1.7.0+`
- **Google Cloud SDK (`gcloud`)**: Installed and initialized

---

## ⚙️ Step-by-Step Installation

### 1. Repository Setup
```bash
git clone https://github.com/your-org/gcp-data-platform.git
cd gcp-data-platform
```

### 2. Python Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

### 3. Verify PySpark & Java
```bash
python -c "import pyspark; print(pyspark.__version__)"
```
