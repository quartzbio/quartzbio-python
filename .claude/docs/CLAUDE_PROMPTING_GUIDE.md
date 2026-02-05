# Claude Code Prompting Guide - QuartzBio Python Client

This guide provides effective prompts and workflows for using Claude Code with the QuartzBio Python client library and CLI. Copy and adapt these prompts for your specific needs.

## Table of Contents
- [Testing Workflows](#testing-workflows)
- [Debugging Patterns](#debugging-patterns)
- [Feature Development](#feature-development)
- [Code Review](#code-review)

---

## Testing Workflows

### Running Tests

**Basic Test Execution**
```
Run all tests for the QuartzBio Python client
```

**Specific Test Module**
```
Run the dataset tests using make test-dataset
```

**Single Test Class**
```
Run the Query test class in quartzbio/test/test_query.py
```

**Test with Multiple Python Versions**
```
Run tox to test across Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
```

### Debugging Test Failures

**Investigate Failing Integration Test**
```
The test test_dataset_query in test_dataset.py is failing with a 404 error.
Help me understand why and fix it. The test requires live API credentials.
```

**Analyze Test Output**
```
Here's the test output [paste output]. What's causing this assertion failure
in the query pagination test?
```

**Fix Tests After Resource Changes**
```
I modified the Dataset resource to add a new method. Now several tests are failing
with import errors. Help me identify which tests need updating and fix them.
```

**Check Test Coverage**
```
What's the test coverage for the quartzbio.query module? Are there any
critical code paths without tests?
```

### Writing New Tests

**Create Test for New Resource**
```
I added a new DatasetTemplate resource with ListableAPIResource and CreateableAPIResource mixins.
Write comprehensive tests covering:
- Listing all templates
- Creating a new template
- Error handling for missing required fields
- Authentication requirements
```

**Add Missing Test Cases**
```
Review the GenomicFilter class and identify any untested edge cases.
Write tests for those scenarios using the QuartzBioTestCase pattern.
```

**Create Integration Test**
```
Create an integration test that:
1. Authenticates with test credentials
2. Queries a public dataset
3. Applies a GenomicFilter
4. Verifies the query results
5. Checks pagination
```

### Test Fixtures and Setup

**Understand Test Setup**
```
Explain the QuartzBioTestCase setup in test/helper.py and what test dataset
it uses by default
```

**Create Custom Test Data**
```
Create test fixtures for a dataset query that returns genomic variants with
fields: chromosome, position, gene, effect
```

---

## Debugging Patterns

### Investigating Errors

**API Error Investigation**
```
The Dataset.query() method is returning a QuartzBioError with status 400.
Help me trace the request construction and identify why the filter is invalid.
```

**Exception Analysis**
```
I'm getting this error: [paste traceback].
It's coming from the query iteration. Explain what's happening and suggest fixes.
```

**Authentication Issues**
```
The client is failing to authenticate with "No token found" error even though
I have QUARTZBIO_ACCESS_TOKEN set. Help me debug the credential resolution logic.
```

**Pagination Problems**
```
Query iteration is not fetching all results. It stops after the first page.
Check the pagination logic in the Query class.
```

### Tracing Code Paths

**Follow API Request Flow**
```
Trace the complete flow for client.Dataset.create(data) including:
- Resource mixin method resolution
- URL construction
- HTTP request execution
- Response conversion to Dataset object
- Type registration system
```

**Understand Lazy Evaluation**
```
How does lazy evaluation work in the Query class? Show me the code path from
query creation to actual API request during iteration.
```

**Track Change Detection**
```
When I modify dataset.title = "New", how does _unsaved_values tracking work?
Show me the code path from attribute assignment to save().
```

### CLI Debugging

**Parse CLI Command Issues**
```
The 'quartzbio import' command is failing with "unrecognized arguments" error.
Help me debug the ArgumentParser configuration in cli/main.py.
```

**Credential File Problems**
```
'quartzbio login' saves credentials but 'quartzbio whoami' says "not authenticated".
Check the credential storage and retrieval logic in cli/credentials.py.
```

**Progress Tracking Issues**
```
The import progress bar isn't showing. Check the pyprind integration
in the import command.
```

### Environment and Configuration Issues

**Dependency Conflicts**
```
I'm getting import errors for requests module. Check setup.py dependencies
and suggest fixes.
```

**Python Version Compatibility**
```
The code fails on Python 3.8 with syntax errors. Check for compatibility
issues and suggest Python 3.8-compatible alternatives.
```

**TLS/SSL Errors**
```
Getting "SSL: CERTIFICATE_VERIFY_FAILED" errors. What's the recommended
fix in the documentation?
```

---

## Feature Development

### Adding Resources

**Create New Resource**
```
Create a new DatasetSnapshot resource that:
- Supports listing (ListableAPIResource)
- Supports deletion (DeletableAPIResource)
- Uses API v2 (RESOURCE_VERSION = 2)
- Has a custom restore() method that POSTs to /v2/dataset_snapshots/{id}/restore/
- Is registered in resource/__init__.py types dict

Include:
- Resource class definition
- Type registration
- URL construction verification
- Basic tests
```

**Extend Existing Resource**
```
Add a validate() method to the Dataset resource that:
- POSTs to /v2/datasets/{id}/validate/
- Returns validation results
- Handles validation errors appropriately
```

**Add Resource Relationship**
```
Add a fields() method to Dataset that returns related DatasetField objects:
- Uses self.instance_url() + '/fields'
- Returns ListObject with DatasetField instances
- Supports pagination
```

### Implementing Query Features

**New Filter Operator**
```
Add a __contains filter operator to the Filter class that generates
a "contains" query parameter for text search.
```

**Batch Query Support**
```
Implement a BatchQuery class that:
- Extends Query
- Accepts multiple Filter objects
- Makes parallel requests
- Combines results
```

**Query Result Export**
```
Add a to_dataframe() method to Query that:
- Fetches all results
- Converts to pandas DataFrame
- Handles pagination automatically
- Preserves field types
```

### CLI Commands

**New CLI Command**
```
Add a 'quartzbio export' command that:
- Accepts dataset ID and output file path
- Queries the dataset
- Exports to CSV or JSON
- Shows progress bar
- Handles large datasets with streaming

Add to cli/main.py subcommands dict following the existing pattern.
```

**CLI Argument Validation**
```
Add validation to the 'quartzbio import' command to check:
- File exists and is readable
- Dataset path is valid format
- Template ID exists
- Required fields are present
```

### Client Features

**Retry Configuration**
```
Add configurable retry settings to QuartzBioClient:
- Allow custom retry count
- Allow custom backoff factor
- Allow custom status codes to retry
- Respect QUARTZBIO_RETRY_ALL environment variable
```

**Response Caching**
```
Implement simple caching for GET requests:
- Use dict cache with URL as key
- Add TTL (time-to-live) parameter
- Add cache_enabled flag to client
- Invalidate on POST/PATCH/DELETE
```

### Documentation

**Docstring Improvements**
```
Add comprehensive docstrings to all public methods in the Query class
following Google docstring style with:
- Description
- Args with types
- Returns with type
- Raises with exception types
- Example usage
```

**Sphinx Documentation**
```
Create a new Sphinx documentation page for the Query DSL with:
- Overview of Filter, GenomicFilter, Query classes
- Code examples
- Common patterns
- API reference links
```

---

## Code Review

### Security Checks

**Credential Handling Review**
```
Review credential management in auth.py and cli/credentials.py for security issues:
- Are credentials stored securely?
- Are file permissions correct?
- Are credentials logged anywhere?
- Are environment variables handled safely?
Suggest improvements
```

**Input Validation Review**
```
Review user input handling in CLI commands for:
- Path traversal vulnerabilities
- Command injection risks
- Unsafe file operations
- SQL injection in query filters
List any issues found
```

**Dependency Security**
```
Check setup.py and requirements for:
- Outdated packages with known vulnerabilities
- Unpinned versions
- Unnecessary dependencies
Suggest updates
```

### Code Quality

**Type Hints**
```
Add type hints to all public methods in quartzbio/resource/apiresource.py
for better IDE support and static analysis
```

**Code Duplication**
```
Find duplicated code patterns in the resource/ directory and suggest how to
refactor using shared utilities or base class methods
```

**Method Complexity**
```
Identify overly complex methods (>50 lines, deep nesting) in quartzbio/query.py
and suggest refactoring
```

**Error Message Clarity**
```
Review error messages in errors.py and throughout the codebase:
- Are they helpful to users?
- Do they suggest solutions?
- Are they consistent?
Suggest improvements
```

### Testing Quality

**Test Coverage Analysis**
```
Analyze test coverage for quartzbio/client.py:
- What percentage is covered?
- Which error paths are untested?
- What edge cases are missing?
Suggest specific tests to add
```

**Integration Test Review**
```
Review integration tests in test/ directory:
- Do they properly clean up after themselves?
- Are they properly isolated?
- Do they handle API failures gracefully?
- Are test credentials managed securely?
```

**Mock vs Integration Balance**
```
Evaluate test/ directory and suggest which tests should use mocks
vs real API calls for better test speed and reliability
```

### Python Best Practices

**PEP 8 Compliance**
```
Review quartzbio/resource/util.py for PEP 8 compliance:
- Line length (max 120)
- Naming conventions
- Import ordering
- Docstring style
List any violations
```

**Python 3.8+ Compatibility**
```
Review the codebase for Python 3.8 compatibility:
- Use of newer syntax features
- Type hints that require newer versions
- Deprecated features
Suggest changes for 3.8 support
```

**Dependency Management**
```
Review setup.py for dependency best practices:
- Are version ranges appropriate?
- Are minimum versions specified?
- Are extras_require organized well?
- Should any dependencies be optional?
```

### Performance Analysis

**Query Optimization**
```
Review the Query class for performance issues:
- Unnecessary API calls
- Inefficient iteration
- Memory usage for large result sets
- Opportunities for lazy loading
Suggest optimizations
```

**Resource Instantiation**
```
Check if resource objects are created efficiently:
- Unnecessary type conversions
- Redundant dictionary operations
- Excessive deepcopy usage
Profile and suggest improvements
```

**CLI Performance**
```
Review CLI startup time and suggest optimizations:
- Lazy imports
- Deferred initialization
- Caching strategies
```

### Documentation Quality

**README Clarity**
```
Review README.md for:
- Clear getting started instructions
- Up-to-date examples
- Complete feature list
- Proper troubleshooting section
Suggest improvements
```

**API Documentation Completeness**
```
Check that all public classes and methods in quartzbio/ have proper documentation:
- Missing docstrings
- Incomplete examples
- Outdated information
List gaps and suggest additions
```

**Code Example Accuracy**
```
Review all code examples in docs/ and docstrings:
- Do they run without errors?
- Are they using current API?
- Are they following best practices?
Update outdated examples
```

---

## Pro Tips for Effective Prompting

### Be Specific
❌ "Fix the query"
✅ "Fix the GenomicFilter.from_string() method that's failing to parse 'chr1:100-200' with a ValueError"

### Provide Context
❌ "This is broken"
✅ "The Dataset.query() is failing when I use Filter(gene__in=['BRCA1', 'TP53']). Here's the error: [paste]. The API expects a comma-separated string, not a list."

### Break Down Complex Tasks
❌ "Build a complete data export system"
✅ "First, help me design the export CLI command structure. Then we'll implement the query logic, then streaming to file, then add progress tracking, then write tests."

### Ask for Explanations
- "Explain how the mixin system works before adding a new mixin"
- "What are the tradeoffs of this approach?"
- "Why does the resource use lazy evaluation here?"

### Request Multiple Options
- "Show me 3 different approaches to implement query result caching"
- "What are the pros and cons of using a separate BatchQuery class vs extending Query?"

### Iterative Refinement
- Start with basic implementation
- Ask for code review
- Request optimization
- Add comprehensive tests

---

## Common Pitfalls to Avoid

### Don't Skip Reading Code First
❌ "Add a method to Dataset"
✅ "Read the Dataset resource class, then add an export() method following the existing pattern"

### Don't Assume Context
- Always mention you're working with a Python SDK client
- Specify if changes need to maintain backward compatibility
- Clarify if changes affect CLI users vs library users

### Don't Ignore Tests
- Always run tests after code changes
- Request test additions for new features
- Verify integration tests still pass with live API

### Don't Forget Documentation
- Update docstrings for modified methods
- Add examples for new features
- Update CLAUDE.md if architecture changes
- Regenerate Sphinx docs if needed

---

## Getting Help

If Claude Code doesn't understand your prompt:
1. Provide more context about the mixin-based architecture
2. Reference specific files, classes, or methods
3. Include relevant error messages or stack traces
4. Break the task into smaller steps
5. Reference CLAUDE.md for architecture details

For questions about Claude Code itself: `/help`

For QuartzBio Python client architecture: Reference `CLAUDE.md`
