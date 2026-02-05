# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the QuartzBio Python client library and CLI - a genomic data platform client that provides programmatic access to datasets, vaults, and genomic analysis tools via REST API. The library uses a mixin-based resource architecture with automatic credential management and lazy evaluation patterns.

## Development Commands

### Initial Setup

```bash
# Clone and install in development mode
git clone https://github.com/quartzbio/quartzbio-python.git
cd quartzbio-python/
pip install -e .

# Or use virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Testing

```bash
# Run all tests
python setup.py test

# Run tests with make
make check

# Run specific test module
make test-sample              # Runs quartzbio.test.test_sample
make test-dataset             # Runs quartzbio.test.test_dataset
python -m unittest quartzbio.test.test_query

# Run tests across multiple Python versions
pip install tox
tox
```

**Important**: Tests require live API credentials. Set environment variables:
```bash
export QUARTZBIO_API_HOST=https://api.quartzbio.com
export QUARTZBIO_ACCESS_TOKEN=your_token_here
```

### Linting

```bash
# Run flake8 (max line length: 120)
flake8 quartzbio

# Or use make
make lint
```

**Ignored flake8 codes**: E127, E203, E402, N801, N802, E722, W504, W503

### Building & Releasing

```bash
# Create source and wheel distributions
make dist

# Bump version (creates git tag)
bumpversion patch   # or minor, major
git push --tags

# Generate changelog
make changelog      # Uses github_changelog_generator

# Release to PyPI (requires Twine configuration)
make release
```

### Documentation

```bash
# Build and serve docs locally (http://localhost:8080)
make sphinx-autobuild

# Generate API documentation
make sphinx-apidoc

# Build HTML docs
make sphinx-build
```

## Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────────┐
│         CLI Interface (cli/)            │
│    argparse-based command routing       │
├─────────────────────────────────────────┤
│   Public API Layer (Query, Filter)     │
│  Query DSL, GenomicFilter, Annotator   │
├─────────────────────────────────────────┤
│   Resource Layer (resource/)            │
│  APIResource + Mixins (CRUD operations) │
├─────────────────────────────────────────┤
│   HTTP Client (client.py)              │
│  QuartzBioClient - requests-based      │
├─────────────────────────────────────────┤
│   Auth & Credentials (auth.py)         │
│  Token management & storage (netrc)    │
└─────────────────────────────────────────┘
```

### Mixin-Based Resource System

Resources compose functionality through multiple inheritance:

```python
class Dataset(
    CreateableAPIResource,      # Class method create() for POST
    ListableAPIResource,        # Class method all() for GET list
    DeletableAPIResource,       # Instance method delete() for DELETE
    UpdateableAPIResource,      # Instance method save() for PATCH
):
    RESOURCE_VERSION = 2

    # Custom methods for related resources
    def fields(self, **params):
        # GET /v2/datasets/{id}/fields
```

**Available Mixins** (in `resource/apiresource.py`):
- `CreateableAPIResource` - `create()`
- `ListableAPIResource` - `all()`, `search()`, pagination
- `DeletableAPIResource` - `delete()` with confirmation
- `UpdateableAPIResource` - `save()` with change tracking via `_unsaved_values`
- `DownloadableAPIResource` - `download()`
- `SearchableAPIResource` - `search()`
- `SingletonAPIResource` - For single-instance resources (User)

**Resources declare exactly which operations they support**, reducing code duplication across 20+ resource types.

### Base Class Hierarchy

**`QuartzBioObject`** (`quartzbio_object.py`):
- Inherits from `dict` - all API responses are dicts with attribute access
- Tracks unsaved changes in `_unsaved_values` set
- Automatic nested object conversion via `convert_to_quartzbio_object()`
- Dynamic attribute access: `obj.field_name` instead of `obj['field_name']`

**`APIResource`** (`apiresource.py`):
- Extends `QuartzBioObject`
- URL generation: `class_url()` and `instance_url()`
- Automatic endpoint mapping: `Dataset` → `/v2/datasets`
- Centralized `refresh()` method for current state

### Type Registration System

In `resource/__init__.py`, all resource types are registered:

```python
types = {
    "Application": Application,
    "Dataset": Dataset,
    "Vault": Vault,
    # ... 20+ types
}
```

