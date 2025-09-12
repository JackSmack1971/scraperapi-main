# security_check.py - Basic security validation
import os
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

if __name__ == "__main__":
    if check_env_security() and check_url_validation():
        print("✅ Basic security checks passed")
    else:
        sys.exit(1)
