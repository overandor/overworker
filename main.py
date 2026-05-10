"""Overworker FastAPI dashboard - GitHub repo to verified package ZIP."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from github_ingestion import GitHubIngestor, RepoStructure
from secret_scanner import SecretScanner, SecretMatch
from claim_labeler import ClaimLabeler, Claim
from verification_firewall import VerificationFirewall
from overwork_score import OverworkScorer
from report_generator import ReportGenerator
from zip_exporter import ZIPExporter
from tokenization import RepoTokenizer, TokenizedRepo
from kpi_computation import KPIEngine, KPIReport
from endpoint_appraisal import EndpointAppraiser, EServiceAppraisal
from inverse_derivative import InverseDerivativeEngine, DerivativePortfolio
import subprocess
import os


app = FastAPI(title="Overworker", description="AI execution layer for repo verification")


class RepoRequest(BaseModel):
    url: str

    def validate_github_url(self):
        """Validate that URL is a GitHub repository URL."""
        import re
        pattern = r'^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+/?$'
        if not re.match(pattern, self.url):
            raise ValueError("URL must be a valid GitHub repository URL (e.g., https://github.com/owner/repo)")
        return True


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with repo input form."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Overworker - GitHub Repo Verification</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            input[type="text"] {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
                margin-bottom: 20px;
                box-sizing: border-box;
            }
            input[type="text"]:focus {
                border-color: #0066cc;
                outline: none;
            }
            button {
                background: #0066cc;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 16px;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
            }
            button:hover {
                background: #0052a3;
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .examples {
                margin-top: 20px;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 4px;
            }
            .examples h3 {
                margin-top: 0;
                font-size: 14px;
                color: #666;
            }
            .example-link {
                color: #0066cc;
                text-decoration: none;
                cursor: pointer;
            }
            .example-link:hover {
                text-decoration: underline;
            }
            #loading {
                display: none;
                text-align: center;
                margin-top: 20px;
            }
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #0066cc;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            #results {
                display: none;
                margin-top: 30px;
            }
            .score-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .score-value {
                font-size: 48px;
                font-weight: bold;
            }
            .score-band {
                font-size: 24px;
                margin-top: 10px;
            }
            .download-btn {
                background: #28a745;
                margin-top: 20px;
            }
            .download-btn:hover {
                background: #218838;
            }
            .kpi-section {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .kpi-section h3 {
                margin-top: 0;
                color: #333;
                font-size: 16px;
                margin-bottom: 15px;
            }
            .kpi-item {
                padding: 8px 0;
                border-bottom: 1px solid #eee;
                font-size: 14px;
            }
            .kpi-item:last-child {
                border-bottom: none;
            }
            .error {
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 4px;
                margin-top: 20px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Overworker</h1>
            <p class="subtitle">AI execution layer - GitHub repo to verified package ZIP</p>
            
            <form id="repoForm">
                <input type="text" id="repoUrl" placeholder="https://github.com/owner/repo" required>
                <button type="submit" id="submitBtn">Analyze Repository</button>
            </form>
            
            <div class="examples">
                <h3>Example repositories:</h3>
                <a class="example-link" onclick="setUrl('https://github.com/torvalds/linux')">torvalds/linux</a> •
                <a class="example-link" onclick="setUrl('https://github.com/python/cpython')">python/cpython</a> •
                <a class="example-link" onclick="setUrl('https://github.com/facebook/react')">facebook/react</a>
            </div>
            
            <div id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 15px; color: #666;">Analyzing repository...</p>
            </div>
            
            <div id="error" class="error"></div>
            
            <div id="results">
                <div class="score-card">
                    <div class="score-value" id="scoreValue">0.000</div>
                    <div class="score-band" id="scoreBand">FRAGMENT</div>
                    <div style="margin-top: 10px; opacity: 0.9;">Weakest Link: <span id="weakestLink">-</span></div>
                </div>
                
                <div class="kpi-section">
                    <h3>KPI Report</h3>
                    <div id="kpiList"></div>
                </div>
                
                <div class="kpi-section">
                    <h3>E-Service Appraisal</h3>
                    <div id="eServiceData"></div>
                </div>
                
                <div class="kpi-section">
                    <h3>Derivative Portfolio</h3>
                    <div id="derivativeData"></div>
                </div>
                
                <button class="download-btn" onclick="downloadZip()">Download ZIP Package</button>
            </div>
        </div>
        
        <script>
            let currentZipUrl = null;
            
            function setUrl(url) {
                document.getElementById('repoUrl').value = url;
            }
            
            document.getElementById('repoForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const url = document.getElementById('repoUrl').value;
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').style.display = 'none';
                document.getElementById('error').style.display = 'none';
                document.getElementById('submitBtn').disabled = true;
                
                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url })
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.detail || 'Analysis failed');
                    }
                    
                    document.getElementById('scoreValue').textContent = data.score.toFixed(3);
                    document.getElementById('scoreBand').textContent = data.band.toUpperCase();
                    document.getElementById('weakestLink').textContent = data.weakest_link;
                    currentZipUrl = data.zip_url;
                    
                    // Display KPIs
                    const kpiList = document.getElementById('kpiList');
                    kpiList.innerHTML = '';
                    if (data.kpi_report && data.kpi_report.kpis) {
                        data.kpi_report.kpis.forEach(kpi => {
                            const div = document.createElement('div');
                            div.className = 'kpi-item';
                            div.innerHTML = `<strong>${kpi.name}:</strong> ${kpi.value.toFixed(3)} ${kpi.unit} (${kpi.category})`;
                            kpiList.appendChild(div);
                        });
                    }
                    
                    // Display E-Service Appraisal
                    const eServiceData = document.getElementById('eServiceData');
                    if (data.e_service_appraisal) {
                        eServiceData.innerHTML = `
                            <div class="kpi-item"><strong>Total Endpoints:</strong> ${data.e_service_appraisal.total_endpoints}</div>
                            <div class="kpi-item"><strong>Total Value:</strong> ${data.e_service_appraisal.total_value.toFixed(3)}</div>
                            <div class="kpi-item"><strong>Avg Value:</strong> ${data.e_service_appraisal.avg_value.toFixed(3)}</div>
                            <div class="kpi-item"><strong>Liquidity Index:</strong> ${data.e_service_appraisal.liquidity_index.toFixed(3)}</div>
                        `;
                    }
                    
                    // Display Derivative Portfolio
                    const derivativeData = document.getElementById('derivativeData');
                    if (data.derivative_portfolio) {
                        const pricing = data.derivative_portfolio.pricing || {};
                        derivativeData.innerHTML = `
                            <div class="kpi-item"><strong>Total Tokens:</strong> ${data.derivative_portfolio.total_tokens}</div>
                            <div class="kpi-item"><strong>Total Notional:</strong> ${data.derivative_portfolio.total_notional.toFixed(3)}</div>
                            <div class="kpi-item"><strong>Weighted Inverse:</strong> ${data.derivative_portfolio.weighted_inverse_value.toFixed(3)}</div>
                            <div class="kpi-item"><strong>Risk Score:</strong> ${data.derivative_portfolio.risk_score.toFixed(3)}</div>
                            <div class="kpi-item"><strong>Fair Value:</strong> ${(pricing.fair_value || 0).toFixed(3)}</div>
                            <div class="kpi-item"><strong>Expected Return:</strong> ${((pricing.expected_return || 0) * 100).toFixed(1)}%</div>
                        `;
                    }
                    
                    document.getElementById('results').style.display = 'block';
                } catch (err) {
                    document.getElementById('error').textContent = err.message;
                    document.getElementById('error').style.display = 'block';
                } finally {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('submitBtn').disabled = false;
                }
            });
            
            function downloadZip() {
                if (currentZipUrl) {
                    window.location.href = currentZipUrl;
                }
            }
        </script>
    </body>
    </html>
    """