**Automatic type conversion**: When API returns `{"class_name": "Dataset", ...}`, it constructs a `Dataset` instance, not generic `QuartzBioObject`.

### Authentication & Credentials

**Multi-source credential resolution** (`auth.py`):

Priority order:
1. Function parameters (highest)
2. Environment variables: `QUARTZBIO_ACCESS_TOKEN`, `QUARTZBIO_API_HOST`, `EDP_ACCESS_TOKEN`, `SOLVEBIO_ACCESS_TOKEN`
3. Credentials file: `~/.quartzbio/credentials` (netrc format)
4. Raises error if none found (unless `debug=True`)

**Token types**:
- `Bearer` - Access tokens (OAuth2)
- `Token` - API keys

**Credential storage** (`cli/credentials.py`):
- Location: `~/.quartzbio/credentials` (Unix) or `~\_quartzbio\credentials` (Windows)
- Format: Standard netrc format
- Security: OS-controlled file permissions

### Query System

Three-tier query DSL in `query.py`:

**1. Filter Objects** - Build WHERE clauses:
```python
# Declarative filter building
f = Filter(gene='BRCA1', chr='13')
f &= Filter(start__gt=1000)       # AND operator
f |= Filter(status='pathogenic')  # OR operator
~f                                # NOT operator

# Supported operators:
# __in=[...], __range=[start,end], __gt, __gte, __lt, __lte
```

**2. GenomicFilter** - Genomic range queries:
```python
# UCSC-style ranges
gf = GenomicFilter.from_string("chr1:100-200")
# Or explicit: GenomicFilter('chr1', 100, 200, exact=False)

# Generates: genomic_coordinates.chromosome/start/stop filters
```

**3. Query Class** - Execution and iteration:
```python
q = dataset.query(Filter(gene__in=['BRCA1', 'TP53']))
q = q.filter(effect='missense')   # Chainable
q = q.limit(1000)

# Lazy evaluation - no request until accessed
for record in q:
    process(record)

# Slicing support
subset = q[100:200]

# Count without fetching all
total = q.count()
```

**Features**:
- Lazy evaluation - requests only when accessed
- Automatic pagination handling
- Streaming support - doesn't load all into memory
- Length aware of limit: `len(q)`

### CLI Implementation

**Pattern**: Custom `ArgumentParser` with declarative subcommands (`cli/main.py`):

```python
class QuartzBioArgumentParser(argparse.ArgumentParser):
    subcommands = {
        "login": {
            "func": auth.login_and_save_credentials,
            "help": "Login and save credentials",
            "arguments": [...]  # Declarative argument specs
        },
        "import": {...},
        "create-dataset": {...},
        # ... more commands
    }
```

**Key commands**:
- `quartzbio login` - Authenticate and save credentials
- `quartzbio logout` - Delete credentials
- `quartzbio whoami` - Show current user
- `quartzbio shell` - Launch IPython with pre-loaded client
- `quartzbio import` - Import files with progress tracking
- `quartzbio create-dataset` - Create new dataset
- `quartzbio upload` - Upload files to vault

**Entry point**: Configured in `setup.py`:
```python
entry_points={
    'console_scripts': ['quartzbio = quartzbio.cli.main:main']
}
```

### URL Construction Patterns

Automatic endpoint generation in `resource/util.py`:

```python
class_url() = "/v{RESOURCE_VERSION}/{pluralized_snake_case}"
instance_url() = "/v{RESOURCE_VERSION}/{pluralized_snake_case}/{id}"

# Examples:
Dataset → /v2/datasets, /v2/datasets/{id}
DatasetField → /v2/dataset_fields, /v2/dataset_fields/{id}
User → /v1/user  # SingletonAPIResource - no plural, no ID
```

Conversion utilities:
- `camelcase_to_underscore()` - `DatasetField` → `dataset_field`
- `class_to_api_name()` - Handles pluralization

### Error Handling

Custom exception hierarchy in `errors.py`:

```python
class QuartzBioError(Exception):
    """Main exception with:
    - status_code: HTTP status
    - message: Formatted from JSON response
    - json_body: Full API response
    - field_errors: Field-specific errors
    """

class NotFoundError(Exception)       # 404
class FileUploadError(Exception)     # Upload errors
```

