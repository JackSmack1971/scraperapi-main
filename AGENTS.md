# AGENTS.md: AI Collaboration Guide
<!-- This document provides essential context for AI models interacting with this project. Adhering to these guidelines will ensure consistency, maintain code quality, and optimize agent performance. -->

<!-- It is Friday, August 15, 2025. This guide is optimized for clarity, efficiency, and maximum utility for modern AI coding agents like OpenAI's Codex, GitHub Copilot Workspace, and Claude. -->

<!-- This file should be placed at the root of your repository. More deeply-nested AGENTS.md files (e.g., in subdirectories) will take precedence for specific sub-areas of the codebase. Direct user prompts will always override instructions in this file. -->

## 1. Project Overview & Purpose
<!-- OBJECTIVE: Help the AI quickly grasp the project's domain, main goal, and high-level functionality. This sets the foundational context. -->

*   **Primary Goal:** A cross-platform web scraping application with GUI interface for extracting and saving web content in multiple formats (TXT, Markdown).
*   **Business Domain:** Web Scraping, Data Extraction, Content Management, Cross-Platform Desktop Applications.
*   **Key Features:** Concurrent multi-threaded URL processing, cross-platform GUI (Windows/macOS/Linux/Android), ScraperAPI integration, multiple output formats, comprehensive error handling with retry logic, real-time progress tracking.

## 2. Core Technologies & Stack
<!-- OBJECTIVE: Inform the AI about the main programming languages, frameworks, runtimes, and key dependencies used. This helps the AI generate compatible code. -->

*   **Languages:** Python 3.7+ (primary language for all components).
*   **Frameworks & Runtimes:** Kivy 2.0.0 (cross-platform GUI framework), Python standard library threading, concurrent.futures for parallel processing.
*   **Databases:** None - file-based output storage with platform-specific directory structures.
*   **Key Libraries/Dependencies:** 
    *   `kivy==2.0.0` - Cross-platform GUI framework
    *   `requests==2.25.1` - HTTP client with retry logic and session management
    *   `beautifulsoup4==4.9.3` - HTML parsing and content extraction
    *   `python-dotenv` (implied) - Environment variable management
