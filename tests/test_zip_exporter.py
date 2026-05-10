"""Tests for ZIPExporter."""
import pytest
import zipfile
import io
from zip_exporter import ZIPExporter
from github_ingestion import RepoFile


def test_zip_exporter_initialization():
    """Test that ZIPExporter initializes correctly."""
    exporter = ZIPExporter()
    assert exporter is not None


def test_export_creates_zip():
    """Test that export creates a valid ZIP file."""
    exporter = ZIPExporter()
    
    # Create test data
    repo_url = "https://github.com/test/repo"
    owner = "test"
    repo = "repo"
    report = "# Test Report\n\nThis is a test report."
    secret_matches = []
    claims = []
    gate_summary = {"total_gates": 5, "passed": 3, "failed": 1, "warned": 1, "gates": []}
    
    class MockScoreResult:
        score = 0.75
        band = type('Band', (), {'value': 'DEMO_READY'})()
        weakest_link = "tests"
        component_scores = {"code_quality": 0.8, "documentation": 0.6}
    
    score_result = MockScoreResult()
    files = [
        RepoFile(path="test.py", content="print('hello')", size=20),
        RepoFile(path="README.md", content="# Test", size=6)
    ]
    
    # Export
    zip_data = exporter.export(
        repo_url, owner, repo, report, secret_matches, claims, gate_summary, score_result, files
    )
    
    # Verify it's a valid ZIP
    assert zip_data is not None
    zip_file = zipfile.ZipFile(io.BytesIO(zip_data))
    assert len(zip_file.namelist()) > 0
    
    # Check for expected files
    file_list = zip_file.namelist()
    assert any("report.md" in f for f in file_list)
