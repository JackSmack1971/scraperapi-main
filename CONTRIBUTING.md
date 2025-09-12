# Contributing to Web Scraper Pro

Thanks for helping build Web Scraper Pro! This guide gets you to your **first PR in ~15 minutes**.

## 1) Quick Start (TL;DR)
- Pick an issue labeled `good first issue`, `help wanted`, or `enhancement`.
- Fork → create a branch: `git checkout -b feat/SHORT-DESCRIPTION`
- Setup & run:
  ```bash
  # Prerequisites: Python 3.7+, ScraperAPI account
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  pip install -r requirements.txt
  
  # Create .env file with your API key
  echo "SCRAPER_API_KEY=your_api_key_here" > .env
  
  # Test the application
  python main.py
  ```
- Commit using **Conventional Commits**:
  ```
  feat(scraper): add retry logic for failed requests
  fix(ui): resolve thread safety issue in progress updates
  docs(readme): update installation instructions
  ```
- Push and open a PR using the template.

## 2) What to Work On

**High Priority (Infrastructure Gaps):**
- 🧪 **Add Testing Framework** - Set up pytest with mocked ScraperAPI calls
- 🔧 **CI/CD Pipeline** - GitHub Actions for automated testing and linting
- 📋 **Code Quality Tools** - Add flake8, black, and pre-commit hooks
- 📁 **Dependency Management** - Add requirements-lock.txt or pip-tools

**Feature Development:**
- Issues labeled `good first issue`, `enhancement`, `bug`, `platform-specific`
- Cross-platform compatibility improvements
- New content extraction methods
- Performance optimizations

**Check the [Issues](../../issues) tab for current opportunities.**

## 3) Development Environment

### Prerequisites
- **Python 3.7+** (tested on 3.7-3.11)
- **ScraperAPI account** with API key
- **Platform-specific:** For Android development, see Kivy's buildozer documentation

### Setup Commands
```bash
# 1. Clone and create virtual environment
git clone https://github.com/YOUR_ORG/web-scraper-pro.git
cd web-scraper-pro
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Environment configuration
cp .env.example .env  # Create from template
# Edit .env and add your SCRAPER_API_KEY

# 4. Verify installation
python main.py
```

### Development Commands
```bash
# Run application
python main.py

# Run with debug logging
export SCRAPER_LOG_LEVEL=DEBUG  # Windows: set SCRAPER_LOG_LEVEL=DEBUG
python main.py

# Test scraping functionality (manual testing currently)
python -c "from scraper import scrape_text_data; print(scrape_text_data('https://example.com'))"
```

## 4) Code Quality & Style

### Current State
**⚠️ Note:** We're currently building our automated quality infrastructure. Your contributions to improve this are highly valued!

### Code Style
- **Python:** Follow PEP 8 conventions
- **Line length:** 100 characters (inferred from existing code)
- **Indentation:** 4 spaces
- **Naming:**
  - Variables/functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `SCREAMING_SNAKE_CASE`

### Required Practices
- **Error Handling:** Use comprehensive try/catch blocks with specific exception types
- **Logging:** Use `utils.get_logger(__name__)` instead of print statements
- **Thread Safety:** GUI updates MUST use `@mainthread` decorator
- **Security:** Never hardcode API keys - use environment variables
- **Cross-Platform:** Use utilities from `utils.py` for platform-specific operations

### Documentation
- Add docstrings for all public functions and classes
- Include parameter types, return values, and raised exceptions
- Update README.md for user-facing changes
- Follow existing documentation patterns

## 5) Commits & Branching

### Commit Messages (Required)
We use **Conventional Commits** for clear history and automated changelog generation:

