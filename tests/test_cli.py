import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_cli_runs():
    result = subprocess.run(
        [sys.executable, "-m", "zip_generator.cli", "--difficulty", "easy", "--seed", "1234"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode in (0, 1)
    data = json.loads(result.stdout)
    assert "error" in data


def test_cli_rejects_invalid_json():
    result = subprocess.run(
        [sys.executable, "-m", "zip_generator.cli", "--stdin-json"],
        cwd=REPO_ROOT,
        input='{"difficulty": ',
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    data = json.loads(result.stdout)
    assert data["error"] is True
    assert "Invalid JSON input" in data["message"]
