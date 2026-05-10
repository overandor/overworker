"""Report generator - creates Markdown reports from analysis results."""
from typing import Dict, Optional, List
from datetime import datetime


class ReportGenerator:
    """Generates Markdown reports from Overworker analysis."""
    
    def redact_secrets(self, text: str, secret_matches: List) -> str:
        """Redact secret values from text for safe export."""
        if not secret_matches:
            return text
        
        redacted = text
        for match in secret_matches:
            if hasattr(match, 'secret_value'):
                # Redact the actual secret value
                secret = match.secret_value
                if secret in redacted:
                    redacted = redacted.replace(secret, "***REDACTED***")
        
        return redacted
    
    def generate_report(self,
                       repo_url: str,
                       owner: str,
                       repo: str,
                       readme: Optional[str],
                       secret_summary: Dict,
                       claim_summary: Dict,
                       gate_summary: Dict,
                       overwork_score_result,
                       files_analyzed: int,
                       secret_matches: Optional[List] = None) -> str:
        """Generate comprehensive Markdown report with secret redaction."""
        
        # Redact secrets from README if present
        if readme and secret_matches:
            readme = self.redact_secrets(readme, secret_matches)
        
        lines = []
        
        # Header
        lines.append("# Overworker Verification Report")
        lines.append("")
        lines.append(f"**Repository:** {owner}/{repo}")
        lines.append(f"**URL:** {repo_url}")
        lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"**Overwork Score:** {overwork_score_result.score:.3f}/1.0")
        lines.append(f"**Readiness Band:** `{overwork_score_result.band.value.upper()}`")
        lines.append(f"**Weakest Link:** `{overwork_score_result.weakest_link}`")
        lines.append(f"**Files Analyzed:** {files_analyzed}")
        lines.append("")
        
        # Score Breakdown
        lines.append("### Component Scores")
        lines.append("")
        for component, score in overwork_score_result.component_scores.items():
            bar = self._score_bar(score)
            lines.append(f"- **{component}:** {score:.2f} {bar}")
        lines.append("")
        
        # Recommendations
        if overwork_score_result.recommendations:
            lines.append("### Recommendations")
            lines.append("")
            for rec in overwork_score_result.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Verification Firewall Results
        lines.append("## Verification Firewall Results")
        lines.append("")
        lines.append(f"**Total Gates:** {gate_summary['total_gates']}")
        lines.append(f"**Passed:** {gate_summary['passed']}")
        lines.append(f"**Failed:** {gate_summary['failed']}")
        lines.append(f"**Warnings:** {gate_summary['warned']}")
        lines.append("")
        
        lines.append("### Gate Details")
        lines.append("")
        for gate in gate_summary["gates"]:
            status_icon = self._status_icon(gate["status"])
            lines.append(f"- {status_icon} **{gate['name']}:** {gate['message']}")
        lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Secret Scan Results
        lines.append("## Secret Scan Results")
        lines.append("")
        lines.append(f"**Total Matches:** {secret_summary['total_matches']}")
        lines.append(f"**Files Affected:** {secret_summary['files_affected']}")
        lines.append("")
        lines.append("> ⚠️ **Note:** Actual secret values have been redacted from this report for security.")
        lines.append("")
        
        lines.append("### By Severity")
        lines.append("")
        for severity, count in secret_summary["by_severity"].items():
            lines.append(f"- **{severity}:** {count}")
        lines.append("")
        
        if secret_summary["by_type"]:
            lines.append("### By Type")
            lines.append("")
            for secret_type, count in secret_summary["by_type"].items():
                lines.append(f"- **{secret_type}:** {count}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Claim Analysis
        lines.append("## Claim Analysis")
        lines.append("")
        lines.append(f"**Total Claims:** {claim_summary.get('total_claims', 0)}")
        lines.append(f"**Verified Ratio:** {claim_summary.get('verified_ratio', 0):.1%}")
        lines.append("")
        
        if claim_summary.get("by_category"):
            lines.append("### Claims by Category")
            lines.append("")
            for category, count in claim_summary["by_category"].items():
                lines.append(f"- **{category}:** {count}")
            lines.append("")
        
        if claim_summary.get("by_evidence"):
            lines.append("### Claims by Evidence Level")
            lines.append("")
            for evidence, count in claim_summary["by_evidence"].items():
                lines.append(f"- **{evidence}:** {count}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # README Assessment
        lines.append("## README Assessment")
        lines.append("")
        if readme:
            word_count = len(readme.split())
            lines.append("**Status:** Present")
            lines.append(f"**Word Count:** {word_count}")
            lines.append(f"**Has Sections:** {'Yes' if any(marker in readme for marker in ['##', '---', '###']) else 'No'}")
        else:
            lines.append("**Status:** Missing or too short")
        lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Footer
        lines.append("## About Overworker")
        lines.append("")
        lines.append("Overworker is an AI execution layer that converts messy repositories into verified, inspectable, saleable assets.")
        lines.append("")
        lines.append("- **Verification Firewall:** Quality gate layer for repo verification")
        lines.append("- **Overwork Score:** Weakest-link commercialization readiness scoring")
        lines.append("- **Secret Scanner:** Detects API keys and sensitive data")
        lines.append("- **Claim Labeler:** Extracts and verifies README claims")
        lines.append("")
        
        return "\n".join(lines)
    
    def _score_bar(self, score: float) -> str:
        """Generate visual score bar."""
        filled = int(score * 20)
        empty = 20 - filled
        return "█" * filled + "░" * empty
    
    def _status_icon(self, status: str) -> str:
        """Get icon for gate status."""
        icons = {
            "pass": "✅",
            "fail": "❌",
            "warn": "⚠️",
            "skip": "⏭️"
        }
        return icons.get(status, "❓")
