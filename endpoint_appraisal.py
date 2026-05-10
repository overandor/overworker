"""Endpoint appraisal - detects and appraises endpoints as e-services."""
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class EndpointCategory(Enum):
    DATA = "data"
    AUTH = "auth"
    COMPUTE = "compute"
    STORAGE = "storage"
    NOTIFICATION = "notification"
    WEBHOOK = "webhook"
    ADMIN = "admin"
    UNKNOWN = "unknown"


@dataclass
class AppraisedEndpoint:
    path: str
    method: HttpMethod
    category: EndpointCategory
    complexity_score: float
    value_score: float
    liquidity_score: float
    appraisal_value: float
    metadata: Dict


@dataclass
class EServiceAppraisal:
    endpoints: List[AppraisedEndpoint]
    total_value: float
    avg_value: float
    liquidity_index: float
    metadata: Dict


class EndpointAppraiser:
    """Detects and appraises endpoints as e-services."""
    
    def __init__(self):
        self.patterns = {
            'flask': [
                r'@app\.route\([\'"]([^\'"]+)[\'"]\)',
                r'@app\.get\([\'"]([^\'"]+)[\'"]\)',
                r'@app\.post\([\'"]([^\'"]+)[\'"]\)',
                r'@app\.put\([\'"]([^\'"]+)[\'"]\)',
                r'@app\.delete\([\'"]([^\'"]+)[\'"]\)',
            ],
            'fastapi': [
                r'@app\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]\)',
            ],
            'express': [
                r'app\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]\)',
            ],
            'django': [
                r'path\([\'"]([^\'"]+)[\'"]\)',
            ],
            'generic': [
                r'/(api|v1|v2)/([^/\s]+)',
                r'/(users|auth|data|compute|storage|webhook|admin)/([^/\s]*)',
            ]
        }
    
    def appraise_endpoints(self, 
                          files: List[Tuple[str, str]],
                          tokenized_repo) -> EServiceAppraisal:
        """Detect and appraise all endpoints in repository."""
        endpoints = []
        
        # Detect endpoints from code
        for file_path, content in files:
            file_endpoints = self._detect_endpoints_in_file(file_path, content)
            endpoints.extend(file_endpoints)
        
        # Remove duplicates
        unique_endpoints = self._deduplicate_endpoints(endpoints)
        
        # Appraise each endpoint
        appraised = []
        for endpoint in unique_endpoints:
            appraised_endpoint = self._appraise_endpoint(endpoint, files, tokenized_repo)
            appraised.append(appraised_endpoint)
        
        # Compute aggregate metrics
        total_value = sum(e.appraisal_value for e in appraised)
        avg_value = total_value / len(appraised) if appraised else 0
        liquidity_index = sum(e.liquidity_score for e in appraised) / len(appraised) if appraised else 0
        
        return EServiceAppraisal(
            endpoints=appraised,
            total_value=total_value,
            avg_value=avg_value,
            liquidity_index=liquidity_index,
            metadata={
                "total_endpoints": len(appraised),
                "categories": set(e.category.value for e in appraised)
            }
        )
    
    def _detect_endpoints_in_file(self, file_path: str, content: str) -> List[Dict]:
        """Detect endpoints in a single file."""
        endpoints = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Try different framework patterns
            for framework, patterns in self.patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, line)
                    if match:
                        if framework == 'fastapi':
                            method_str = match.group(1)
                            path = match.group(2)
                            method = HttpMethod(method_str.upper()) if method_str else HttpMethod.GET
                        elif framework == 'express':
                            method_str = match.group(1)
                            path = match.group(2)
                            method = HttpMethod(method_str.upper()) if method_str else HttpMethod.GET
                        else:
                            path = match.group(1) if match.groups() else match.group(0)
                            method = HttpMethod.GET
                        
                        endpoints.append({
                            "path": path,
                            "method": method,
                            "file": file_path,
                            "line": line_num
                        })
                        break
        
        return endpoints
    
    def _deduplicate_endpoints(self, endpoints: List[Dict]) -> List[Dict]:
        """Remove duplicate endpoints."""
        seen = set()
        unique = []
        
        for endpoint in endpoints:
            key = (endpoint["path"], endpoint["method"])
            if key not in seen:
                seen.add(key)
                unique.append(endpoint)
        
        return unique
    
    def _appraise_endpoint(self,
                          endpoint: Dict,
                          files: List[Tuple[str, str]],
                          tokenized_repo) -> AppraisedEndpoint:
        """Appraise a single endpoint."""
        path = endpoint["path"]
        method = endpoint["method"]
        
        # Determine category
        category = self._categorize_endpoint(path)
        
        # Compute complexity score
        complexity = self._compute_complexity_score(endpoint, files)
        
        # Compute value score
        value = self._compute_value_score(endpoint, category, complexity)
        
        # Compute liquidity score
        liquidity = self._compute_liquidity_score(endpoint, category)
        
        # Final appraisal value
        appraisal = value * complexity * liquidity
        
        return AppraisedEndpoint(
            path=path,
            method=method,
            category=category,
            complexity_score=complexity,
            value_score=value,
            liquidity_score=liquidity,
            appraisal_value=appraisal,
            metadata={
                "file": endpoint.get("file"),
                "line": endpoint.get("line")
            }
        )
    
    def _categorize_endpoint(self, path: str) -> EndpointCategory:
        """Categorize endpoint based on path."""
        path_lower = path.lower()
        
        if any(x in path_lower for x in ['login', 'register', 'auth', 'token', 'oauth']):
            return EndpointCategory.AUTH
        elif any(x in path_lower for x in ['data', 'query', 'search', 'list', 'get']):
            return EndpointCategory.DATA
        elif any(x in path_lower for x in ['compute', 'process', 'calculate', 'transform']):
            return EndpointCategory.COMPUTE
        elif any(x in path_lower for x in ['upload', 'download', 'file', 'storage', 's3']):
            return EndpointCategory.STORAGE
        elif any(x in path_lower for x in ['notify', 'webhook', 'callback', 'event']):
            return EndpointCategory.NOTIFICATION
        elif any(x in path_lower for x in ['admin', 'manage', 'config', 'settings']):
            return EndpointCategory.ADMIN
        else:
            return EndpointCategory.UNKNOWN
    
    def _compute_complexity_score(self, 
                                 endpoint: Dict,
                                 files: List[Tuple[str, str]]) -> float:
        """Compute complexity score based on endpoint implementation."""
        # Base complexity from path depth
        path_depth = endpoint["path"].count('/')
        base_complexity = min(path_depth / 5, 1.0)
        
        # Add complexity if endpoint has parameters
        has_params = '{' in endpoint["path"] or '<' in endpoint["path"]
        if has_params:
            base_complexity += 0.2
        
        return min(base_complexity, 1.0)
    
    def _compute_value_score(self,
                           endpoint: Dict,
                           category: EndpointCategory,
                           complexity: float) -> float:
        """Compute value score based on category and complexity."""
        # Base value by category
        category_values = {
            EndpointCategory.AUTH: 0.8,
            EndpointCategory.DATA: 0.6,
            EndpointCategory.COMPUTE: 0.7,
            EndpointCategory.STORAGE: 0.5,
            EndpointCategory.NOTIFICATION: 0.4,
            EndpointCategory.ADMIN: 0.3,
            EndpointCategory.UNKNOWN: 0.2,
        }
        
        base_value = category_values.get(category, 0.2)
        
        # Adjust by complexity
        adjusted_value = base_value * (1 + complexity * 0.5)
        
        return min(adjusted_value, 1.0)
    
    def _compute_liquidity_score(self,
                                endpoint: Dict,
                                category: EndpointCategory) -> float:
        """Compute liquidity score - how tradable the endpoint is."""
        # Higher liquidity for common, reusable endpoints
        high_liquidity_categories = {
            EndpointCategory.DATA,
            EndpointCategory.COMPUTE,
            EndpointCategory.AUTH
        }
        
        if category in high_liquidity_categories:
            return 0.8
        elif category == EndpointCategory.STORAGE:
            return 0.6
        elif category == EndpointCategory.NOTIFICATION:
            return 0.5
        else:
            return 0.3
