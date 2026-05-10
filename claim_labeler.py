"""Claim labeling - extracts and labels claims from README files."""
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class ClaimCategory(Enum):
    """Categories of claims."""
    FEATURE = "feature"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    INTEGRATION = "integration"
    ADOPTION = "adoption"
    REVENUE = "revenue"
    TECHNICAL = "technical"
    MARKETING = "marketing"
    UNCATEGORIZED = "uncategorized"


class ClaimEvidence(Enum):
    """Evidence levels for claims."""
    VERIFIED = "verified"  # Has code/tests to back it up
    PARTIAL = "partial"  # Some evidence exists
    CLAIMED_ONLY = "claimed_only"  # No evidence found
    UNVERIFIABLE = "unverifiable"  # Cannot be verified from code


@dataclass
class Claim:
    text: str
    category: ClaimCategory
    evidence_level: ClaimEvidence
    line_number: int
    context: str


class ClaimLabeler:
    """Extracts and labels claims from README and documentation."""
    
    # Patterns for different claim types
    PATTERNS = {
        ClaimCategory.FEATURE: [
            r'(?i)(supports|includes|provides|offers|features|has)\s+\w+',
            r'(?i)(can|able to)\s+\w+',
        ],
        ClaimCategory.PERFORMANCE: [
            r'(?i)(fast|quick|speed|latency|performance|optimi(z|s)ed|efficient)',
            r'(?i)(\d+ms|\d+ seconds|\d+% (faster|slower|improvement))',
        ],
        ClaimCategory.SECURITY: [
            r'(?i)(secure|security|encrypted|auth|authentication|authorization)',
            r'(?i)(no keys|keyless|api key|secret)',
        ],
        ClaimCategory.COMPLIANCE: [
            r'(?i)(compliant|compliance|gdpr|soc2|hipaa|regulation)',
        ],
        ClaimCategory.INTEGRATION: [
            r'(?i)(integrates with|works with|compatible with|supports)\s+\w+',
            r'(?i)(api|sdk|library|plugin)',
        ],
        ClaimCategory.ADOPTION: [
            r'(?i)(used by|adopted by|deployed by|customers|users|downloads)',
            r'(?i)(\d+k?\+?\s*(users|downloads|stars))',
        ],
        ClaimCategory.REVENUE: [
            r'(?i)(revenue|pricing|paid|subscription|enterprise|commercial)',
            r'(?i)(\$|€|£)\d+',
        ],
        ClaimCategory.TECHNICAL: [
            r'(?i)(built with|powered by|uses|framework|stack|architecture)',
        ],
        ClaimCategory.MARKETING: [
            r'(?i)(best|leading|revolutionary|game-changing|innovative)',
            r'(?i)(first|only|unique|proprietary)',
        ],
    }
    
    def __init__(self):
        self.compiled_patterns = {
            category: [re.compile(p) for p in patterns]
            for category, patterns in self.PATTERNS.items()
        }
    
    def extract_claims(self, readme: str) -> List[Claim]:
        """Extract claims from README content."""
        if not readme:
            return []
        
        claims = []
        lines = readme.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and headers
            if not line.strip() or line.startswith('#'):
                continue
            
            # Check each pattern
            for category, patterns in self.compiled_patterns.items():
                for pattern in patterns:
                    if pattern.search(line):
                        # Get context
                        context_start = max(0, line_num - 1)
                        context_end = min(len(lines), line_num + 2)
                        context = '\n'.join(lines[context_start:context_end])
                        
                        claims.append(Claim(
                            text=line.strip(),
                            category=category,
                            evidence_level=ClaimEvidence.CLAIMED_ONLY,  # Default, updated later
                            line_number=line_num,
                            context=context
                        ))
                        break  # One category per line
        
        return claims
    
    def verify_claim_against_files(self, claim: Claim, files: List[Tuple[str, str]]) -> ClaimEvidence:
        """Check if claim has supporting evidence in code."""
        claim_lower = claim.text.lower()
        
        # Look for keywords in code files
        for file_path, content in files:
            # Skip the README itself
            if 'README' in file_path.upper():
                continue
            
            # Simple keyword matching
            if any(word in content.lower() for word in claim_lower.split() if len(word) > 4):
                # Found some evidence
                return ClaimEvidence.PARTIAL
        
        return ClaimEvidence.CLAIMED_ONLY
    
    def label_all_claims(self, readme: str, files: List[Tuple[str, str]]) -> List[Claim]:
        """Extract claims and verify them against code."""
        claims = self.extract_claims(readme)
        
        # Verify each claim
        for claim in claims:
            claim.evidence_level = self.verify_claim_against_files(claim, files)
        
        return claims
    
    def summarize(self, claims: List[Claim]) -> Dict:
        """Generate summary of claims."""
        by_category = {}
        by_evidence = {}
        
        for claim in claims:
            # Count by category
            cat = claim.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            
            # Count by evidence level
            ev = claim.evidence_level.value
            by_evidence[ev] = by_evidence.get(ev, 0) + 1
        
        return {
            "total_claims": len(claims),
            "by_category": by_category,
            "by_evidence": by_evidence,
            "verified_ratio": by_evidence.get("verified", 0) / len(claims) if claims else 0
        }