*   **Package Manager:** pip (with requirements.txt for dependency management).
*   **Platforms:** Windows, macOS, Linux, Android (via Kivy's cross-platform capabilities).

## 3. Architectural Patterns & Structure
<!-- OBJECTIVE: Guide the AI on the project's high-level architecture, module organization, and file hierarchy to ensure new code aligns with existing patterns. -->

*   **Overall Architecture:** Layered desktop application with GUI frontend, concurrent processing engine, and cross-platform utility layer. Uses threading for non-blocking UI and parallel scraping operations.
*   **Directory Structure Philosophy:** 
    *   `/` (root): Contains all primary source code files and configuration.
    *   No separate `/src` directory - main modules are at root level.
    *   No `/tests` directory present (testing framework not implemented).
    *   Platform-specific output directories managed dynamically by utils.py.
*   **Module Organization:** 
    *   **main.py**: Application entry point and Kivy configuration
    *   **ui.py**: GUI components, user interactions, and thread management  
    *   **scraper.py**: Core scraping logic, concurrent processing, and content extraction
    *   **utils.py**: Cross-platform utilities, logging, and file management
*   **Common Patterns & Idioms:**
    *   **Concurrency**: ThreadPoolExecutor for parallel URL processing, @mainthread decorator for thread-safe GUI updates
    *   **Error Handling**: Comprehensive try/catch blocks with specific exception types, exponential backoff retry logic
    *   **Cross-Platform**: Platform detection and OS-specific path resolution
    *   **Security**: Environment variable-based configuration, URL validation, input sanitization

## 4. Coding Conventions & Style Guide
<!-- OBJECTIVE: Ensure AI-generated code adheres to the project's specific style, formatting, and best practices, reducing the need for manual review and refactoring. -->

*   **Formatting:** Python PEP 8 style conventions. Use 4-space indentation, 100-character line limit (inferred from existing code structure).
*   **Naming Conventions:**
    *   Variables, functions: `snake_case` (e.g., `get_default_output_directory`, `scrape_text_data`)
    *   Classes: `PascalCase` (e.g., `ScraperApp`, `HTTPAdapter`)  
    *   Constants: `SCREAMING_SNAKE_CASE` (e.g., `USER_AGENTS`, `SCRAPERAPI_URL`)
    *   Files: `snake_case` (e.g., `scraper.py`, `utils.py`)
*   **API Design Principles:** 
    *   **Object-Oriented/Procedural Hybrid**: Classes for stateful components (GUI), functions for stateless operations (scraping, utilities)
    *   **Error Transparency**: Functions return None or raise exceptions rather than silently failing
    *   **Platform Abstraction**: Cross-platform functionality handled in utils.py
*   **Documentation Style:** Comprehensive docstrings for all public functions and classes explaining purpose, parameters, return values, and exceptions.
*   **Error Handling:** 
    *   Uses Python's exception system with specific exception types (`RequestException`, `HTTPError`, `Timeout`)
    *   Comprehensive logging at multiple levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    *   Retry logic with exponential backoff for network operations
    *   Input validation before processing (URL validation, file path validation)
*   **Forbidden Patterns:** 
    *   **NEVER** hardcode API keys, secrets, or sensitive configuration - use environment variables
    *   **NEVER** skip URL validation before processing
    *   **NEVER** update GUI from background threads without @mainthread decorator
    *   **NEVER** ignore exceptions without proper logging

## 5. Development & Testing Workflow
<!-- OBJECTIVE: Provide the AI with clear instructions on how to set up the environment, run builds, and execute tests. This is critical for verifiable code generation. -->

*   **Local Development Setup:**
    *   **Python Environment Setup**:
        1. Install Python 3.7+ 
        2. Create virtual environment: `python -m venv venv`
        3. Activate environment: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
        4. Install dependencies: `pip install -r requirements.txt`
    *   **Environment Configuration**:
        1. Create `.env` file in project root
        2. Add required variables: `SCRAPER_API_KEY=your_api_key_here`
        3. Optional Kivy settings: `KIVY_FULLSCREEN=auto`, `KIVY_WIDTH=800`, `KIVY_HEIGHT=600`
*   **Build Commands:** No explicit build step required - Python application runs directly.
*   **Testing Commands:** **No testing framework currently implemented.** This is a critical gap that should be addressed.
    *   Recommended: Add pytest for unit testing
    *   Test files should follow `test_*.py` naming convention
    *   **MUST** mock external API calls (ScraperAPI) in tests to avoid network dependencies
*   **Linting/Formatting Commands:** **No automated linting configured.** Recommended additions:
    *   `flake8` for linting: `flake8 *.py`
    *   `black` for formatting: `black *.py`
    *   **All code MUST pass lint checks before committing.**
*   **CI/CD Process Overview:** **No CI/CD pipeline currently implemented.** Manual testing and deployment process.

## 6. Git Workflow & PR Instructions
<!-- OBJECTIVE: Guide the AI on how to interact with Git and create pull requests that align with team standards. This ensures smooth integration into development pipelines. -->

*   **Pre-Commit Checks:** **Currently no automated pre-commit checks.** Recommended to add:
    *   Run linting and formatting checks
    *   Validate that application starts without errors
    *   Check for hardcoded secrets or API keys
*   **Branching Strategy:** **(Inferred from single-contributor project)** Work on feature branches and create pull requests.
*   **Commit Messages:** **(Confidence: Low - no commit history provided)** Recommended to follow Conventional Commits format:
    *   `feat: add new scraping feature`
    *   `fix: resolve GUI threading issue`
    *   `docs: update README with setup instructions`
*   **Pull Request (PR) Process:** 
    *   Ensure code follows existing style conventions
    *   Add comprehensive error handling and logging for new features
    *   Test cross-platform compatibility where applicable
*   **Force Pushes:** **NEVER** use `git push --force` on main/master branch.
*   **Clean State:** **You MUST leave your worktree in a clean state after completing a task.**

## 7. Security Considerations
<!-- OBJECTIVE: Embed security best practices directly into the AI's coding process, reducing vulnerabilities in generated code. -->

*   **General Security Practices:** **Be highly security-conscious** when handling network requests, file I/O, and user inputs.
*   **Sensitive Data Handling:** **DO NOT** hardcode API keys, secrets, or credentials. **ALWAYS** use environment variables loaded via `os.getenv()` or `python-dotenv`.
*   **Input Validation:** **ALWAYS** validate URLs using the existing `validate_url()` function before processing. Sanitize file paths and user inputs.
*   **Vulnerability Avoidance:** 
    *   Prevent path traversal attacks in file operations
    *   Avoid code injection through URL or user input processing
    *   Use session-based requests with proper timeout and retry configuration
*   **Dependency Management:** Keep dependencies updated and monitor for security vulnerabilities.
*   **Principle of Least Privilege:** File operations should use minimal required permissions, create directories with appropriate access controls.

## 8. Specific Agent Instructions & Known Issues
<!-- OBJECTIVE: Provide meta-instructions about agent behavior, specific tool usage, and any known project quirks or challenges the AI should be aware of. -->

*   **Tool Usage:**
    *   **For Python dependencies:** Use `pip install <package>` and update `requirements.txt`
    *   **For environment variables:** Always use `os.getenv()` with appropriate defaults or error handling
    *   **For cross-platform paths:** Use `utils.py` functions for platform-specific directory handling
*   **Context Management:** 
    *   This is a relatively small codebase that can be understood holistically
    *   Focus on maintaining consistency across the four main modules
    *   When adding features, consider impact on all platforms (Windows/macOS/Linux/Android)
*   **Quality Assurance & Verification:** 
    *   **After making changes, ALWAYS verify the application starts without errors**
    *   **Test GUI responsiveness and thread safety for any UI-related changes**
    *   **Validate that scraping operations work with sample URLs**
    *   **Check cross-platform compatibility for path and directory operations**
*   **Project-Specific Quirks/Antipatterns:**
    *   **Threading**: GUI updates MUST use `@mainthread` decorator from Kivy
    *   **Platform Detection**: Use existing platform detection logic in `ui.py:17-32` rather than reimplementing
    *   **Logging**: Use the configured logger from `utils.get_logger()` rather than print statements
    *   **ScraperAPI Integration**: Respect rate limits and use provided retry logic rather than implementing custom solutions
*   **Troubleshooting & Debugging:** 
    *   **GUI Issues**: Check Kivy logs and ensure proper thread usage
    *   **Scraping Failures**: Verify API key configuration and check network connectivity
    *   **Cross-Platform Issues**: Test path resolution and directory creation on target platforms
    *   **If errors occur, provide full stack traces and relevant log output for debugging**
*   **Missing Infrastructure (High Priority):**
    *   **Testing Framework**: No unit tests present - this is a critical gap
    *   **CI/CD Pipeline**: No automation for testing, linting, or deployment
    *   **Dependency Locking**: Consider adding `requirements-lock.txt` or using `pip-tools`
    *   **Code Quality Tools**: No linting, formatting, or static analysis configured

## 9. Known Limitations & Future Improvements
<!-- Additional section for project-specific context -->

*   **Current Limitations:**
    *   No automated testing infrastructure
    *   No code quality enforcement (linting/formatting)
    *   ScraperAPI dependency creates vendor lock-in
    *   Limited error recovery for GUI state management
*   **Recommended Improvements:**
    *   Add comprehensive test suite with pytest
    *   Implement CI/CD pipeline for automated quality checks
    *   Add configuration management for scraping parameters (concurrent workers, timeouts)
    *   Consider plugin architecture for supporting additional content extraction methods