**Error message construction**:
- Extracts `non_field_errors`, `detail`, and field-specific errors from API JSON
- 400 Bad Request includes URL and field errors
- Network errors suggest: `pip install --upgrade urllib3 certifi`

### HTTP Client Configuration

In `client.py`:

**Retry logic**:
```python
retries = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[502, 503, 504],  # Bad gateway, unavailable, timeout
)
```

**Environment variable**: `QUARTZBIO_RETRY_ALL` - if set, retries all methods (POST, PATCH, DELETE). Default: only idempotent (GET, HEAD) are retried.

**Timeout**: 80 seconds default

**TLS**: Minimum TLS 1.2 enforced

### Logging

Configured in `__init__.py`:

**Environment variables**:
- `QUARTZBIO_LOGLEVEL` - Default: `WARN`
- `QUARTZBIO_LOGFILE` - Default: `~/.quartzbio/quartzbio.log`

**Dual output**:
1. Stream (stderr) - Format: `[QuartzBio] %(message)s`
2. File - Full timestamp/level format

## Key Patterns & Conventions

### 1. Lazy Evaluation
Resources and queries don't fetch until accessed:
```python
q = dataset.query(...)  # No API call
for r in q:             # NOW the API call happens
    process(r)
```

### 2. Change Tracking
`_unsaved_values` set tracks modifications for PATCH:
```python
obj = Dataset.retrieve(id)
obj.title = "New Title"       # Adds 'title' to _unsaved_values
obj.save()                    # PATCH with only changed fields
```

### 3. Type Safety
API responses automatically converted to correct resource classes via type registry.

### 4. Pagination Transparency
Iteration automatically fetches next pages:
```python
for item in client.Dataset.all():  # Handles pagination automatically
    process(item)
```

### 5. Dictionary as Base
All resources are dicts, enabling flexible access:
```python
dataset['title']           # Dict access
dataset.title              # Attribute access
dataset.get('title', '')   # Dict methods work
```

### 6. Progress Visibility
Task resources show progress during long operations:
```python
task.follow(loop=True, sleep_seconds=5)
# Prints: Progress: 50/100
# Auto-refreshes with task.refresh() in loop
```

## Testing Patterns

**Base test class** (`test/helper.py`):
```python
class QuartzBioTestCase(unittest.TestCase):
    TEST_DATASET_FULL_PATH = "quartzbio:Public:/HGNC/3.3.1-2021-08-25/HGNC"

    def setUp(self):
        self.client = quartzbio.QuartzBioClient(
            host=os.environ.get("QUARTZBIO_API_HOST"),
            token=os.environ.get("QUARTZBIO_ACCESS_TOKEN")
        )
```

**Important**: Tests are integration tests requiring live API credentials, not mocked.

## Extension Points

The architecture supports extensions through:

1. **New Resources** - Add class extending appropriate mixins in `resource/`
2. **Custom Queries** - Subclass `Query` or `BatchQuery`
3. **CLI Commands** - Add to `subcommands` dict in `cli/main.py`
4. **Custom Filters** - Subclass `Filter` for domain-specific filtering
5. **Authentication Strategies** - Extend `QuartzBioTokenAuth` in `auth.py`

## Python Version Support

Supports Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

**Dependencies**:
- Core: `requests>=2.0.0`, `urllib3>=1.26.0`, `pyprind`
- Optional: `quartzbio[recipes]` - adds `pyyaml`, `click`, `ruamel.yaml`

## Environment Variables Reference

- `QUARTZBIO_API_HOST` - API URL (default: from credentials file)
- `QUARTZBIO_ACCESS_TOKEN` - OAuth2 access token
- `EDP_ACCESS_TOKEN` - Alternative token env var
- `SOLVEBIO_ACCESS_TOKEN` - Legacy token env var
- `QUARTZBIO_LOGLEVEL` - Log level (default: WARN)
- `QUARTZBIO_LOGFILE` - Log file path (default: ~/.quartzbio/quartzbio.log)
- `QUARTZBIO_RETRY_ALL` - Retry all HTTP methods (default: false, only idempotent)
