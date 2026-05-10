"""Remote snap2txt - fetches remote snapshots and converts to text."""
import subprocess
import tempfile
import shutil
import os
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Snapshot:
    url: str
    timestamp: str
    content: str
    metadata: Dict


class Snap2TxtFetcher:
    """Fetches snapshots from various sources and converts to text."""
    
    def __init__(self):
        self.temp_dir = None
    
    def fetch_web_snapshot(self, url: str) -> Snapshot:
        """Fetch snapshot from web URL using text-based browser."""
        # Use text-based browser or curl to fetch content
        try:
            result = subprocess.run(
                ["curl", "-s", "-L", url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return Snapshot(
                    url=url,
                    timestamp=self._get_timestamp(),
                    content=result.stdout,
                    metadata={"source": "web", "status": "success"}
                )
        except subprocess.TimeoutExpired:
            return Snapshot(
                url=url,
                timestamp=self._get_timestamp(),
                content="",
                metadata={"source": "web", "status": "timeout"}
            )
        
        return Snapshot(
            url=url,
            timestamp=self._get_timestamp(),
            content="",
            metadata={"source": "web", "status": "failed"}
        )
    
    def fetch_repo_snapshot(self, repo_url: str) -> Snapshot:
        """Fetch snapshot from git repository."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Clone repo
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, temp_dir],
                check=True,
                capture_output=True,
                timeout=60
            )
            
            # Convert repo to text representation
            content = self._repo_to_text(temp_dir)
            
            return Snapshot(
                url=repo_url,
                timestamp=self._get_timestamp(),
                content=content,
                metadata={"source": "git", "status": "success"}
            )
        except Exception as e:
            return Snapshot(
                url=repo_url,
                timestamp=self._get_timestamp(),
                content="",
                metadata={"source": "git", "status": "failed", "error": str(e)}
            )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _repo_to_text(self, repo_path: str) -> str:
        """Convert repository to text representation."""
        lines = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            dirs[:] = [d for d in dirs if d != '.git']
            
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, repo_path)
                
                # Skip binary files
                if self._is_text_file(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines.append(f"FILE: {rel_path}")
                            lines.append("=" * len(f"FILE: {rel_path}"))
                            lines.append(content)
                            lines.append("")
                    except (OSError, UnicodeDecodeError):
                        pass
        
        return "\n".join(lines)
    
    def _is_text_file(self, path: str) -> bool:
        """Check if file is text-based."""
        text_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.md', '.txt', '.json', 
            '.yaml', '.yml', '.toml', '.cfg', '.ini', '.sh', '.bash', 
            '.zsh', '.rs', '.go', '.java', '.c', '.cpp', '.h', '.hpp', 
            '.css', '.html', '.xml', '.sql', '.rb', '.php'
        }
        
        return any(path.endswith(ext) for ext in text_extensions)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def batch_fetch(self, urls: List[str]) -> List[Snapshot]:
        """Fetch multiple snapshots."""
        snapshots = []
        
        for url in urls:
            if url.startswith("http"):
                snapshot = self.fetch_web_snapshot(url)
            elif url.startswith("git"):
                snapshot = self.fetch_repo_snapshot(url)
            else:
                # Assume GitHub URL
                snapshot = self.fetch_repo_snapshot(f"https://github.com/{url}.git")
            
            snapshots.append(snapshot)
        
        return snapshots
