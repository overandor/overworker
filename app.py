"""Hugging Face Spaces app for Overworker - Gradio interface."""
import gradio as gr
import asyncio
from main import analyze_repo, RepoRequest


def analyze_repo_sync(url: str) -> dict:
    """Synchronous wrapper for async analyze_repo."""
    try:
        request = RepoRequest(url=url)
        request.validate_github_url()
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(analyze_repo(request))
        loop.close()
        
        return result
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


def format_result(result: dict) -> str:
    """Format analysis result for display."""
    if "error" in result:
        return f"❌ Error: {result['error']}"
    
    lines = []
    lines.append("# Overworker Analysis Results")
    lines.append("")
    lines.append(f"**Score:** {result['score']:.3f}/1.0")
    lines.append(f"**Band:** {result['band']}")
    lines.append(f"**Weakest Link:** {result['weakest_link']}")
    lines.append("")
    
    lines.append("## Component Scores")
    for component, score in result['component_scores'].items():
        lines.append(f"- **{component}:** {score:.2f}")
    lines.append("")
    
    lines.append("## KPI Report")
    lines.append(f"**Overall Score:** {result['kpi_report']['overall_score']:.3f}")
    lines.append("")
    for kpi in result['kpi_report']['kpis']:
        lines.append(f"- **{kpi['name']}:** {kpi['value']} {kpi['unit']}")
    lines.append("")
    
    lines.append("## E-Service Appraisal")
    lines.append(f"**Total Endpoints:** {result['e_service_appraisal']['total_endpoints']}")
    lines.append(f"**Total Value:** {result['e_service_appraisal']['total_value']:.3f}")
    lines.append(f"**Liquidity Index:** {result['e_service_appraisal']['liquidity_index']:.3f}")
    lines.append("")
    
    lines.append("## Download Package")
    lines.append(f"ZIP Filename: {result['filename']}")
    lines.append("")
    lines.append("Note: ZIP download available in web interface only")
    
    return "\n".join(lines)


# Create Gradio interface
with gr.Blocks(title="Overworker - GitHub Repo Verification") as demo:
    gr.Markdown("# 🏗️ Overworker")
    gr.Markdown("**AI execution layer - GitHub repo to verified package**")
    gr.Markdown("")
    
    with gr.Row():
        url_input = gr.Textbox(
            label="GitHub Repository URL",
            placeholder="https://github.com/owner/repo",
            value="https://github.com/overandor/overworker"
        )
        analyze_btn = gr.Button("Analyze", variant="primary")
    
    with gr.Row():
        result_output = gr.Markdown(label="Analysis Results")
    
    with gr.Row():
        zip_filename = gr.Textbox(label="ZIP Filename", interactive=False)
        zip_download = gr.File(label="Download ZIP Package")
    
    analyze_btn.click(
        fn=lambda url: format_result(analyze_repo_sync(url)),
        inputs=[url_input],
        outputs=[result_output]
    )
    
    # Note: ZIP download not available in Gradio interface
    # Users can use the main FastAPI app for full ZIP download functionality
    
    gr.Markdown("---")
    gr.Markdown("## About")
    gr.Markdown("Overworker analyzes GitHub repositories and generates verification reports with:")
    gr.Markdown("- **Overwork Score**: Commercialization readiness score")
    gr.Markdown("- **Verification Firewall**: 10 quality gates")
    gr.Markdown("- **Secret Scanner**: Detects sensitive data")
    gr.Markdown("- **Claim Labeler**: Extracts and verifies README claims")
    gr.Markdown("- **KPI Computation**: Heuristic performance metrics")
    gr.Markdown("- **E-Service Appraisal**: Analyzes API endpoints")
    gr.Markdown("- **Heuristic Derivatives**: Non-financial analytics")
    gr.Markdown("")
    gr.Markdown("**⚠️ Note:** This is a demonstration system. All financial metrics are heuristic analytics for codebase assessment only, not tradable instruments.")


if __name__ == "__main__":
    demo.launch()
