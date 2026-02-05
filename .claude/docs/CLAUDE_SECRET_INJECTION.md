# Secret Injection Strategy - QuartzBio Python Client

This document outlines the secret management and injection strategies for the QuartzBio Python client library across different environments. This guide is essential for Claude Code to understand how to handle secrets when working with the codebase.

## Table of Contents
- [Overview](#overview)
- [Secret Categories](#secret-categories)
- [Environment-Specific Strategies](#environment-specific-strategies)
- [Secret Reference Guide](#secret-reference-guide)
- [Best Practices](#best-practices)
- [Claude Code Guidelines](#claude-code-guidelines)

---

## Overview

### Secret Management Architecture

The QuartzBio Python client uses a layered approach to secret management:

```
┌─────────────────────────────────────────────────────────────┐
│  PyPI Release: Twine configuration (~/.pypirc)               │
├─────────────────────────────────────────────────────────────┤
│  CI/CD: GitLab CI Variables (masked & protected)            │
├─────────────────────────────────────────────────────────────┤
│  Testing: Environment variables                              │
├─────────────────────────────────────────────────────────────┤
│  Development: Credentials file (~/.quartzbio/credentials)    │
└─────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Never commit secrets to version control**
2. **Use environment-specific secret stores**
3. **Pass secrets via environment variables for testing**
4. **Store user credentials in netrc-format file**
5. **Rotate tokens regularly**

---

## Secret Categories

### 1. API Access Tokens
- `QUARTZBIO_ACCESS_TOKEN` - Primary API authentication token
- `EDP_ACCESS_TOKEN` - Alternative token environment variable
- `SOLVEBIO_ACCESS_TOKEN` - Legacy token environment variable

### 2. API Host Configuration
- `QUARTZBIO_API_HOST` - API endpoint URL (e.g., https://api.quartzbio.com)

### 3. PyPI Publishing Credentials
- PyPI username and password (stored in ~/.pypirc)
- PyPI API token (preferred over password)

### 4. GitHub Access
- `GITHUB_TOKEN` - For changelog generation (github_changelog_generator)
- Personal access token for releases

### 5. CI/CD Secrets
- `QUARTZBIO_API_HOST` - Test environment API
- `QUARTZBIO_ACCESS_TOKEN` - Test account token
- `PYPI_TOKEN` - For automated releases

---

## Environment-Specific Strategies

### Local Development Environment

#### Method 1: Credentials File (Recommended for Users)

**File:** `~/.quartzbio/credentials` (netrc format)

```
machine api.quartzbio.com
login user@example.com
password your_access_token_here
```

**Setup:**
```bash
# Login via CLI (recommended)
quartzbio login
# Enter your credentials interactively

# Or manually create credentials file
mkdir -p ~/.quartzbio
cat > ~/.quartzbio/credentials <<EOF
machine api.quartzbio.com
login your-email@example.com
password your_token_here
EOF
chmod 600 ~/.quartzbio/credentials
```

**Credential Resolution Priority:**
1. Environment variables (highest)
2. Credentials file for specific API host
3. Error if not found

#### Method 2: Environment Variables (Recommended for Development)

**For bash/zsh** (`~/.bashrc` or `~/.zshrc`):
```bash
# API Configuration
export QUARTZBIO_API_HOST=https://api-dev.quartzbio.com
export QUARTZBIO_ACCESS_TOKEN=your_token_here

# Optional: Logging configuration
export QUARTZBIO_LOGLEVEL=DEBUG
export QUARTZBIO_LOGFILE=~/.quartzbio/debug.log
```

**For Windows PowerShell**:
```powershell
$env:QUARTZBIO_API_HOST="https://api-dev.quartzbio.com"
$env:QUARTZBIO_ACCESS_TOKEN="your_token_here"
```

**Usage:**
```bash
# Start a new shell or source the profile
source ~/.bashrc

# Verify
echo $QUARTZBIO_ACCESS_TOKEN  # Should show token

# Run CLI
quartzbio whoami

# Run tests
python setup.py test
```

#### Method 3: Per-Session Environment Variables

```bash
# Set for current session only
export QUARTZBIO_API_HOST=https://api-dev.quartzbio.com
export QUARTZBIO_ACCESS_TOKEN=your_token_here

# Run commands in same session
quartzbio whoami
python -m unittest quartzbio.test.test_dataset
```

---

### Testing Environment

#### Integration Tests

**Required Environment Variables:**
```bash
export QUARTZBIO_API_HOST=https://api-test.quartzbio.com
export QUARTZBIO_ACCESS_TOKEN=test_token_here
```

**Running Tests:**
```bash
# With environment variables set
python setup.py test

# Or with make
make check

# Or with specific test
python -m unittest quartzbio.test.test_dataset
```

**Test Configuration:**

Tests use `QuartzBioTestCase` from `test/helper.py`:
```python
class QuartzBioTestCase(unittest.TestCase):
    def setUp(self):
        self.client = quartzbio.QuartzBioClient(
            host=os.environ.get("QUARTZBIO_API_HOST"),
            token=os.environ.get("QUARTZBIO_ACCESS_TOKEN")
        )
```

**Important:** Tests are integration tests that require live API credentials, not mocked.

---

### CI/CD Environment (GitLab CI)

**File:** `.gitlab-ci.yml` (references variables, not values)

#### GitLab CI Variables Configuration

Secrets are stored as **GitLab CI/CD Variables** (Settings → CI/CD → Variables):

**Required Variables:**
```
QUARTZBIO_API_HOST          (protected)
QUARTZBIO_ACCESS_TOKEN      (masked, protected)
PYPI_TOKEN                  (masked, protected) - For releases
GITHUB_TOKEN                (masked, protected) - For changelog
```

#### Using Variables in .gitlab-ci.yml

```yaml
test:
  stage: test
  script:
    - pip install -e .
    - python setup.py test
  variables:
    QUARTZBIO_API_HOST: $QUARTZBIO_API_HOST
    QUARTZBIO_ACCESS_TOKEN: $QUARTZBIO_ACCESS_TOKEN

release:
  stage: deploy
  script:
    - pip install twine
    - python setup.py sdist bdist_wheel
    - twine upload dist/* -u __token__ -p $PYPI_TOKEN
  only:
    - tags
```

---

### PyPI Release Environment

**File:** `~/.pypirc` (for package maintainers)

```ini
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...your-token-here
```

**Setup:**
```bash
# Create PyPI config
cat > ~/.pypirc <<EOF
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = your-pypi-token-here
EOF

chmod 600 ~/.pypirc
```

**Usage:**
```bash
# Build package
python setup.py sdist bdist_wheel

# Upload to PyPI (uses ~/.pypirc)
twine upload dist/*

# Or with make
make release
```

**Security:** Never commit `.pypirc` to version control. It's in `.gitignore`.

---

## Secret Reference Guide

### How Secrets Are Consumed in Code

#### API Authentication

**In `auth.py`:**
```python
def get_credentials(api_host=None, api_key=None):
    """
    Credential resolution priority:
    1. api_key parameter (explicit)
    2. QUARTZBIO_ACCESS_TOKEN env var
    3. EDP_ACCESS_TOKEN env var
    4. SOLVEBIO_ACCESS_TOKEN env var (legacy)
    5. ~/.quartzbio/credentials file (netrc format)
    """

    if api_key:
        return api_key

    # Check environment variables
    api_key = os.environ.get('QUARTZBIO_ACCESS_TOKEN')
    if api_key:
        return api_key

    # Check credentials file
    creds_path = os.path.expanduser('~/.quartzbio/credentials')
    # ... netrc parsing logic
```

#### Client Initialization

**In `client.py`:**
```python
class QuartzBioClient:
    def __init__(self, api_host=None, api_key=None, access_token=None, **kwargs):
        # Resolve credentials via auth.get_credentials()
        self.api_host = api_host or os.environ.get('QUARTZBIO_API_HOST') or default_host
        self.api_key = access_token or api_key or get_credentials(self.api_host)
```

#### CLI Commands

**In `cli/main.py`:**
```python
def login_and_save_credentials(args):
    """Login and save credentials to ~/.quartzbio/credentials"""
    api_host = args.api_host or os.environ.get('QUARTZBIO_API_HOST')
    email = args.email or input('Email: ')
    password = getpass.getpass('Password: ')

    # Authenticate and get token
    token = authenticate(api_host, email, password)

    # Save to credentials file
    save_credentials(api_host, email, token)
```

### Required vs Optional Secrets

**Required (Client won't work without these):**
- API access token (via any of the 3 methods)
- API host URL (defaults to production if not specified)

**Optional (For specific operations):**
- `GITHUB_TOKEN` - Only for changelog generation
- `PYPI_TOKEN` - Only for PyPI releases
- `QUARTZBIO_LOGLEVEL` - Defaults to WARN
- `QUARTZBIO_LOGFILE` - Defaults to ~/.quartzbio/quartzbio.log

### Default Test Values

For local development and testing:

```bash
# Test Environment
export QUARTZBIO_API_HOST=https://api-test.quartzbio.com
export QUARTZBIO_ACCESS_TOKEN=test_token_from_team_lead

# Development Environment
export QUARTZBIO_API_HOST=https://api-dev.quartzbio.com
export QUARTZBIO_ACCESS_TOKEN=dev_token_from_team_lead
```

**⚠️ NEVER use production tokens for testing!**

---

## Best Practices

### For Developers

#### ✅ DO:
- Use `quartzbio login` to save credentials securely
- Store test tokens in environment variables
- Use separate tokens for dev/test/prod
- Keep credentials file permissions at 600 (owner read/write only)
- Request tokens from team lead for testing
- Use ~/.pypirc for PyPI credentials (not env vars)

#### ❌ DON'T:
- Commit credentials to git
- Share tokens via email or Slack
- Use production tokens in tests
- Hardcode tokens in code
- Log tokens (even in DEBUG mode)
- Store tokens in shell history

### Token Management

**Creating Tokens:**
1. Log in to QuartzBio web interface
2. Go to Account Settings → API Tokens
3. Create new token with appropriate permissions
4. Copy token immediately (shown only once)
5. Save to credentials file or environment variable

**Rotating Tokens:**
1. Create new token in web interface
2. Update credentials file or environment variable
3. Test that new token works
4. Revoke old token in web interface

**Revoking Tokens:**
1. Go to Account Settings → API Tokens
2. Revoke compromised token immediately
3. Create replacement token
4. Update all systems using the old token

### Debugging Secret Issues

Common issues and solutions:

**Problem: "No token found" error**
```bash
# Check environment variables
echo $QUARTZBIO_ACCESS_TOKEN

# Check credentials file exists
cat ~/.quartzbio/credentials

# Check file permissions
ls -la ~/.quartzbio/credentials  # Should be -rw------- (600)

# Fix permissions if needed
chmod 600 ~/.quartzbio/credentials
```

**Problem: "Authentication failed" error**
```bash
# Verify token is valid
quartzbio whoami

# Check API host is correct
echo $QUARTZBIO_API_HOST

# Try re-logging in
quartzbio logout
quartzbio login
```

**Problem: Tests fail with authentication error**
```bash
# Verify test environment variables are set
env | grep QUARTZBIO

# Set them if missing
export QUARTZBIO_API_HOST=https://api-test.quartzbio.com
export QUARTZBIO_ACCESS_TOKEN=your_test_token

# Run tests again
python setup.py test
```

---

## Claude Code Guidelines

### When Claude Code Works with Secrets

#### ✅ Claude Code CAN:
- Read auth.py to understand credential resolution
- Suggest environment variable names
- Create credential file templates (without actual values)
- Document required environment variables
- Add token validation code
- Improve error messages for missing credentials

#### ❌ Claude Code MUST NOT:
- Generate actual API tokens
- Display tokens from environment or files
- Commit credentials to version control
- Suggest storing tokens in code
- Use production tokens in examples
- Modify ~/.quartzbio/credentials directly

### Prompting for Secret-Related Tasks

**Good Prompts:**

```
"Add validation to check if QUARTZBIO_ACCESS_TOKEN is set before running tests"
```

```
"Document the credential resolution priority order in auth.py docstrings"
```

```
"Add a better error message when no credentials are found, suggesting how to set them up"
```

**Bad Prompts:**

```
"Generate a QuartzBio API token for me"  ❌ Claude cannot generate real tokens
```

```
"Show me the token from my credentials file"  ❌ Claude should not display secrets
```

```
"Add my token xyz123 to the code"  ❌ Never hardcode secrets
```

### Code Patterns Claude Should Follow

**Good: Read from environment**
```python
def get_token():
    token = os.environ.get("QUARTZBIO_ACCESS_TOKEN")
    if not token:
        raise ValueError(
            "No API token found. Set QUARTZBIO_ACCESS_TOKEN environment variable "
            "or run 'quartzbio login' to save credentials."
        )
    return token
```

**Good: Document required secrets**
```python
class QuartzBioClient:
    """
    QuartzBio API client.

    Requires authentication via one of:
    1. access_token parameter
    2. QUARTZBIO_ACCESS_TOKEN environment variable
    3. ~/.quartzbio/credentials file (created by 'quartzbio login')
    """
```

**Good: Secure credential storage**
```python
def save_credentials(api_host, email, token):
    """Save credentials to ~/.quartzbio/credentials with secure permissions"""
    creds_path = os.path.expanduser('~/.quartzbio/credentials')
    # ... write to file ...
    os.chmod(creds_path, 0o600)  # Owner read/write only
```

**Bad: Hardcoded tokens**
```python
API_TOKEN = "abc123..."  # ❌ Never do this
```

**Bad: Logging tokens**
```python
logger.debug(f"Using token: {token}")  # ❌ Leaks secrets to logs
```

**Bad: Exposing tokens**
```python
def get_client_info():
    return {"token": client.api_key}  # ❌ Don't expose tokens
```

---

## Secret Audit Checklist

Use this checklist to verify secret management:

### Code Review
- [ ] No hardcoded tokens in code
- [ ] All tokens read from environment or credentials file
- [ ] Tokens not logged or printed
- [ ] Tokens not returned in API responses or displayed to users
- [ ] Token validation for required values
- [ ] Appropriate error messages (don't leak token values)
- [ ] Credentials file has secure permissions (600)

### Environment Configuration
- [ ] `.gitignore` includes `.pypirc`, credentials files
- [ ] Required secrets documented in README
- [ ] Secret injection documented in CLAUDE_SECRET_INJECTION.md
- [ ] Test environment uses separate tokens
- [ ] CI/CD uses masked/protected variables

### PyPI Configuration (Maintainers)
- [ ] `~/.pypirc` has secure permissions (600)
- [ ] PyPI token has minimal required scope
- [ ] Token is backed up securely
- [ ] Only maintainers have PyPI access

### CI/CD Configuration
- [ ] GitLab CI variables marked as "masked"
- [ ] Production tokens marked as "protected"
- [ ] No tokens in `.gitlab-ci.yml` file
- [ ] Test tokens separate from production

---

## Quick Reference: Getting API Credentials

### For End Users

**Via CLI (Recommended):**
```bash
# Interactive login
quartzbio login
# Enter email and password
# Credentials saved to ~/.quartzbio/credentials
```

**Via Web Interface:**
```bash
# 1. Log in to https://app.quartzbio.com
# 2. Go to Account Settings → API Tokens
# 3. Create new token
# 4. Copy token and save to environment variable
export QUARTZBIO_ACCESS_TOKEN=your_token_here
```

### For Developers

**Get test credentials from team lead:**
```bash
# Request test environment token
export QUARTZBIO_API_HOST=https://api-test.quartzbio.com
export QUARTZBIO_ACCESS_TOKEN=test_token_from_team_lead

# Run tests
python setup.py test
```

### For Maintainers

**PyPI credentials:**
```bash
# Get PyPI token from pypi.org
# Add to ~/.pypirc (see PyPI Release Environment section)
```

**GitHub token for changelog:**
```bash
# Create personal access token at github.com/settings/tokens
# Needs 'repo' scope
export GITHUB_TOKEN=your_github_token
make changelog
```

---

## Troubleshooting

### "No token found"

**Cause:** No credentials configured

**Solution:**
```bash
# Option 1: Login via CLI
quartzbio login

# Option 2: Set environment variable
export QUARTZBIO_ACCESS_TOKEN=your_token_here

# Option 3: Create credentials file
mkdir -p ~/.quartzbio
cat > ~/.quartzbio/credentials <<EOF
machine api.quartzbio.com
login your-email@example.com
password your_token_here
EOF
chmod 600 ~/.quartzbio/credentials
```

---

### "Authentication failed"

**Cause:** Invalid or expired token

**Solution:**
```bash
# Re-login
quartzbio logout
quartzbio login

# Or request new token from web interface
# and update environment variable
```

---

### "Permission denied" on credentials file

**Cause:** Incorrect file permissions

**Solution:**
```bash
# Fix permissions
chmod 600 ~/.quartzbio/credentials

# Verify
ls -la ~/.quartzbio/credentials
# Should show: -rw------- (owner read/write only)
```

---

### Tests fail with "No token found"

**Cause:** Environment variables not set for tests

**Solution:**
```bash
# Set test credentials
export QUARTZBIO_API_HOST=https://api-test.quartzbio.com
export QUARTZBIO_ACCESS_TOKEN=test_token_from_team_lead

# Run tests
python setup.py test
```

---

## Summary

### Key Takeaways

1. **Local Development**: Use `quartzbio login` or environment variables
2. **Testing**: Use environment variables with test tokens
3. **CI/CD**: Use GitLab CI Variables (masked and protected)
4. **PyPI**: Use ~/.pypirc with secure permissions
5. **Never Commit**: Keep secrets out of version control

### For Claude Code Users

When working with Claude Code:
- Reference this document for credential configuration
- Ask Claude to read from environment variables, never hardcode
- Have Claude validate required credentials exist
- Use Claude to document new credential requirements

---

**Last Updated:** 2026-01-27
**Maintained By:** Engineering Team
**Review Schedule:** Quarterly