def use_installed_snap2txt(directory: str) -> str:
    """Use installed snap2txt package to scan local directory."""
    original_dir = os.getcwd()
    try:
        os.chdir(directory)
        subprocess.run(["snap2txt"], check=True, capture_output=True, timeout=60)
        
        # Read the generated file
        output_file = os.path.join(directory, "project_contents.txt")
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                return f.read()
        return ""
    finally:
        os.chdir(original_dir)


def is_local_directory(path: str) -> bool:
    """Check if path is a local directory."""
    return os.path.isdir(path) and not path.startswith("http")


def parse_snap2txt_output(snap_content: str) -> list:
    """Parse snap2txt output into RepoFile objects."""
    from github_ingestion import RepoFile
    
    files = []
    lines = snap_content.split('\n')
    
    current_file = None
    current_content = []
    in_code_block = False
    
    for line in lines:
        if line.startswith("Project Structure:"):
            continue
        elif line.startswith("File Contents:"):
            continue
        elif line.strip() == "```":
            in_code_block = not in_code_block
            continue
        elif line.endswith(":") and not in_code_block:
            if current_file and current_content:
                content = '\n'.join(current_content)
                files.append(RepoFile(
                    path=current_file,
                    content=content,
                    size=len(content)
                ))
            current_file = line.rstrip(':')
            current_content = []
        elif current_file and in_code_block:
            current_content.append(line)
    
    # Add last file
    if current_file and current_content:
        content = '\n'.join(current_content)
        files.append(RepoFile(
            path=current_file,
            content=content,
            size=len(content)
        ))
    
    return files


def extract_readme(files: list) -> str:
    """Extract README content from files."""
    for file in files:
        if "README" in file.path.upper():
            return file.content
    return None


