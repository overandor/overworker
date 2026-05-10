"""KPI computation engine - computes key performance indicators from repos."""
from typing import List, Dict, Tuple
from dataclasses import dataclass
import re


@dataclass
class KPI:
    name: str
    value: float
    unit: str
    description: str
    category: str


@dataclass
class KPIReport:
    kpis: List[KPI]
    overall_score: float
    metadata: Dict


class KPIEngine:
    """Computes KPIs from repository metrics."""
    
    def compute_kpis(self, 
                    files: List[Tuple[str, str]],
                    tokenized_repo,
                    readme: str = None) -> KPIReport:
        """Compute all KPIs for a repository."""
        kpis = []
        
        # Code Quality KPIs
        kpis.extend(self._compute_code_quality_kpis(files))
        
        # Activity KPIs
        kpis.extend(self._compute_activity_kpis(files))
        
        # Complexity KPIs
        kpis.extend(self._compute_complexity_kpis(files, tokenized_repo))
        
        # Documentation KPIs
        kpis.extend(self._compute_documentation_kpis(files, readme))
        
        # Maintainability KPIs
        kpis.extend(self._compute_maintainability_kpis(files))
        
        # Liquidity KPI (new)
        kpis.append(self._compute_liquidity_kpi(files, tokenized_repo))
        
        # Endpoint KPI (for e-service appraisal)
        kpis.append(self._compute_endpoint_kpi(tokenized_repo))
        
        # Compute overall score
        overall_score = self._compute_overall_score(kpis)
        
        return KPIReport(
            kpis=kpis,
            overall_score=overall_score,
            metadata={
                "total_kpis": len(kpis),
                "categories": set(k.category for k in kpis)
            }
        )
    
    def _compute_code_quality_kpis(self, files: List[Tuple[str, str]]) -> List[KPI]:
        """Compute code quality KPIs."""
        kpis = []
        
        # Lines of code
        total_loc = sum(len(content.split('\n')) for _, content in files)
        kpis.append(KPI(
            name="lines_of_code",
            value=total_loc,
            unit="lines",
            description="Total lines of code in repository",
            category="code_quality"
        ))
        
        # Code density (code vs total)
        code_files = [f for f, _ in files if self._is_code_file(f)]
        code_density = len(code_files) / len(files) if files else 0
        kpis.append(KPI(
            name="code_density",
            value=code_density,
            unit="ratio",
            description="Ratio of code files to total files",
            category="code_quality"
        ))
        
        return kpis
    
    def _compute_activity_kpis(self, files: List[Tuple[str, str]]) -> List[KPI]:
        """Compute activity KPIs."""
        kpis = []
        
        # File count
        kpis.append(KPI(
            name="file_count",
            value=len(files),
            unit="files",
            description="Total number of files in repository",
            category="activity"
        ))
        
        # Average file size
        total_size = sum(len(content) for _, content in files)
        avg_size = total_size / len(files) if files else 0
        kpis.append(KPI(
            name="avg_file_size",
            value=avg_size,
            unit="bytes",
            description="Average file size in repository",
            category="activity"
        ))
        
        return kpis
    
    def _compute_complexity_kpis(self, 
                                  files: List[Tuple[str, str]],
                                  tokenized_repo) -> List[KPI]:
        """Compute complexity KPIs."""
        kpis = []
        
        # Token diversity
        if tokenized_repo and tokenized_repo.unique_tokens > 0:
            diversity = tokenized_repo.unique_tokens / tokenized_repo.total_tokens
            kpis.append(KPI(
                name="token_diversity",
                value=diversity,
                unit="ratio",
                description="Ratio of unique tokens to total tokens",
                category="complexity"
            ))
        
        # Function count
        func_count = sum(1 for _, content in files 
                        for line in content.split('\n')
                        if re.search(r'def\s+\w+|function\s+\w+', line))
        kpis.append(KPI(
            name="function_count",
            value=func_count,
            unit="functions",
            description="Total number of functions in codebase",
            category="complexity"
        ))
        
        return kpis
    
    def _compute_documentation_kpis(self,
                                    files: List[Tuple[str, str]],
                                    readme: str = None) -> List[KPI]:
        """Compute documentation KPIs."""
        kpis = []
        
        # README coverage
        has_readme = 1.0 if readme and len(readme) > 100 else 0.0
        kpis.append(KPI(
            name="readme_coverage",
            value=has_readme,
            unit="ratio",
            description="Whether repository has substantial README",
            category="documentation"
        ))
        
        # Documentation files
        doc_files = [f for f, _ in files if f.endswith(('.md', '.rst', '.txt'))]
        doc_ratio = len(doc_files) / len(files) if files else 0
        kpis.append(KPI(
            name="documentation_ratio",
            value=doc_ratio,
            unit="ratio",
            description="Ratio of documentation files to total files",
            category="documentation"
        ))
        
        return kpis
    
    def _compute_maintainability_kpis(self, 
                                      files: List[Tuple[str, str]]) -> List[KPI]:
        """Compute maintainability KPIs."""
        kpis = []
        
        # Test coverage indicator
        test_files = [f for f, _ in files if 'test' in f.lower()]
        test_ratio = len(test_files) / len(files) if files else 0
        kpis.append(KPI(
            name="test_coverage_indicator",
            value=test_ratio,
            unit="ratio",
            description="Ratio of test files to total files",
            category="maintainability"
        ))
        
        # Config file presence
        config_files = [f for f, _ in files if f.endswith(('.json', '.yaml', '.yml', '.toml'))]
        has_config = 1.0 if config_files else 0.0
        kpis.append(KPI(
            name="has_config",
            value=has_config,
            unit="ratio",
            description="Whether repository has configuration files",
            category="maintainability"
        ))
        
        return kpis
    
    def _compute_liquidity_kpi(self,
                              files: List[Tuple[str, str]],
                              tokenized_repo) -> KPI:
        """Compute liquidity KPI - measures tradability/interest."""
        # Liquidity based on:
        # 1. Code completeness (test coverage, config presence)
        # 2. Documentation quality
        # 3. Endpoint availability (for e-services)
        # 4. Token diversity (complexity/interest)
        
        test_files = [f for f, _ in files if 'test' in f.lower()]
        test_score = min(len(test_files) / max(len(files), 1) * 2, 1.0)
        
        doc_files = [f for f, _ in files if f.endswith(('.md', '.rst'))]
        doc_score = min(len(doc_files) / max(len(files), 1) * 3, 1.0)
        
        config_files = [f for f, _ in files if f.endswith(('.json', '.yaml', '.yml'))]
        config_score = 1.0 if config_files else 0.5
        
        endpoint_score = 0.0
        if tokenized_repo:
            endpoints = [t for t in tokenized_repo.tokens if t.type == 'endpoint']
            endpoint_score = min(len(endpoints) / 10, 1.0)
        
        # Weighted liquidity score
        liquidity = (test_score * 0.3 + doc_score * 0.3 + 
                    config_score * 0.2 + endpoint_score * 0.2)
        
        return KPI(
            name="liquidity_score",
            value=liquidity,
            unit="ratio",
            description="Liquidity score - measures tradability and market interest",
            category="liquidity"
        )
    
    def _compute_endpoint_kpi(self, tokenized_repo) -> KPI:
        """Compute endpoint KPI for e-service appraisal."""
        if not tokenized_repo:
            return KPI(
                name="endpoint_count",
                value=0,
                unit="endpoints",
                description="Number of API endpoints detected",
                category="e_service"
            )
        
        endpoints = [t for t in tokenized_repo.tokens if t.type == 'endpoint']
        
        return KPI(
            name="endpoint_count",
            value=len(endpoints),
            unit="endpoints",
            description="Number of API endpoints detected for e-service valuation",
            category="e_service"
        )
    
    def _compute_overall_score(self, kpis: List[KPI]) -> float:
        """Compute overall KPI score."""
        if not kpis:
            return 0.0
        
        # Normalize and weight different categories
        category_weights = {
            "code_quality": 0.2,
            "activity": 0.15,
            "complexity": 0.15,
            "documentation": 0.2,
            "maintainability": 0.15,
            "liquidity": 0.15
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for kpi in kpis:
            weight = category_weights.get(kpi.category, 0.1)
            # Normalize value to 0-1 range if needed
            normalized = min(kpi.value, 1.0) if kpi.unit == "ratio" else min(kpi.value / 1000, 1.0)
            weighted_sum += normalized * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _is_code_file(self, file_path: str) -> bool:
        """Check if file is a code file."""
        code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.rs', '.go', '.java', '.rb', '.php'}
        return any(file_path.endswith(ext) for ext in code_extensions)
