"""Verification Firewall - quality gate layer for repo analysis."""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class GateStatus(Enum):
    """Status of a verification gate."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class VerificationGate:
    name: str
    description: str
    status: GateStatus
    message: str
    score_impact: float  # How much this gate affects the Overwork Score


class VerificationFirewall:
    """Deterministic quality gate layer for repo verification."""
    
    def __init__(self):
        self.gates: List[VerificationGate] = []
    
    def run_all_gates(self, 
                     files: List[Tuple[str, str]], 
                     readme: Optional[str],
                     secret_matches: List,
                     claims: List) -> List[VerificationGate]:
        """Run all verification gates."""
        self.gates = []
        
        # Gate 1: Has README
        self._check_has_readme(readme)
        
        # Gate 2: README has substance
        if readme:
            self._check_readme_substance(readme)
        
        # Gate 3: Has code files
        self._check_has_code(files)
        
        # Gate 4: No critical secrets
        self._check_critical_secrets(secret_matches)
        
        # Gate 5: Has license
        self._check_has_license(files)
        
        # Gate 6: Has tests
        self._check_has_tests(files)
        
        # Gate 7: Has documentation
        self._check_has_documentation(files)
        
        # Gate 8: Claim verification ratio
        if claims:
            self._check_claim_verification(claims)
        
        # Gate 9: File count threshold
        self._check_file_count(files)
        
        # Gate 10: Has configuration files
        self._check_has_config(files)
        
        return self.gates
    
    def _check_has_readme(self, readme: Optional[str]) -> None:
        """Check if repository has a README."""
        if readme and len(readme.strip()) > 50:
            self.gates.append(VerificationGate(
                name="has_readme",
                description="Repository has a README file",
                status=GateStatus.PASS,
                message="README present with content",
                score_impact=0.0
            ))
        else:
            self.gates.append(VerificationGate(
                name="has_readme",
                description="Repository has a README file",
                status=GateStatus.FAIL,
                message="README missing or too short",
                score_impact=-0.15
            ))
    
    def _check_readme_substance(self, readme: str) -> None:
        """Check if README has substantial content."""
        word_count = len(readme.split())
        has_sections = any(marker in readme for marker in ["##", "---", "###"])
        
        if word_count > 100 and has_sections:
            self.gates.append(VerificationGate(
                name="readme_substance",
                description="README has substantial content",
                status=GateStatus.PASS,
                message=f"README has {word_count} words with sections",
                score_impact=0.0
            ))
        else:
            self.gates.append(VerificationGate(
                name="readme_substance",
                description="README has substantial content",
                status=GateStatus.WARN,
                message=f"README has {word_count} words, could be more detailed",
                score_impact=-0.05
            ))
    
    def _check_has_code(self, files: List[Tuple[str, str]]) -> None:
        """Check if repository has code files."""
        code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.rs', '.go', '.java', '.c', '.cpp'}
        has_code = any(any(f.endswith(ext) for ext in code_extensions) for f, _ in files)
        
        if has_code:
            self.gates.append(VerificationGate(
                name="has_code",
                description="Repository has code files",
                status=GateStatus.PASS,
                message="Found code files in repository",
                score_impact=0.0
            ))
        else:
            self.gates.append(VerificationGate(
                name="has_code",
                description="Repository has code files",
                status=GateStatus.WARN,
                message="No code files found",
                score_impact=-0.1
            ))
    
    def _check_critical_secrets(self, secret_matches: List) -> None:
        """Check for critical secrets."""
        critical_count = sum(1 for m in secret_matches if hasattr(m, 'secret_type') and 
                           ('AWS' in m.secret_type or 'Key' in m.secret_type or 'Token' in m.secret_type))
        
        if critical_count == 0:
            self.gates.append(VerificationGate(
                name="no_critical_secrets",
                description="No critical secrets detected",
                status=GateStatus.PASS,
                message="No critical secrets found",
                score_impact=0.0
            ))
        else:
            self.gates.append(VerificationGate(
                name="no_critical_secrets",
                description="No critical secrets detected",
                status=GateStatus.FAIL,
                message=f"Found {critical_count} potential critical secrets",
                score_impact=-0.25
            ))
    
    def _check_has_license(self, files: List[Tuple[str, str]]) -> None:
        """Check if repository has a license file."""
        license_names = ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'COPYING']
        has_license = any(license_name in path.upper() for path, _ in files for license_name in license_names)
        
        if has_license:
            self.gates.append(VerificationGate(
                name="has_license",
                description="Repository has a license file",
                status=GateStatus.PASS,
                message="License file present",
                score_impact=0.0
            ))
        else:
            self.gates.append(VerificationGate(
                name="has_license",
                description="Repository has a license file",
                status=GateStatus.WARN,
                message="No license file found",
                score_impact=-0.05
            ))
    
    def _check_has_tests(self, files: List[Tuple[str, str]]) -> None:
        """Check if repository has test files."""
        test_indicators = ['test', 'spec', '__tests__']
        has_tests = any(indicator in path.lower() for path, _ in files for indicator in test_indicators)
        
        if has_tests:
            self.gates.append(VerificationGate(
                name="has_tests",
                description="Repository has test files",
                status=GateStatus.PASS,
                message="Test files present",
                score_impact=0.0
            ))
        else:
            self.gates.append(VerificationGate(
                name="has_tests",
                description="Repository has test files",
                status=GateStatus.WARN,
                message="No test files found",
                score_impact=-0.1
            ))
    
    def _check_has_documentation(self, files: List[Tuple[str, str]]) -> None:
        """Check if repository has documentation beyond README."""
        doc_extensions = {'.md', '.rst', '.txt'}
        doc_files = [f for f, _ in files if any(f.endswith(ext) for ext in doc_extensions)]
        
        if len(doc_files) > 1:  # More than just README
            self.gates.append(VerificationGate(
                name="has_documentation",
                description="Repository has documentation",
                status=GateStatus.PASS,
                message=f"Found {len(doc_files)} documentation files",
                score_impact=0.0
            ))
        else:
            self.gates.append(VerificationGate(
                name="has_documentation",
                description="Repository has documentation",
                status=GateStatus.WARN,
                message="Limited documentation beyond README",
                score_impact=-0.05
            ))
    
    def _check_claim_verification(self, claims: List) -> None:
        """Check claim verification ratio."""
        if not claims:
            self.gates.append(VerificationGate(
                name="claim_verification",
                description="Claims have supporting evidence",
                status=GateStatus.SKIP,
                message="No claims to verify",
                score_impact=0.0
            ))
            return
        
        verified_count = sum(1 for c in claims if hasattr(c, 'evidence_level') and 
                           c.evidence_level.value in ['verified', 'partial'])
        ratio = verified_count / len(claims)
        
        if ratio >= 0.5:
            self.gates.append(VerificationGate(
                name="claim_verification",
                description="Claims have supporting evidence",
                status=GateStatus.PASS,
                message=f"{verified_count}/{len(claims)} claims have evidence ({ratio:.0%})",
                score_impact=0.0
            ))
        else:
            self.gates.append(VerificationGate(
                name="claim_verification",
                description="Claims have supporting evidence",
                status=GateStatus.WARN,
                message=f"{verified_count}/{len(claims)} claims have evidence ({ratio:.0%})",
                score_impact=-0.1
            ))
    
    def _check_file_count(self, files: List[Tuple[str, str]]) -> None:
        """Check if repository has sufficient files."""
        file_count = len(files)
        
        if file_count >= 5:
            self.gates.append(VerificationGate(
                name="file_count",
                description="Repository has sufficient files",
                status=GateStatus.PASS,
                message=f"Repository has {file_count} file(s)",
                score_impact=0.0
            ))
        else:
            self.gates.append(VerificationGate(
                name="file_count",
                description="Repository has sufficient files",
                status=GateStatus.WARN,
                message=f"Repository has only {file_count} files",
                score_impact=-0.1
            ))
    
    def _check_has_config(self, files: List[Tuple[str, str]]) -> None:
        """Check if repository has configuration files."""
        config_files = ['package.json', 'requirements.txt', 'setup.py', 'pyproject.toml', 
                       'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle']
        has_config = any(config in path for path, _ in files for config in config_files)
        
        if has_config:
            self.gates.append(VerificationGate(
                name="has_config",
                description="Repository has configuration files",
                status=GateStatus.PASS,
                message="Configuration files present",
                score_impact=0.0
            ))
        else:
            self.gates.append(VerificationGate(
                name="has_config",
                description="Repository has configuration files",
                status=GateStatus.WARN,
                message="No configuration files found",
                score_impact=-0.05
            ))
    
    def get_summary(self) -> Dict:
        """Get summary of gate results."""
        passed = sum(1 for g in self.gates if g.status == GateStatus.PASS)
        failed = sum(1 for g in self.gates if g.status == GateStatus.FAIL)
        warned = sum(1 for g in self.gates if g.status == GateStatus.WARN)
        skipped = sum(1 for g in self.gates if g.status == GateStatus.SKIP)
        
        total_score_impact = sum(g.score_impact for g in self.gates)
        
        return {
            "total_gates": len(self.gates),
            "passed": passed,
            "failed": failed,
            "warned": warned,
            "skipped": skipped,
            "score_impact": total_score_impact,
            "gates": [
                {
                    "name": g.name,
                    "status": g.status.value,
                    "message": g.message,
                    "score_impact": g.score_impact
                }
                for g in self.gates
            ]
        }
