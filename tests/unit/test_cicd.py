"""Unit tests for Phase 10 CI/CD & DevSecOps Platform Workflows and Scripts."""

from pathlib import Path

import pytest
import yaml


@pytest.mark.unit
def test_devsecops_config_files_exist_and_valid():
    """Verify DevSecOps tool configuration files exist and parse as valid YAML."""
    root_dir = Path(__file__).resolve().parents[2]
    configs = [
        root_dir / "devsecops" / "trivy" / "trivy.yaml",
        root_dir / "devsecops" / "tfsec" / "tfsec.yaml",
        root_dir / "devsecops" / "bandit" / "bandit.yaml",
        root_dir / "devsecops" / "semgrep" / "semgrep.yaml",
    ]

    for cfg in configs:
        assert cfg.exists(), f"DevSecOps config file missing: {cfg}"
        content = cfg.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        assert isinstance(parsed, dict)


@pytest.mark.unit
def test_github_action_workflows_exist_and_valid():
    """Verify GitHub Actions workflow files exist and parse as valid YAML."""
    root_dir = Path(__file__).resolve().parents[2]
    workflows = [
        root_dir / ".github" / "workflows" / "ci.yml",
        root_dir / ".github" / "workflows" / "cd.yml",
        root_dir / ".github" / "workflows" / "terraform.yml",
        root_dir / ".github" / "workflows" / "release.yml",
    ]

    for wf in workflows:
        assert wf.exists(), f"GitHub workflow file missing: {wf}"
        content = wf.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        assert "name" in parsed
        assert "jobs" in parsed or "on" in parsed


@pytest.mark.unit
def test_automation_scripts_exist_and_executable():
    """Verify bash deployment and build scripts exist and contain valid shebangs."""
    root_dir = Path(__file__).resolve().parents[2]
    scripts = [
        root_dir / "scripts" / "build.sh",
        root_dir / "scripts" / "deploy.sh",
        root_dir / "scripts" / "smoke_tests.sh",
        root_dir / "scripts" / "rollback.sh",
        root_dir / "scripts" / "package.sh",
    ]

    for s in scripts:
        assert s.exists(), f"Automation script missing: {s}"
        content = s.read_text(encoding="utf-8")
        assert content.startswith("#!/usr/bin/env bash")
