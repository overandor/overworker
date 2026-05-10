"""Repository to single file converter - combines repo files into one file."""
import os
from typing import List, Tuple
from datetime import datetime


class RepoToSingleFileConverter:
    """Converts repository structure into a single file containing multiple files."""
    
    def __init__(self):
        self.separator = "=" * 80
    
    def convert_repo_to_single_file(self, 
                                    repo_files: List[Tuple[str, str]],
                                    output_filename: str = "combined_chat_repo.txt") -> str:
        """Convert repository files into a single combined file."""
        lines = []
        
        # Header
        lines.append("# Combined Repository File")
        lines.append(f"# Generated: {datetime.utcnow().isoformat()}")
        lines.append(f"# Total Files: {len(repo_files)}")
        lines.append("")
        lines.append(self.separator)
        lines.append("")
        
        # Table of contents
        lines.append("## Table of Contents")
        lines.append("")
        for filepath, _ in repo_files:
            lines.append(f"- {filepath}")
        lines.append("")
        lines.append(self.separator)
        lines.append("")
        
        # File contents
        for filepath, content in repo_files:
            lines.append(f"FILE: {filepath}")
            lines.append(self.separator)
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append(self.separator)
            lines.append("")
        
        return "\n".join(lines)
    
    def write_combined_file(self, content: str, output_path: str) -> None:
        """Write the combined file to disk."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def convert_and_write(self,
                         repo_files: List[Tuple[str, str]],
                         output_path: str) -> None:
        """Convert repo to single file and write to disk."""
        content = self.convert_repo_to_single_file(repo_files)
        self.write_combined_file(content, output_path)
