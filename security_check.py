# security_check.py - Basic security validation
import os
import subprocess
import sys
from scraper import validate_url

def check_env_security():
    """Check for hardcoded secrets"""
    if 'your_api_key_here' in os.getenv('SCRAPER_API_KEY', ''):
        print("⚠️  Using default API key - security risk!")
        return False
    return True

def check_url_validation():
    """Test URL validation function"""
    test_cases = ['http://evil.com/../../../etc/passwd', 'file:///etc/passwd']
    for url in test_cases:
        if validate_url(url):
            print(f"⚠️  URL validation bypass: {url}")
            return False
    return True


def run_dependency_scan() -> bool:
    """Run pip-audit to check for vulnerable dependencies."""
    try:
        result = subprocess.run(
            ["pip-audit", "-r", "requirements.txt"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("⚠️  pip-audit not installed. Skipping dependency scan.")
        return False
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        return False
    print(result.stdout)
    return True

if __name__ == "__main__":
    checks = [check_env_security(), check_url_validation(), run_dependency_scan()]
    if all(checks):
        print("✅ All security checks passed")
    else:
        sys.exit(1)
