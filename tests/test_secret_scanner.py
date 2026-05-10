"""Tests for SecretScanner."""
import pytest
from secret_scanner import SecretScanner, SecretMatch


def test_secret_scanner_initialization():
    """Test that SecretScanner initializes correctly."""
    scanner = SecretScanner()
    assert scanner is not None
    assert len(scanner.patterns) > 0


def test_detect_aws_key():
    """Test AWS key detection."""
    scanner = SecretScanner()
    test_content = "aws_access_key_id=AKIAIOSFODNN7EXAMPLE"
    files = [("test.txt", test_content)]
    matches = scanner.scan_repo(files)
    assert len(matches) > 0
    assert any("AWS" in match.secret_type for match in matches)


def test_detect_github_token():
    """Test GitHub token detection."""
    scanner = SecretScanner()
    test_content = "token: ghp_1234567890abcdefghijklmnop"
    files = [("test.txt", test_content)]
    matches = scanner.scan_repo(files)
    assert len(matches) > 0
    assert any("GitHub" in match.secret_type for match in matches)


def test_no_secrets():
    """Test that clean content returns no matches."""
    scanner = SecretScanner()
    test_content = "This is just normal text with no secrets"
    files = [("test.txt", test_content)]
    matches = scanner.scan_repo(files)
    assert len(matches) == 0


def test_summarize():
    """Test summary generation."""
    scanner = SecretScanner()
    test_content = "aws_access_key_id=AKIAIOSFODNN7EXAMPLE\ntoken: ghp_1234567890abcdefghijklmnop"
    files = [("test.txt", test_content)]
    matches = scanner.scan_repo(files)
    summary = scanner.summarize(matches)
    assert "total_matches" in summary
    assert summary["total_matches"] > 0
