#!/usr/bin/env python
"""Security report generator.

Generates HTML/JSON reports for all security tools.
"""

import subprocess
from datetime import datetime
from pathlib import Path


REPORT_DIR = Path("security_reports")


def ensure_report_dir():
    """Create report directory if not exists."""
    REPORT_DIR.mkdir(exist_ok=True)


def run_bandit():
    """Run Bandit and generate HTML report."""
    print("Running Bandit...")
    output_file = REPORT_DIR / "bandit_report.html"
    subprocess.run(
        f"bandit -r support_board config --skip B101 -x tests,migrations,venv,.venv,node_modules -f html -o {output_file}",
        shell=True
    )
    if output_file.exists() and output_file.stat().st_size > 0:
        print(f"  -> {output_file}")
        return True
    return False


def run_pip_audit():
    """Run pip-audit and generate JSON report."""
    print("Running pip-audit...")
    output_file = REPORT_DIR / "pip_audit_report.json"
    subprocess.run(
        f"pip-audit -f json -o {output_file}",
        shell=True
    )
    if output_file.exists() and output_file.stat().st_size > 0:
        print(f"  -> {output_file}")
        return True
    return False


def run_safety():
    """Run Safety and generate JSON report."""
    print("Running Safety...")
    output_file = REPORT_DIR / "safety_report.json"
    with open(output_file, "w", encoding="utf-8") as f:
        subprocess.run(
            "safety check --json",
            shell=True,
            stdout=f
        )
    if output_file.exists() and output_file.stat().st_size > 0:
        print(f"  -> {output_file}")
        return True
    return False


def run_flake8():
    """Run Flake8 and generate text report."""
    print("Running Flake8...")
    output_file = REPORT_DIR / "flake8_report.txt"
    subprocess.run(
        f"flake8 support_board config --output-file={output_file}",
        shell=True
    )
    print(f"  -> {output_file}")
    return True


def run_detect_secrets():
    """Run detect-secrets and generate JSON report."""
    print("Running detect-secrets...")
    output_file = REPORT_DIR / "secrets_report.json"
    with open(output_file, "w", encoding="utf-8") as f:
        subprocess.run(
            "detect-secrets scan --all-files --exclude-files \"\\.env.*\" --exclude-files \"node_modules/.*\" --exclude-files \"staticfiles/.*\"",
            shell=True,
            stdout=f
        )
    if output_file.exists() and output_file.stat().st_size > 0:
        print(f"  -> {output_file}")
        return True
    return False


def generate_summary_html():
    """Generate summary HTML report."""
    print("Generating summary report...")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Security Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .report-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .report-section h2 {{ margin-top: 0; color: #555; }}
        a {{ color: #0066cc; }}
        .timestamp {{ color: #888; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>Security Report</h1>
    <p class="timestamp">Generated: {timestamp}</p>

    <div class="report-section">
        <h2>Bandit (Security Vulnerability Scan)</h2>
        <p><a href="bandit_report.html">View Bandit Report (HTML)</a></p>
    </div>

    <div class="report-section">
        <h2>pip-audit (Dependency Vulnerabilities)</h2>
        <p><a href="pip_audit_report.json">View pip-audit Report (JSON)</a></p>
    </div>

    <div class="report-section">
        <h2>Safety (Dependency Vulnerabilities)</h2>
        <p><a href="safety_report.json">View Safety Report (JSON)</a></p>
    </div>

    <div class="report-section">
        <h2>Flake8 (Code Quality)</h2>
        <p><a href="flake8_report.txt">View Flake8 Report (TXT)</a></p>
    </div>

    <div class="report-section">
        <h2>detect-secrets (Secret Detection)</h2>
        <p><a href="secrets_report.json">View detect-secrets Report (JSON)</a></p>
    </div>
</body>
</html>
"""

    output_file = REPORT_DIR / "index.html"
    output_file.write_text(html_content, encoding="utf-8")
    print(f"  -> {output_file}")


def main():
    """Main function."""
    print("=" * 50)
    print("Security Report Generator")
    print("=" * 50)

    ensure_report_dir()

    run_bandit()
    run_pip_audit()
    run_safety()
    run_flake8()
    run_detect_secrets()
    generate_summary_html()

    print("=" * 50)
    print(f"Reports saved to: {REPORT_DIR.absolute()}")
    print(f"Open {REPORT_DIR / 'index.html'} in browser")
    print("=" * 50)


if __name__ == "__main__":
    main()
