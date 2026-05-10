"""Tokenization engine - converts repo content into tokens."""
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import Counter


@dataclass
class Token:
    value: str
    type: str  # 'code', 'text', 'metric', 'endpoint', 'config'
    frequency: int
    context: str


@dataclass
class TokenizedRepo:
    tokens: List[Token]
    total_tokens: int
    unique_tokens: int
    token_distribution: Dict[str, int]
    metadata: Dict


class RepoTokenizer:
    """Tokenizes repository content for analysis and derivative creation."""
    
    def __init__(self):
        self.code_patterns = {
            'function': r'def\s+(\w+)|function\s+(\w+)|const\s+(\w+)\s*=',
            'class': r'class\s+(\w+)',
            'endpoint': r'@(app\.)?(route|get|post|put|delete)\([\'"]([^\'"]+)[\'"]\)',
            'config': r'(\w+)\s*=\s*[\'"]?([^\'"\n]+)[\'"]?',
            'import': r'import\s+(\w+)|from\s+(\w+)',
        }
    
    def tokenize_repo(self, files: List[Tuple[str, str]]) -> TokenizedRepo:
        """Tokenize all files in a repository."""
        all_tokens = []
        
        for file_path, content in files:
            tokens = self._tokenize_file(file_path, content)
            all_tokens.extend(tokens)
        
        # Count frequencies
        token_values = [t.value for t in all_tokens]
        counter = Counter(token_values)
        
        # Update token frequencies
        for token in all_tokens:
            token.frequency = counter[token.value]
        
        # Calculate distribution
        token_distribution = {}
        for token in all_tokens:
            token_distribution[token.type] = token_distribution.get(token.type, 0) + 1
        
        return TokenizedRepo(
            tokens=all_tokens,
            total_tokens=len(all_tokens),
            unique_tokens=len(counter),
            token_distribution=token_distribution,
            metadata={
                "files_processed": len(files),
                "avg_tokens_per_file": len(all_tokens) / len(files) if files else 0
            }
        )
    
    def _tokenize_file(self, file_path: str, content: str) -> List[Token]:
        """Tokenize a single file."""
        tokens = []
        
        # Determine file type
        file_type = self._get_file_type(file_path)
        
        if file_type == 'code':
            tokens.extend(self._tokenize_code(file_path, content))
        elif file_type == 'config':
            tokens.extend(self._tokenize_config(file_path, content))
        else:
            tokens.extend(self._tokenize_text(file_path, content))
        
        return tokens
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type."""
        code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.rs', '.go', '.java', '.rb', '.php'}
        config_extensions = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.env'}
        
        for ext in code_extensions:
            if file_path.endswith(ext):
                return 'code'
        
        for ext in config_extensions:
            if file_path.endswith(ext):
                return 'config'
        
        return 'text'
    
    def _tokenize_code(self, file_path: str, content: str) -> List[Token]:
        """Tokenize code file."""
        tokens = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Extract functions
            func_match = re.search(r'def\s+(\w+)|function\s+(\w+)|const\s+(\w+)\s*=', line)
            if func_match:
                func_name = next(g for g in func_match.groups() if g)
                tokens.append(Token(
                    value=func_name,
                    type='code',
                    frequency=0,
                    context=f"{file_path}:{line_num}"
                ))
            
            # Extract endpoints
            endpoint_match = re.search(r'@(route|get|post|put|delete)\([\'"]([^\'"]+)[\'"]\)', line)
            if endpoint_match:
                endpoint_path = endpoint_match.group(2)
                tokens.append(Token(
                    value=endpoint_path,
                    type='endpoint',
                    frequency=0,
                    context=f"{file_path}:{line_num}"
                ))
        
        return tokens
    
    def _tokenize_config(self, file_path: str, content: str) -> List[Token]:
        """Tokenize config file."""
        tokens = []
        
        # Extract key-value pairs
        for match in re.finditer(r'(\w+)\s*[:=]\s*[\'"]?([^\'"\n]+)[\'"]?', content):
            key = match.group(1)
            tokens.append(Token(
                value=key,
                type='config',
                frequency=0,
                context=file_path
            ))
        
        return tokens
    
    def _tokenize_text(self, file_path: str, content: str) -> List[Token]:
        """Tokenize text file."""
        tokens = []
        
        # Extract words (simple tokenization)
        words = re.findall(r'\b\w+\b', content.lower())
        
        for word in words:
            if len(word) > 3:  # Skip short words
                tokens.append(Token(
                    value=word,
                    type='text',
                    frequency=0,
                    context=file_path
                ))
        
        return tokens
    
    def get_top_tokens(self, tokenized_repo: TokenizedRepo, n: int = 20) -> List[Token]:
        """Get top N tokens by frequency."""
        return sorted(tokenized_repo.tokens, key=lambda t: t.frequency, reverse=True)[:n]
    
    def get_endpoint_tokens(self, tokenized_repo: TokenizedRepo) -> List[Token]:
        """Get all endpoint tokens."""
        return [t for t in tokenized_repo.tokens if t.type == 'endpoint']
