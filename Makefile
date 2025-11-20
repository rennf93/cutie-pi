# Lint code
.PHONY: lint
lint:
	@ruff format . ; ruff check . ; mypy .
	@find . | grep -E "(__pycache__|\\.pyc|\\.pyo\\.pytest_cache|\\.ruff_cache|\\.mypy_cache)" | xargs rm -rf

# Fix
.PHONY: fix
fix:
	@ruff check --fix
	@find . | grep -E "(__pycache__|\\.pyc|\\.pyo\\.pytest_cache|\\.ruff_cache|\\.mypy_cache)" | xargs rm -rf

# Find dead code with Vulture
.PHONY: vulture
vulture:
	@echo "Finding dead code with Vulture..."
	@echo ''
	@vulture . vulture_whitelist.py --exclude .venv --min-confidence 100
	@find . | grep -E "(__pycache__|\\.pyc|\\.pyo|\\.pytest_cache|\\.ruff_cache|\\.mypy_cache)" | xargs rm -rf

# Security scan with Bandit
.PHONY: bandit
bandit:
	@echo "Running Bandit security scan..."
	@echo ''
	@bandit -r . -ll --exclude "./.venv,./vulture_whitelist.py,./.claude" -s B101,B601
	@find . | grep -E "(__pycache__|\\.pyc|\\.pyo|\\.pytest_cache|\\.ruff_cache|\\.mypy_cache)" | xargs rm -rf

# Check dependencies with Safety
.PHONY: safety
safety:
	@echo "Checking dependencies with Safety..."
	@echo ''
	@safety scan
	@find . | grep -E "(__pycache__|\\.pyc|\\.pyo|\\.pytest_cache|\\.ruff_cache|\\.mypy_cache)" | xargs rm -rf

# Audit dependencies with pip-audit
.PHONY: pip-audit
pip-audit:
	@echo "Auditing dependencies with pip-audit..."
	@echo ''
	@pip-audit
	@find . | grep -E "(__pycache__|\\.pyc|\\.pyo|\\.pytest_cache|\\.ruff_cache|\\.mypy_cache)" | xargs rm -rf

# Analyze code complexity with Radon
.PHONY: radon
radon:
	@echo "Analyzing code complexity with Radon..."
	@echo ''
	@echo "Cyclomatic Complexity:"
	@radon cc . -nc --exclude ".venv/*,vulture_whitelist.py"
	@echo ''
	@echo "Maintainability Index:"
	@radon mi . -nc --exclude ".venv/*,vulture_whitelist.py"
	@echo ''
	@echo "Raw Metrics:"
	@radon raw . --exclude ".venv/*,vulture_whitelist.py"
	@find . | grep -E "(__pycache__|\\.pyc|\\.pyo|\\.pytest_cache|\\.ruff_cache|\\.mypy_cache)" | xargs rm -rf

# Check complexity thresholds with Xenon
.PHONY: xenon
xenon:
	@echo "Checking complexity thresholds with Xenon..."
	@echo ''
	@xenon . --max-absolute B --max-modules A --max-average A --exclude ".venv/*,vulture_whitelist.py"
	@find . | grep -E "(__pycache__|\\.pyc|\\.pyo|\\.pytest_cache|\\.ruff_cache|\\.mypy_cache)" | xargs rm -rf

# Analyze dependencies with Deptry
.PHONY: deptry
deptry:
	@echo "Analyzing dependencies with Deptry..."
	@echo ''
	@deptry .
	@find . | grep -E "(__pycache__|\\.pyc|\\.pyo|\\.pytest_cache|\\.ruff_cache|\\.mypy_cache)" | xargs rm -rf

# Static analysis with Semgrep
.PHONY: semgrep
semgrep:
	@echo "Running Semgrep static analysis..."
	@echo ''
	@semgrep --config=auto .
	@find . | grep -E "(__pycache__|\\.pyc|\\.pyo|\\.pytest_cache|\\.ruff_cache|\\.mypy_cache)" | xargs rm -rf

# Run all security checks
.PHONY: security
security: bandit safety pip-audit
	@echo "All security checks completed."

# Run all code quality checks
.PHONY: quality
quality: lint vulture radon xenon
	@echo "All code quality checks completed."

# Run all analysis tools
.PHONY: analysis
analysis: deptry semgrep
	@echo "All analysis tools completed."

# Run all checks (linting, security, quality, and analysis)
.PHONY: check-all
check-all: lint security quality analysis
	@echo "All checks completed."

# Clean
.PHONY: clean
clean:
	@find . | grep -E "(__pycache__|\\.pyc|\\.pyo\\.pytest_cache|\\.ruff_cache|\\.mypy_cache)" | xargs rm -rf

# Help
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make lint             - Run linting checks (ruff & mypy)"
	@echo "  make fix              - Auto-fix linting issues"
	@echo "  make vulture          - Find dead code with Vulture"
	@echo "  make bandit           - Run Bandit security scan"
	@echo "  make safety           - Check dependencies with Safety"
	@echo "  make pip-audit        - Audit dependencies with pip-audit"
	@echo "  make radon            - Analyze code complexity with Radon"
	@echo "  make xenon            - Check complexity thresholds with Xenon"
	@echo "  make deptry           - Analyze dependencies with Deptry"
	@echo "  make semgrep          - Run Semgrep static analysis"
	@echo "  make security         - Run all security checks"
	@echo "  make quality          - Run all code quality checks"
	@echo "  make analysis         - Run all analysis tools"
	@echo "  make check-all        - Run all checks (lint, security, quality, analysis)"
	@echo "  make clean            - Remove Python cache files"
	@echo "  make help             - Show this help message"
