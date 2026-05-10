"""ZIP exporter - packages analysis results into downloadable ZIP."""
import zipfile
import io
from typing import Dict, List
from datetime import datetime


class ZIPExporter:
    """Exports analysis results to ZIP package."""
    
    def export(self,
               repo_url: str,
               owner: str,
               repo: str,
               report_markdown: str,
               secret_matches: List,
               claims: List,
               gate_summary: Dict,
               overwork_score_result,
               files: List[tuple]) -> bytes:
        """Create ZIP package with all analysis artifacts."""
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Main report
            zipf.writestr(f"{repo}_overworker_report.md", report_markdown)
            
            # 2. JSON summary
            json_summary = self._create_json_summary(
                repo_url, owner, repo, gate_summary, overwork_score_result
            )
            zipf.writestr(f"{repo}_summary.json", json_summary)
            
            # 3. Secret scan results
            if secret_matches:
                secret_report = self._create_secret_report(secret_matches)
                zipf.writestr(f"{repo}_secrets.txt", secret_report)
            
            # 4. Claims analysis
            if claims:
                claims_report = self._create_claims_report(claims)
                zipf.writestr(f"{repo}_claims.txt", claims_report)
            
            # 5. Gate results
            gate_report = self._create_gate_report(gate_summary)
            zipf.writestr(f"{repo}_gates.txt", gate_report)
            
            # 6. File inventory
            file_inventory = self._create_file_inventory(files)
            zipf.writestr(f"{repo}_files.txt", file_inventory)
            
            # 7. Metadata
            metadata = self._create_metadata(repo_url, owner, repo)
            zipf.writestr("metadata.txt", metadata)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def _create_json_summary(self,
                            repo_url: str,
                            owner: str,
                            repo: str,
                            gate_summary: Dict,
                            overwork_score_result) -> str:
        """Create JSON summary of results."""
        import json
        
        data = {
            "repository": {
                "url": repo_url,
                "owner": owner,
                "name": repo
            },
            "timestamp": datetime.utcnow().isoformat(),
            "overwork_score": {
                "score": overwork_score_result.score,
                "band": overwork_score_result.band.value,
                "weakest_link": overwork_score_result.weakest_link,
                "component_scores": overwork_score_result.component_scores
            },
            "verification_firewall": {
                "total_gates": gate_summary["total_gates"],
                "passed": gate_summary["passed"],
                "failed": gate_summary["failed"],
                "warned": gate_summary["warned"]
            }
        }
        
        return json.dumps(data, indent=2)
    
    def _create_secret_report(self, secret_matches: List) -> str:
        """Create secret scan report."""
        lines = ["SECRET SCAN RESULTS", "=" * 50, ""]
        
        for match in secret_matches:
            lines.append(f"File: {match.file_path}")
            lines.append(f"Line: {match.line_number}")
            lines.append(f"Type: {match.secret_type}")
            lines.append(f"Matched: {match.matched_text}")
            lines.append("-" * 30)
            lines.append(match.context)
            lines.append("")
        
        return "\n".join(lines)
    
    def _create_claims_report(self, claims: List) -> str:
        """Create claims analysis report."""
        lines = ["CLAIM ANALYSIS", "=" * 50, ""]
        
        for claim in claims:
            lines.append(f"Line {claim.line_number}: {claim.text}")
            lines.append(f"Category: {claim.category.value}")
            lines.append(f"Evidence: {claim.evidence_level.value}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _create_gate_report(self, gate_summary: Dict) -> str:
        """Create verification firewall report."""
        lines = ["VERIFICATION FIREWALL RESULTS", "=" * 50, ""]
        
        lines.append(f"Total Gates: {gate_summary['total_gates']}")
        lines.append(f"Passed: {gate_summary['passed']}")
        lines.append(f"Failed: {gate_summary['failed']}")
        lines.append(f"Warned: {gate_summary['warned']}")
        lines.append("")
        lines.append("Gate Details:")
        lines.append("-" * 30)
        
        for gate in gate_summary["gates"]:
            lines.append(f"{gate['name']}: {gate['status'].upper()}")
            lines.append(f"  {gate['message']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _create_file_inventory(self, files: List[tuple]) -> str:
        """Create file inventory."""
        lines = ["FILE INVENTORY", "=" * 50, ""]
        
        for file_path, content in files:
            lines.append(f"{file_path} ({len(content)} bytes)")
        
        lines.append("")
        lines.append(f"Total files: {len(files)}")
        
        return "\n".join(lines)
    
    def _create_metadata(self, repo_url: str, owner: str, repo: str) -> str:
        """Create metadata file."""
        lines = [
            "OVERWORKER PACKAGE METADATA",
            "=" * 50,
            "",
            f"Repository: {owner}/{repo}",
            f"URL: {repo_url}",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "This package was generated by Overworker, an AI execution layer",
            "that converts repositories into verified, inspectable assets.",
            "",
            "Contents:",
            "- overworker_report.md: Main verification report",
            "- summary.json: JSON summary of results",
            "- secrets.txt: Secret scan details (if found)",
            "- claims.txt: Claim analysis details (if found)",
            "- gates.txt: Verification firewall details",
            "- files.txt: Complete file inventory",
            "- metadata.txt: This file"
        ]
        
        return "\n".join(lines)
