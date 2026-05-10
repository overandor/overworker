# Overworker

**AI execution layer - GitHub repo to verified package ZIP**

Overworker converts messy repositories into verified, inspectable, saleable assets through automated analysis, scoring, and packaging.

## What It Does

Paste a public GitHub URL → Overworker analyzes the repository and produces:

- **Overwork Score**: Weakest-link commercialization readiness score (0.0 - 1.0)
- **Verification Firewall**: 10 quality gates (README, secrets, tests, config, etc.)
- **Secret Scanner**: Detects API keys, tokens, and sensitive data
- **Claim Labeler**: Extracts and verifies README claims against code
- **KPI Computation**: Computes key performance indicators including liquidity
- **E-Service Appraisal**: Detects and appraises API endpoints as tradable e-services
- **Inverse Derivatives**: Tokenizes appraised endpoints into inverse derivative contracts
- **Markdown Report**: Comprehensive analysis document
- **ZIP Package**: Downloadable archive with all artifacts

## Demo Flow

1. User pastes GitHub URL
2. System clones repository using git
3. Secret scanner checks for sensitive data
4. Claim labeler extracts README claims
5. Verification firewall runs quality gates
6. Tokenization engine tokenizes repo content
7. KPI engine computes performance indicators including liquidity
8. Endpoint appraiser detects and appraises API endpoints as e-services
9. Inverse derivative engine creates derivative tokens from endpoints
10. Overwork Score computes readiness
11. Markdown report is generated
12. ZIP package is exported
13. Dashboard displays results with KPIs and derivative metrics

## Quick Start

### Prerequisites

- Python 3.8+
- Git (required for cloning repositories)

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py

# Open browser
# http://localhost:8000
```

### Deploy to Render

```bash
# Install Render CLI
npm i -g @render/cli

