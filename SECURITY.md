# Security Policy

## Report a Vulnerability

**🔒 For security vulnerabilities, please DO NOT open public issues.**

### Preferred Reporting Methods

- **GitHub (Recommended):** Use GitHub's private vulnerability reporting via the **Security** tab → **"Report a vulnerability"**
- **Email:** security@artofficial-intelligence.com
- **Encryption:** PGP key provided below for sensitive reports

### Response Timeline

- **Initial acknowledgment:** Within 2 business days
- **Status updates:** Weekly until resolution
- **Coordinated disclosure:** Typically 45-90 days from initial report

## Security Scope & Testing Guidelines

### In Scope

✅ **Application Components:**
- Core scraping engine (`scraper.py`)
- GUI application (`ui.py`, `main.py`) 
- Cross-platform utilities (`utils.py`)
- Configuration and environment handling
- File system operations and output handling
- Network request handling and API integrations

✅ **Vulnerability Types:**
- Code execution vulnerabilities
- Authentication/authorization bypasses
- API key exposure or mishandling
- Path traversal attacks
- Input validation failures
- Cross-platform security issues
- Dependency vulnerabilities in `requirements.txt`
- Memory corruption or resource exhaustion

### Out of Scope

❌ **Excluded from Bounty/VDP:**
- Denial of Service attacks against external services
- Social engineering attacks
- Physical device access scenarios
- Issues requiring root/admin privileges unrelated to the application
- Third-party service vulnerabilities (ScraperAPI, external websites)
- Browser-based attacks (this is a desktop application)
- Issues in unmaintained dependencies (report to upstream)

### Safe Testing Guidelines

- **Rate limiting:** Please be respectful of ScraperAPI quotas during testing
- **File system:** Test only in isolated directories, avoid system-critical paths
- **Network:** Do not test against sites without permission
- **Data:** Do not attempt to access, modify, or exfiltrate user data
- **Automation:** Limit automated scanning; provide proof-of-concept over volume

## Supported Versions & Security Updates

We provide security updates for the following versions:

| Version | Status | Security Support |
|---------|--------|------------------|
| 1.x.x (current) | ✅ Supported | Full security patches |
| Pre-release | ⚠️ Development | Critical fixes only |
| Dependencies | 📋 Tracked | Regular updates via Dependabot |

**Note:** This project is actively maintained. All security patches are applied to the main branch and released as point updates.

## Vulnerability Assessment

### Severity Classification

We use **CVSS v4.0** for vulnerability scoring: [CVSS Calculator](https://www.first.org/cvss/calculator/4.0)

**Priority Matrix:**
- **Critical (9.0-10.0):** Immediate hotfix within 1-7 days
- **High (7.0-8.9):** Patch within 14 days  
- **Medium (4.0-6.9):** Regular release cycle (30-60 days)
- **Low (0.1-3.9):** Next minor version or documentation update

### Common Attack Vectors for This Project

🎯 **High-risk areas to focus testing:**
- Environment variable handling (`SCRAPER_API_KEY` exposure)
- URL validation and request handling (`validate_url()` function)
- File path construction and directory traversal prevention
- Thread safety in GUI operations (`@mainthread` usage)
- Input sanitization for user-provided URLs
- Cross-platform path handling vulnerabilities
- Logging sensitive information exposure

## Encryption & Secure Communication

### PGP Public Key for Encrypted Reports

```
-----BEGIN PGP PUBLIC KEY BLOCK-----

[Key ID: 0x1234567890ABCDEF]
[Fingerprint: 1234 5678 90AB CDEF 1234 5678 90AB CDEF 1234 5678]

mQENBGXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
[Your actual PGP public key block would go here]
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
=XXXX
-----END PGP PUBLIC KEY BLOCK-----
```

**Key Details:**
- **Algorithm:** RSA-4096/ECC-P384 
- **Valid until:** [Expiration Date]
- **Verification:** Available on keyserver.ubuntu.com and keys.openpgp.org

### Languages Supported
- **Primary:** English
- **Also accepted:** Spanish, French (may require additional response time)

## Our Security Process

### 1. Report Intake & Validation
- Automated acknowledgment of receipt
- Security team review within 2 business days
- Request for additional details or proof-of-concept if needed
- Classification and severity scoring (CVSS v4.0)

### 2. Investigation & Reproduction
- Technical analysis by maintainers
- Environment setup for reproduction
- Impact assessment across supported platforms
- Dependency chain analysis if applicable

### 3. Coordinated Disclosure Timeline
- **Day 0:** Report received and acknowledged
- **Days 1-7:** Initial triage and reproduction
- **Days 7-30:** Development of patches and testing
- **Days 30-45:** Coordination with reporter on disclosure timeline
- **Day 45+:** Public disclosure via GitHub Security Advisory (GHSA)

### 4. Publication & Credits
- **GitHub Security Advisory (GHSA)** creation with CVE assignment
- **OSV.dev integration** for ecosystem-wide visibility
- **Release notes** with security section
- **Credit acknowledgment** (with permission) on our security page

## Acknowledgments & Hall of Fame

We gratefully acknowledge security researchers who help keep our users safe. With your permission, we'll add you to our [Security Hall of Fame](https://github.com/JackSmack1971/web-scraper-pro/security/advisories).

### Recognition Includes:
- 🏆 Name and/or handle on our acknowledgments page
- 🔗 Link to your profile/blog (if desired) 
- 📧 LinkedIn recommendation for security research (upon request)
- 🎁 Project swag for significant findings

## Additional Resources

### Security Configuration
- **Environment Security:** [Setup Guide](README.md#security-considerations)
- **Cross-Platform Security:** [Platform-specific Notes](docs/cross-platform-security.md)
- **API Security:** [ScraperAPI Best Practices](docs/api-security.md)

### Vulnerability Disclosure Policy
This project follows **Coordinated Vulnerability Disclosure (CVD)** principles consistent with:
- [CVE Program](https://www.cve.org/)
- [CERT/CC Vulnerability Disclosure Policy](https://vuls.cert.org/confluence/display/CVD)
- [disclose.io Core Terms](https://disclose.io/dioterms/)

### Security.txt Location
A machine-readable version of this policy is available at:
`https://artofficial-intelligence.com/.well-known/security.txt`

## Legal Safe Harbor

We support security research conducted in good faith and provide safe harbor for:
- Vulnerability discovery and responsible disclosure
- Security research that follows our testing guidelines
- Reports that help improve our security posture

We will not pursue legal action against security researchers who:
- Make a good faith effort to avoid data destruction, privacy violations, and service disruption
- Only interact with accounts they own or with explicit permission
- Do not violate any applicable laws
- Follow this disclosure policy

## Questions?

For questions about this security policy or our disclosure process:
- 📧 **General inquiries:** security@artofficial-intelligence.com
- 💬 **Community discussions:** [GitHub Discussions](https://github.com/JackSmack1971/web-scraper-pro/discussions)
- 📚 **Documentation:** [Security Documentation](docs/security/)

---

**Last updated:** January 2025  
**Next review:** July 2025  

*This security policy is maintained by ARTOfficial Intelligence LLC and the Web Scraper Pro project maintainers.*
