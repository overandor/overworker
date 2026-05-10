"""Overworker - AI execution layer for GitHub repo verification."""
import os
import subprocess
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse
from pydantic import BaseModel
import stripe
from github_ingestion import GitHubIngestor, RepoFile, RepoStructure
from secret_scanner import SecretScanner, SecretMatch
from claim_labeler import ClaimLabeler, Claim
from verification_firewall import VerificationFirewall
from overwork_score import OverworkScorer, ReadinessBand
from tokenization import TokenizedRepo
from kpi_computation import KPIEngine, KPIReport
from endpoint_appraisal import EndpointAppraiser, EServiceAppraisal
from inverse_derivative import DerivativePortfolio, InverseDerivativeEngine
from report_generator import ReportGenerator
from zip_exporter import ZIPExporter


class RepoRequest(BaseModel):
    url: str

    def validate_github_url(self):
        """Validate that URL is a GitHub repository URL."""
        import re
        pattern = r'^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+/?$'
        if not re.match(pattern, self.url):
            raise ValueError("URL must be a valid GitHub repository URL (e.g., https://github.com/owner/repo)")
        return True


app = FastAPI()

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "price_placeholder")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard HTML - direct file read to avoid Jinja2 caching issues."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/static/styles.css")
async def styles_css():
    """Serve the CSS file."""
    css_path = os.path.join(os.path.dirname(__file__), "templates", "styles.css")
    from fastapi.responses import FileResponse
    return FileResponse(css_path, media_type="text/css")


@app.get("/features", response_class=HTMLResponse)
async def features():
    """Serve the features page."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "features.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/pricing", response_class=HTMLResponse)
async def pricing():
    """Serve the pricing page."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "pricing.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/about", response_class=HTMLResponse)
async def about():
    """Serve the about page."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "about.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/contact", response_class=HTMLResponse)
async def contact():
    """Serve the contact page."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "contact.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/docs", response_class=HTMLResponse)
async def docs():
    """Serve the documentation page."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "docs.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


class CheckoutRequest(BaseModel):
    plan_id: str


@app.post("/create-checkout-session")
async def create_checkout_session(request_data: CheckoutRequest):
    """Create a Stripe checkout session for subscription."""
    try:
        # Plan pricing
        plans = {
            "starter": {"price": 0, "name": "Starter"},
            "professional": {"price": 2900, "name": "Professional"},  # $29.00 in cents
            "enterprise": {"price": 9900, "name": "Enterprise"}  # $99.00 in cents
        }
        
        plan = plans.get(request_data.plan_id)
        if not plan:
            raise HTTPException(status_code=400, detail="Invalid plan ID")
        
        if plan["price"] == 0:
            # Free plan - no checkout needed
            return {"url": None, "free": True}
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Overworker {plan['name']} Plan",
                        },
                        "unit_amount": plan["price"],
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://huggingface.co/spaces/luguog/overworker?success=true",
            cancel_url="https://huggingface.co/spaces/luguog/overworker?canceled=true",
        )
        
        return {"url": checkout_session.url, "free": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    score_engine = OverworkScorer()
    report_gen = ReportGenerator()
    zip_exporter = ZIPExporter()
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
        score_result = score_engine.compute_score(
            files, repo_structure.readme, secret_summary, 
            gate_summary, claim_summary
        )
        
        # Step 6: Tokenize repo
        from tokenization import tokenize_repo
        tokenized_repo: TokenizedRepo = tokenize_repo(files)
        
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
        
    except Exception as e:
        import traceback
        return {
            "error": f"Analysis failed: {str(e)}",
            "details": traceback.format_exc()
        }
    finally:
        try:
            await ingestor.close()
        except:
            pass


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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