# Login and deploy
render login
render deploy
```

Or connect your GitHub repo to Render and use the included `render.yaml`.

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Use the included `vercel.json` configuration.

## Overwork Score Bands

| Score | Band | Description |
|-------|------|-------------|
| 0.85 - 1.0 | PRODUCTION_READY | Ready for production deployment |
| 0.70 - 0.84 | DEMO_READY | Suitable for demos and prototypes |
| 0.50 - 0.69 | SCAFFOLD | Basic structure present, needs work |
| 0.30 - 0.49 | PROVENANCE | Minimal provenance, mostly archival |
| 0.0 - 0.29 | FRAGMENT | Incomplete or fragmented |

## Verification Firewall Gates

1. **has_readme** - Repository has a README file
2. **readme_substance** - README has substantial content
3. **has_code** - Repository has code files
4. **no_critical_secrets** - No critical secrets detected
5. **has_license** - Repository has a license file
6. **has_tests** - Repository has test files
7. **has_documentation** - Repository has documentation
8. **claim_verification** - Claims have supporting evidence
9. **file_count** - Repository has sufficient files
10. **has_config** - Repository has configuration files

## Secret Scanner Patterns

Detects:
- AWS Access Keys
- AWS Secret Keys
- GitHub Tokens
- GitHub OAuth tokens
- Slack Tokens
- Stripe API Keys
- Generic API keys
- Generic secrets
- Passwords in code
- Private keys
- Database URLs
- JWT tokens
- Email addresses

## Claim Categories

- **feature** - Feature claims
- **performance** - Performance claims
- **security** - Security claims
- **compliance** - Compliance claims
- **integration** - Integration claims
- **adoption** - Adoption/user claims
- **revenue** - Revenue/pricing claims
- **technical** - Technical/architecture claims
- **marketing** - Marketing/positioning claims

## API Endpoints

### `GET /`
Returns the web interface.

### `POST /analyze`
Analyzes a GitHub repository.

**Request:**
```json
{
  "url": "https://github.com/owner/repo"
}
```

**Response:**
```json
{
  "score": 0.723,
  "band": "demo_ready",
  "weakest_link": "testing",
  "component_scores": {
    "documentation": 0.8,
    "code_quality": 0.9,
    "security": 1.0,
    "testing": 0.5,
    "configuration": 0.7,
    "claims_verification": 0.6,
    "file_structure": 0.8
  },
  "zip_url": "/download/repo_overworker_package.zip"
}
```

## ZIP Package Contents

Each exported ZIP includes:

- `{repo}_overworker_report.md` - Main verification report
- `{repo}_summary.json` - JSON summary of results
- `{repo}_secrets.txt` - Secret scan details (if found)
- `{repo}_claims.txt` - Claim analysis details (if found)
- `{repo}_gates.txt` - Verification firewall details
- `{repo}_files.txt` - Complete file inventory
- `metadata.txt` - Package metadata

## Architecture

```
main.py (FastAPI dashboard)
├── github_ingestion.py (Repo fetching via git)
├── secret_scanner.py (Secret detection)
├── claim_labeler.py (Claim extraction)
├── verification_firewall.py (Quality gates)
├── overwork_score.py (Scoring engine)
├── tokenization.py (Content tokenization)
├── kpi_computation.py (KPI & liquidity computation)
├── endpoint_appraisal.py (E-service valuation)
├── inverse_derivative.py (Derivative creation)
├── report_generator.py (Markdown reports)
└── zip_exporter.py (Package export)
```

## Financial Features

### KPI Computation

Computes key performance indicators from repository metrics:

- **Code Quality KPIs**: Lines of code, code density
- **Activity KPIs**: File count, average file size
- **Complexity KPIs**: Token diversity, function count
- **Documentation KPIs**: README coverage, documentation ratio
- **Maintainability KPIs**: Test coverage indicator, config presence
- **Liquidity KPI**: Measures tradability and market interest based on completeness, documentation, and endpoint availability

### E-Service Appraisal

Detects and appraises API endpoints as tradable e-services:

- Detects endpoints from Flask, FastAPI, Express, Django, and generic patterns
- Categorizes endpoints: Auth, Data, Compute, Storage, Notification, Admin
- Computes complexity score based on path depth and parameters
- Computes value score based on category and complexity
- Computes liquidity score based on endpoint type and reusability
- Appraises each endpoint with final appraisal value

### Inverse Derivatives

Creates inverse derivative contracts from appraised endpoints:

- Generates unique token IDs for each endpoint
- Computes inverse value (inverse of appraisal value)
- Sets collateral ratio (default 50%)
- Computes maturity date (default 30 days)
- Computes strike price (10% premium over appraisal)
- Calculates portfolio risk score based on concentration, volatility, and collateral
- Computes pricing metrics: fair value, required collateral, leverage ratio, expected return

## Use Cases

- **Investor Due Diligence**: Quick repo assessment for funding decisions
- **Acquisition Analysis**: Evaluate target codebases
- **Open Source Audit**: Verify project health before contribution
- **Internal QA**: Automated repo health checks
- **Portfolio Management**: Track readiness across multiple repos
- **E-Service Valuation**: Appraise API endpoints as tradable assets
- **Derivative Trading**: Create inverse derivatives from endpoint appraisals
- **Liquidity Assessment**: Measure tradability of repo assets

## Limitations

- Only analyzes public GitHub repositories
- Requires Git to be installed on the system
- Text-based analysis (doesn't run code)
- Pattern-based secret detection (may have false positives)
- Claim verification is heuristic-based
- No persistent storage in demo mode
- Repo cloning may be slow for large repositories
- Financial derivatives are for demonstration only, not actual trading
- E-service appraisal is heuristic-based and not financial advice

## Future Expansions

- Private repo support (with Git authentication)
- Code execution and testing
- Dependency analysis
- License compliance checking
- CI/CD integration
- Multi-repo batch analysis
- Historical score tracking
- Custom gate configurations
- Cached repo analysis for faster repeated scans

## License

MIT

## About Overworker

Overworker is an AI execution layer that converts messy human/AI work into verified, inspectable, saleable assets. It applies weakest-link scoring and verification firewalls to turn prototypes, repos, chats, and R&D archives into production-ready packages.

**Core primitives:**
- **Verification Firewall**: Deterministic quality gate layer
- **Overwork Score**: Weakest-link commercialization readiness
- **Secret Scanner**: Automated sensitive data detection
- **Claim Labeler**: README claim extraction and verification

Built for founders, operators, and investors who need to quickly assess and package technical work.
