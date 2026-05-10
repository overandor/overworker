"""Tests for GitHub URL parsing."""
import pytest
from github_ingestion import GitHubIngestor


def test_parse_github_url():
    """Test GitHub URL parsing."""
    ingestor = GitHubIngestor()
    
    # Test various URL formats
    test_cases = [
        ("https://github.com/owner/repo", ("owner", "repo")),
        ("https://github.com/owner/repo.git", ("owner", "repo")),
        ("https://github.com/owner/repo/", ("owner", "repo")),
        ("github.com/owner/repo", ("owner", "repo")),
    ]
    
    for url, expected in test_cases:
        result = ingestor.parse_repo_url(url)
        assert result == expected


def test_parse_invalid_url():
    """Test that invalid URLs raise ValueError."""
    ingestor = GitHubIngestor()
    
    invalid_urls = [
        "https://notgithub.com/owner/repo",
        "https://github.com/owner",
        "invalid-url",
        "",
    ]
    
    for url in invalid_urls:
        with pytest.raises(ValueError):
            ingestor.parse_repo_url(url)


def test_validate_github_url():
    """Test GitHub URL validation from main.py."""
    from main import RepoRequest
    
    # Valid URLs
    valid_urls = [
        "https://github.com/owner/repo",
        "https://github.com/owner/repo-name",
        "https://github.com/owner/repo.name",
    ]
    
    for url in valid_urls:
        request = RepoRequest(url=url)
        assert request.validate_github_url() is True
    
    # Invalid URLs
    invalid_urls = [
        "https://notgithub.com/owner/repo",
        "https://github.com/owner",
        "invalid-url",
    ]
    
    for url in invalid_urls:
        request = RepoRequest(url=url)
        with pytest.raises(ValueError):
            request.validate_github_url()
