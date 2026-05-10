"""Overwork Score - weakest-link readiness scoring for commercialization."""
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class ReadinessBand(Enum):
    """Readiness bands based on Overwork Score."""
    PRODUCTION_READY = "production_ready"  # 0.85 - 1.0
    DEMO_READY = "demo_ready"  # 0.70 - 0.84
    SCAFFOLD = "scaffold"  # 0.50 - 0.69
    PROVENANCE = "provenance"  # 0.30 - 0.49
    FRAGMENT = "fragment"  # 0.0 - 0.29


@dataclass
class OverworkScoreResult:
    score: float
    band: ReadinessBand
    weakest_link: str
    component_scores: Dict[str, float]
    recommendations: List[str]


class OverworkScorer:
    """Computes weakest-link commercialization readiness score."""
    
    def __init__(self):
        self.weights = {
            "documentation": 0.15,
            "code_quality": 0.20,
            "security": 0.20,
            "testing": 0.15,
            "configuration": 0.10,
            "claims_verification": 0.10,
            "file_structure": 0.10
        }
    
    def compute_score(self,
                     files: List[tuple],
                     readme: str,
                     secret_summary: Dict,
                     gate_summary: Dict,
                     claim_summary: Dict) -> OverworkScoreResult:
        """Compute Overwork Score based on all analysis results."""
        
        # Component 1: Documentation
        doc_score = self._score_documentation(files, readme)
        
        # Component 2: Code Quality (from gate results)
        code_score = self._score_code_quality(gate_summary)
        
        # Component 3: Security (from secret scanner)
        security_score = self._score_security(secret_summary)
        
        # Component 4: Testing (from gate results)
        test_score = self._score_testing(gate_summary)
        
        # Component 5: Configuration (from gate results)
        config_score = self._score_configuration(gate_summary)
        
        # Component 6: Claims Verification
        claims_score = self._score_claims(claim_summary)
        
        # Component 7: File Structure
        structure_score = self._score_structure(files)
        
        # Component scores
        component_scores = {
            "documentation": doc_score,
            "code_quality": code_score,
            "security": security_score,
            "testing": test_score,
            "configuration": config_score,
            "claims_verification": claims_score,
            "file_structure": structure_score
        }
        
        # Weighted score (weakest-link principle)
        weighted_scores = [
            component_scores[k] * self.weights[k]
            for k in self.weights
        ]
        
        total_score = sum(weighted_scores)
        
        # Find weakest link
        weakest_link = min(component_scores, key=component_scores.get)
        
        # Determine band
        band = self._get_band(total_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(component_scores)
        
        return OverworkScoreResult(
            score=round(total_score, 3),
            band=band,
            weakest_link=weakest_link,
            component_scores=component_scores,
            recommendations=recommendations
        )
    
    def _score_documentation(self, files: List[tuple], readme: str) -> float:
        """Score documentation quality."""
        score = 0.0
        
        # Has README
        if readme and len(readme.strip()) > 50:
            score += 0.4
        
        # README length
        if readme and len(readme.split()) > 200:
            score += 0.3
        
        # Has sections
        if readme and any(marker in readme for marker in ["##", "---", "###"]):
            score += 0.2
        
        # Additional docs
        doc_files = [f for f, _ in files if f.endswith(('.md', '.rst', '.txt'))]
        if len(doc_files) > 1:
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_code_quality(self, gate_summary: Dict) -> float:
        """Score code quality based on gate results."""
        score = 1.0
        
        # Deduct for failed gates
        for gate in gate_summary.get("gates", []):
            if gate["name"] == "has_code" and gate["status"] == "warn":
                score -= 0.3
            if gate["name"] == "file_count" and gate["status"] == "warn":
                score -= 0.2
        
        return max(score, 0.0)
    
    def _score_security(self, secret_summary: Dict) -> float:
        """Score security based on secret scan results."""
        by_severity = secret_summary.get("by_severity", {})
        
        # Critical secrets are major issues
        if by_severity.get("CRITICAL", 0) > 0:
            return 0.0
        
        # High secrets reduce score
        if by_severity.get("HIGH", 0) > 0:
            return 0.3
        
        # Medium secrets reduce score
        if by_severity.get("MEDIUM", 0) > 0:
            return 0.6
        
        # Low secrets are minor
        if by_severity.get("LOW", 0) > 0:
            return 0.8
        
        # No secrets found
        return 1.0
    
    def _score_testing(self, gate_summary: Dict) -> float:
        """Score testing based on gate results."""
        for gate in gate_summary.get("gates", []):
            if gate["name"] == "has_tests":
                if gate["status"] == "pass":
                    return 1.0
                elif gate["status"] == "warn":
                    return 0.5
        
        return 0.0
    
    def _score_configuration(self, gate_summary: Dict) -> float:
        """Score configuration based on gate results."""
        for gate in gate_summary.get("gates", []):
            if gate["name"] == "has_config":
                if gate["status"] == "pass":
                    return 1.0
                elif gate["status"] == "warn":
                    return 0.5
        
        return 0.0
    
    def _score_claims(self, claim_summary: Dict) -> float:
        """Score claims verification."""
        if not claim_summary:
            return 0.5
        
        verified_ratio = claim_summary.get("verified_ratio", 0.0)
        return verified_ratio
    
    def _score_structure(self, files: List[tuple]) -> float:
        """Score file structure."""
        file_count = len(files)
        
        # Too few files
        if file_count < 3:
            return 0.2
        
        # Minimal structure
        if file_count < 5:
            return 0.5
        
        # Good structure
        if file_count < 10:
            return 0.8
        
        # Complex structure
        return 1.0
    
    def _get_band(self, score: float) -> ReadinessBand:
        """Determine readiness band from score."""
        if score >= 0.85:
            return ReadinessBand.PRODUCTION_READY
        elif score >= 0.70:
            return ReadinessBand.DEMO_READY
        elif score >= 0.50:
            return ReadinessBand.SCAFFOLD
        elif score >= 0.30:
            return ReadinessBand.PROVENANCE
        else:
            return ReadinessBand.FRAGMENT
    
    def _generate_recommendations(self, component_scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on component scores."""
        recommendations = []
        
        if component_scores["documentation"] < 0.7:
            recommendations.append("Expand README with installation instructions, usage examples, and contribution guidelines")
        
        if component_scores["security"] < 0.8:
            recommendations.append("Remove or redact API keys and secrets from code")
        
        if component_scores["testing"] < 0.7:
            recommendations.append("Add test files to verify functionality")
        
        if component_scores["configuration"] < 0.7:
            recommendations.append("Add configuration files (requirements.txt, package.json, etc.)")
        
        if component_scores["claims_verification"] < 0.5:
            recommendations.append("Add code evidence to support README claims")
        
        if component_scores["file_structure"] < 0.7:
            recommendations.append("Add more implementation files to flesh out the project")
        
        return recommendations