@app.post("/analyze")
async def analyze_repo(request: RepoRequest):
    """Analyze a GitHub repository or local directory and return results."""
    
    # Validate GitHub URL
    try:
        request.validate_github_url()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    ingestor = GitHubIngestor()
    secret_scanner = SecretScanner()
    claim_labeler = ClaimLabeler()
    firewall = VerificationFirewall()
    scorer = OverworkScorer()
    report_gen = ReportGenerator()
    zip_exporter = ZIPExporter()
    tokenizer = RepoTokenizer()
    kpi_engine = KPIEngine()
    endpoint_appraiser = EndpointAppraiser()
    derivative_engine = InverseDerivativeEngine()
    
    try:
        # Step 1: Ingest repo (detect local vs remote)
        if is_local_directory(request.url):
            # Use installed snap2txt for local directory
            snap_content = use_installed_snap2txt(request.url)
            # Parse snap2txt output to create RepoStructure
            files = parse_snap2txt_output(snap_content)
            repo_structure = RepoStructure(
                owner="local",
                repo=os.path.basename(request.url),
                files=files,
                readme=extract_readme(files)
            )
        else:
            # Use custom remote_snap2txt + git clone for remote repos
            repo_structure: RepoStructure = await ingestor.ingest_repo(request.url)
        
        # Prepare file list for scanners
        files = [(f.path, f.content) for f in repo_structure.files]
        
        # Step 2: Scan for secrets
        secret_matches: list[SecretMatch] = secret_scanner.scan_repo(files)
        secret_summary = secret_scanner.summarize(secret_matches)
        
        # Step 3: Label claims
        claims: list[Claim] = claim_labeler.label_all_claims(
            repo_structure.readme, files
        )
        claim_summary = claim_labeler.summarize(claims)
        
        # Step 4: Run verification firewall
        firewall.run_all_gates(
            files, repo_structure.readme, secret_matches, claims
        )
        gate_summary = firewall.get_summary()
        
        # Step 5: Compute Overwork Score
        score_result = scorer.compute_score(
            files, repo_structure.readme, secret_summary, 
            gate_summary, claim_summary
        )
        
        # Step 6: Tokenize repo
        tokenized_repo: TokenizedRepo = tokenizer.tokenize_repo(files)
        
        # Step 7: Compute KPIs
        kpi_report: KPIReport = kpi_engine.compute_kpis(
            files, tokenized_repo, repo_structure.readme
        )
        
        # Step 8: Appraise endpoints as e-services
        e_service_appraisal: EServiceAppraisal = endpoint_appraiser.appraise_endpoints(
            files, tokenized_repo
        )
        
        # Step 9: Create inverse derivatives
        derivative_portfolio: DerivativePortfolio = derivative_engine.create_inverse_derivatives(
            e_service_appraisal
        )
        
        # Step 10: Generate report with secret redaction
        report = report_gen.generate_report(
            request.url,
            repo_structure.owner,
            repo_structure.repo,
            repo_structure.readme,
            secret_summary,
            claim_summary,
            gate_summary,
            score_result,
            len(files),
            secret_matches
        )
        
        # Step 11: Export ZIP
        zip_data = zip_exporter.export(
            request.url,
            repo_structure.owner,
            repo_structure.repo,
            report,
            secret_matches,
            claims,
            gate_summary,
            score_result,
            files
        )
        
        # Store ZIP in memory with timestamp for cleanup (in production, use S3 or similar)
        import time
        zip_filename = f"{repo_structure.repo}_overworker_package_{int(time.time())}.zip"
        zip_storage[zip_filename] = {
            "data": zip_data,
            "timestamp": time.time(),
            "repo_url": request.url
        }
        
        return {
            "score": score_result.score,
            "band": score_result.band.value,
            "weakest_link": score_result.weakest_link,
            "component_scores": score_result.component_scores,
            "kpi_report": {
                "kpis": [
                    {
                        "name": k.name,
                        "value": k.value,
                        "unit": k.unit,
                        "category": k.category
                    }
                    for k in kpi_report.kpis
                ],
                "overall_score": kpi_report.overall_score
            },
            "e_service_appraisal": {
                "total_endpoints": e_service_appraisal.metadata.get("total_endpoints", 0),
                "total_value": e_service_appraisal.total_value,
                "avg_value": e_service_appraisal.avg_value,
                "liquidity_index": e_service_appraisal.liquidity_index
            },
            "derivative_portfolio": {
                "total_tokens": len(derivative_portfolio.tokens),
                "total_notional": derivative_portfolio.total_notional,
                "weighted_inverse_value": derivative_portfolio.weighted_inverse_value,
                "risk_score": derivative_portfolio.risk_score,
                "pricing": derivative_engine.compute_derivative_pricing(derivative_portfolio)
            },
            "zip_url": f"/download/{zip_filename}",
            "zip_data": zip_data.hex(),
            "filename": zip_filename
        }
        
    finally:
        await ingestor.close()


# In-memory ZIP storage (for demo purposes)
zip_storage = {}


@app.get("/download/{filename}")
async def download_zip(filename: str):
    """Download ZIP package from in-memory storage."""
    import time
    
    # Clean up old ZIPs (older than 1 hour)
    current_time = time.time()
    keys_to_delete = [k for k, v in zip_storage.items() if current_time - v["timestamp"] > 3600]
    for key in keys_to_delete:
        del zip_storage[key]
    
    if filename not in zip_storage:
        raise HTTPException(status_code=404, detail="ZIP not found. Please analyze a repository first.")
    
    zip_entry = zip_storage[filename]
    zip_data = zip_entry["data"]
    from fastapi.responses import Response
    return Response(content=zip_data, media_type="application/zip", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
