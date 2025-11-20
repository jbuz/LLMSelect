# CI/CD Workflows

This document describes the streamlined CI/CD workflows for the LLMSelect project.

## Workflow Overview

The project uses 3 GitHub Actions workflows:

### 1. CI (`ci.yml`)
**Runs on:** Pull requests and pushes to main

**Purpose:** Core continuous integration checks

**Jobs:**
- **Lint Python** - Runs flake8 and black on Python code
- **Lint JavaScript** - Runs ESLint on JavaScript code
- **Test Python** - Runs pytest on Python 3.9, 3.10, 3.11 with coverage
- **Test JavaScript** - Runs npm test
- **Build** - Builds frontend with webpack
- **Docker Build** - Builds and tests Docker image (push to main only)
- **CI Summary** - Aggregates results and fails if core checks fail

**Duration:** ~2-3 minutes per run

### 2. Security (`security.yml`)
**Runs on:** Pull requests, pushes to main, daily at 2 AM UTC, manual trigger

**Purpose:** Comprehensive security scanning

**Jobs:**
- **Secret Scanning (Gitleaks)** - Scans for hardcoded secrets and credentials
- **CodeQL Analysis** - Static analysis for Python and JavaScript security vulnerabilities
- **Dependency Review** - Reviews dependency changes in PRs for vulnerabilities and licenses
- **Dependency Audit** - Audits Python (Safety) and Node (npm audit) dependencies
- **SBOM Generation** - Generates Software Bill of Materials (main branch only)
- **Container Scan** - Scans Docker image with Trivy for vulnerabilities
- **Security Summary** - Aggregates security scan results

**Duration:** ~5-7 minutes per run

### 3. Copilot Agent Notification (`copilot-agent-notify.yml`)
**Runs on:** PR opened/closed

**Purpose:** Sends Pushover notifications when Copilot agent completes work

**Jobs:**
- **Notify Pushover** - Sends notification with PR details

## Workflow Consolidation

Previously, the project had 5 separate workflow files with overlapping functionality:
- `ci.yml`
- `security-scan.yml` (removed)
- `gitleaks.yml` (removed)
- `dependency-review.yml` (removed)
- `copilot-agent-notify.yml`

### Changes Made:
1. **Merged security workflows** - Combined `security-scan.yml`, `gitleaks.yml`, and `dependency-review.yml` into a single `security.yml`
2. **Removed redundancy** - Eliminated duplicate secret scanning (kept Gitleaks, removed TruffleHog)
3. **Consolidated dependency checks** - Merged dependency review and audit into single workflow
4. **Simplified structure** - Reduced from 5 to 3 workflows for easier maintenance

### Benefits:
- ✅ **Clearer organization** - Each workflow has a distinct purpose
- ✅ **Faster feedback** - No duplicate checks running
- ✅ **Easier maintenance** - Fewer files to update
- ✅ **Better visibility** - Single security workflow shows all security checks together

## Running Workflows Locally

### Lint
```bash
./scripts/lint.sh
```

### Test
```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}"
pytest tests/ -v --cov=llmselect
```

### Build
```bash
npm install
npm run build
```

### Docker
```bash
docker build -t llmselect:local .
docker run --rm -p 3044:3044 \
  -e SECRET_KEY=test-key \
  -e JWT_SECRET_KEY=test-jwt \
  -e ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())") \
  llmselect:local
```

## Workflow Triggers

### CI Workflow
- **Pull Request**: Runs on all PRs to `main`
- **Push**: Runs on direct pushes to `main`

### Security Workflow
- **Pull Request**: Runs on all PRs to `main`
- **Push**: Runs on direct pushes to `main`
- **Schedule**: Daily at 2 AM UTC to catch new vulnerabilities
- **Manual**: Can be triggered manually via GitHub Actions UI

### Copilot Agent Notification
- **Pull Request**: Runs when PRs are opened or closed (if from Copilot)

## Troubleshooting

### CI Failures
1. Check which job failed in the CI Summary
2. Click on the failed job to see detailed logs
3. Run the same commands locally to reproduce
4. Fix the issue and push again

### Security Failures
1. Review the Security Summary for which scan failed
2. For secret leaks: Remove secrets and rotate credentials
3. For vulnerabilities: Update affected dependencies
4. For license issues: Replace or get approval for flagged dependencies

### Build Failures
1. Ensure all dependencies are installed: `npm install` and `pip install -r requirements.txt`
2. Check for syntax errors in code
3. Verify webpack.config.js is correct
4. Check that all required environment variables are set

## Best Practices

1. **Fix CI failures quickly** - Don't merge PRs with failing CI
2. **Review security alerts** - Don't ignore security warnings
3. **Keep dependencies updated** - Regularly update to patch vulnerabilities
4. **Test locally first** - Run lint and tests before pushing
5. **Use meaningful commit messages** - Helps track changes in CI logs

## Future Improvements

Potential enhancements to consider:
- Add deployment workflow for staging/production
- Add performance testing job
- Add visual regression testing
- Add automatic PR labeling based on changed files
- Add automatic changelog generation