```
type(scope): description

feat(scraper): add concurrent URL processing
fix(ui): resolve progress bar threading issue
docs(readme): update installation instructions
refactor(utils): improve cross-platform path handling
test(scraper): add unit tests for URL validation
chore(deps): update requests to 2.28.1
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
**Scopes:** `scraper`, `ui`, `utils`, `main`, `docs`

### Branching Strategy
- Create descriptive branches: `feat/concurrent-scraping`, `fix/gui-threading`, `docs/api-setup`
- Keep branches focused and small
- Rebase before submitting PR to maintain clean history

## 6) Pull Request Process

### Before Submitting
- [ ] Code follows existing style and patterns
- [ ] All GUI updates use `@mainthread` decorator
- [ ] Environment variables used for sensitive data
- [ ] Cross-platform compatibility considered
- [ ] Documentation updated for user-facing changes
- [ ] Application starts and runs without errors
- [ ] No hardcoded secrets or API keys

### PR Template Checklist
When you submit a PR, please:
- Fill out the entire PR template
- Include screenshots for UI changes
- Provide test cases or manual testing steps
- Link related issues
- Describe platform-specific considerations

### Review Process
- **Reviewers:** 1-2 maintainer approvals required
- **Automated Checks:** Currently manual (help us add CI/CD!)
- **Testing:** Manual testing required until automated tests are implemented

## 7) Issue Reporting

### Bug Reports
Please include:
- **Steps to reproduce** with exact commands/clicks
- **Expected behavior** vs **actual behavior**
- **Environment:** OS, Python version, dependency versions
- **Logs:** Enable debug logging with `SCRAPER_LOG_LEVEL=DEBUG`
- **Screenshots** for UI issues
- **Sample URLs** that demonstrate the issue (if applicable)

### Feature Requests
- Describe the problem you're trying to solve
- Propose a solution with examples
- Consider cross-platform implications
- Check if similar functionality exists

## 8) Security Policy

🔒 **For security vulnerabilities, DO NOT open public issues.**

**Private Reporting:**
- Email: [SECURITY_EMAIL]
- GitHub: Use "Security" tab → "Report a vulnerability"

See [`SECURITY.md`](./SECURITY.md) for our full security policy and response timeline.

**Security Best Practices:**
- Never commit API keys, tokens, or credentials
- Use environment variables for sensitive configuration
- Validate all user inputs (URLs, file paths)
- Follow principle of least privilege for file operations

## 9) Code of Conduct

We follow the [Contributor Covenant](CODE_OF_CONDUCT.md). 

**TL;DR:** Be kind, inclusive, and professional. Harassment and discrimination are not tolerated.

## 10) License & Legal

- **License:** MIT License (see [LICENSE](LICENSE))
- **Contributor Agreement:** By submitting a PR, you agree that your contributions will be licensed under the MIT License
- **Copyright:** Contributions become part of the project under existing copyright

**No CLA or DCO required** - but we may add DCO in the future for larger contributions.

## 11) Development Priorities & Roadmap

### Immediate Infrastructure Needs (Great for Contributors!)
1. **Testing Framework** (High Impact)
   - Set up pytest with fixtures for ScraperAPI mocking
   - Add unit tests for `scraper.py`, `utils.py` functions
   - Integration tests for GUI components

2. **Code Quality Automation** (Medium Impact)
   - Pre-commit hooks with flake8, black, isort
   - GitHub Actions CI/CD pipeline
   - Dependency vulnerability scanning

3. **Documentation** (Medium Impact)
   - API documentation for scraper functions
   - Developer setup videos/screenshots
   - Troubleshooting guide

### Feature Development
- **Plugin Architecture:** Support for custom content extractors
- **Batch Processing:** Queue management for large URL sets
- **Export Options:** JSON, CSV, XML output formats
- **Configuration GUI:** Settings panel for scraping parameters

## 12) Getting Help

- **Questions:** Open a [Discussion](../../discussions) or issue with `question` label
- **Real-time:** Join our community chat [CHAT_LINK]
- **Documentation:** Check the [Wiki](../../wiki) for detailed guides

## 13) Recognition

We appreciate all contributions! Contributors are recognized in:
- README.md contributors section
- Release notes for significant features
- Annual contributor appreciation posts

---

### Quick Reference Links
- **Setup:** See section 3 above
- **Code Style:** PEP 8, docstrings required, cross-platform considerations
- **Commit Format:** Conventional Commits with type(scope): description
- **Security:** Private disclosure via Security tab
- **License:** MIT - contributions welcome

**Need help?** Open an issue with the `question` label or start a discussion!

---

*Maintainers: [@JackSmack1971](https://github.com/JackSmack1971)*

*This guide is living documentation - help us improve it!*
