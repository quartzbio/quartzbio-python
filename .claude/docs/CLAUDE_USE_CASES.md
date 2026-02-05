# Claude Code Use Cases - QuartzBio Python Client

This document outlines effective use cases, quick wins, and important guardrails for using Claude Code with the QuartzBio Python client library and CLI codebase.

## Table of Contents
- [Quick Wins](#quick-wins)
- [Common Use Cases](#common-use-cases)
- [Guardrails](#guardrails)
- [Limitations](#limitations)
- [Real-World Examples](#real-world-examples)

---

## Quick Wins

These are tasks where Claude Code delivers immediate value with minimal risk:

### 1. Test Writing and Debugging
**Time Saved: 30-60 minutes per test suite**

✅ **Perfect For:**
- Writing integration tests for new resources
- Creating tests for query functionality
- Debugging failing tests with live API
- Adding test coverage for edge cases

**Example:**
```
"Write integration tests for the DatasetTemplate resource including list(),
create(), and error handling"
```

### 2. Code Explanation and Documentation
**Time Saved: 20-40 minutes per module**

✅ **Perfect For:**
- Understanding mixin-based architecture
- Documenting query DSL functionality
- Creating examples for CLI commands
- Explaining lazy evaluation patterns

**Example:**
```
"Explain how the mixin system works in the resource layer, including how
CreateableAPIResource, ListableAPIResource, and DeletableAPIResource
compose functionality"
```

### 3. Simple Bug Fixes
**Time Saved: 15-30 minutes per bug**

✅ **Perfect For:**
- Fixing query filter construction issues
- Correcting CLI argument parsing
- Resolving import errors
- Fixing credential resolution bugs

**Example:**
```
"The GenomicFilter.from_string() method fails on 'chrX:100-200'.
Fix the chromosome parsing logic to handle X and Y chromosomes"
```

### 4. Code Style and Formatting
**Time Saved: 10-20 minutes**

✅ **Perfect For:**
- Applying PEP 8 formatting (line length 120)
- Fixing flake8 issues
- Adding type hints to methods
- Improving docstring consistency

**Example:**
```
"Fix all flake8 violations in quartzbio/query.py and add type hints
to public methods"
```

### 5. Boilerplate Generation
**Time Saved: 20-45 minutes**

✅ **Perfect For:**
- Creating new resource classes with mixins
- Generating CLI command boilerplate
- Creating test case skeletons
- Writing Sphinx documentation stubs

**Example:**
```
"Create a new DatasetSnapshot resource with ListableAPIResource and
DeletableAPIResource mixins, using API v2"
```

### 6. Documentation Updates
**Time Saved: 15-30 minutes**

✅ **Perfect For:**
- Adding docstrings to methods
- Creating usage examples
- Updating README sections
- Generating Sphinx API docs

**Example:**
```
"Add Google-style docstrings to all public methods in quartzbio/client.py
with examples"
```

---

## Common Use Cases

### SDK Development

#### Resource Implementation
**Frequency: Monthly**

Use Claude Code for:
- Adding new resource classes with appropriate mixins
- Implementing custom resource methods
- Adding resource relationships (e.g., dataset.fields())
- Registering resources in type registry

**Example Workflow:**
1. "Read the Dataset resource to understand the pattern"
2. "Create a DatasetVersion resource with ListableAPIResource and CreateableAPIResource"
3. "Add a restore() method that POSTs to /v2/dataset_versions/{id}/restore/"
4. "Register the new resource in resource/__init__.py types dict"
5. "Write integration tests"

#### Query DSL Enhancement
**Frequency: Quarterly**

Use Claude Code for:
- Adding new filter operators
- Implementing query optimizations
- Adding result formatting options
- Improving pagination logic

**Example Workflow:**
```
"Add a __contains filter operator to the Filter class that generates
text search queries"
```

### CLI Development

#### New Commands
**Frequency: Monthly**

Use Claude Code for:
- Adding new CLI commands
- Implementing command argument validation
- Adding progress tracking
- Improving error messages

**Typical Pattern:**
1. Design command structure (arguments, options)
2. Add to subcommands dict in cli/main.py
3. Implement command logic
4. Add progress tracking if long-running
5. Write command tests
6. Update CLI documentation

#### CLI Improvements
**Frequency: Weekly**

Use Claude Code for:
- Improving argument parsing
- Adding output formatting options
- Implementing shell completion
- Better error handling

**Example:**
```
"Add a --format option to 'quartzbio query' that supports json, csv, and table output"
```

### Testing

#### Integration Test Development
**Frequency: Daily**

Use Claude Code for:
- Writing tests for new resources
- Creating query test scenarios
- Testing CLI commands
- Adding error case coverage

**Safe Approach:**
1. Understand QuartzBioTestCase setup
2. Set up test credentials properly
3. Write test scenarios
4. Run with live API
5. Verify cleanup

#### Test Maintenance
**Frequency: Weekly**

Use Claude Code for:
- Fixing tests after API changes
- Updating test data
- Improving test reliability
- Adding missing coverage

**Example:**
```
"The test_dataset_query tests are failing after API v2 changes.
Update them to work with the new response format"
```

### Package Management

#### Dependency Updates
**Frequency: Monthly**

Use Claude Code for:
- Reviewing dependency versions
- Checking for security updates
- Testing compatibility
- Updating requirements

**Example:**
```
"Check setup.py dependencies for outdated versions and security issues.
Suggest updates while maintaining Python 3.8+ compatibility"
```

#### Release Preparation
**Frequency: Per release**

Use Claude Code for:
- Generating changelog entries
- Updating version numbers
- Checking package metadata
- Verifying documentation

**Example:**
```
"Review recent commits and generate changelog entries for version 3.5.0
using the existing CHANGELOG.md format"
```

### Documentation

#### API Documentation
**Frequency: Weekly**

Use Claude Code for:
- Writing/updating docstrings
- Creating usage examples
- Building Sphinx docs
- Adding tutorials

#### README Updates
**Frequency: Monthly**

Use Claude Code for:
- Keeping examples current
- Adding new feature documentation
- Improving troubleshooting section
- Updating installation instructions

---

## Guardrails

### ❌ Do NOT Use Claude Code For:

#### 1. PyPI Releases
**Risk: High - Package distribution**

Never ask Claude Code to:
- Push releases to PyPI
- Update live package versions
- Modify PyPI credentials
- Execute twine upload

**Why:** Package releases need human oversight and verification.

**Instead:** Use Claude Code to prepare release artifacts, then publish manually.

---

#### 2. Credential Management
**Risk: Critical - Security vulnerabilities**

Never ask Claude Code to:
- Generate real API tokens
- Modify credential files directly
- Display stored credentials
- Test with production tokens

**Why:** Credentials must be protected from exposure.

**Instead:** Use Claude Code to improve credential handling code, test with dummy tokens.

---

#### 3. Breaking API Changes
**Risk: High - Client compatibility**

Exercise extreme caution with:
- Changing public method signatures
- Removing existing resource classes
- Modifying query DSL behavior
- Changing CLI command interfaces

**Why:** Breaking changes affect all users.

**Instead:** Deprecate old APIs, add new ones, maintain backward compatibility.

---

#### 4. Live API Testing Without Approval
**Risk: Medium - API rate limits/costs**

Be careful when:
- Running bulk operations against live API
- Creating many test resources
- Executing long-running imports
- Testing deletion operations

**Why:** Can consume API quota and affect service.

**Instead:** Use test environment, request approval for load testing.

---

### ⚠️ Use With Caution:

#### Resource Refactoring
**Risk: Medium - Backward compatibility**

When refactoring resources:
- Ensure mixin behavior is preserved
- Test all resource methods work
- Check type registry updates
- Verify URL construction
- Run full integration test suite

#### Query DSL Changes
**Risk: Medium - Query behavior**

When modifying query logic:
- Test with various filter combinations
- Verify pagination still works
- Check lazy evaluation behavior
- Test with large result sets
- Ensure backward compatibility

#### CLI Command Changes
**Risk: Medium - User workflows**

When modifying CLI commands:
- Preserve existing argument behavior
- Add new options, don't change existing
- Maintain output format
- Update help text
- Test with real workflows

---

## Limitations

### Areas Requiring Human Review

#### 1. Architecture Decisions
**Claude Code can suggest, but humans should decide:**
- Choosing mixin combinations for resources
- Deciding on query DSL extensions
- Planning CLI command structure
- Selecting authentication strategies

**Approach:** Use Claude Code to analyze options and trade-offs, then make informed decision.

---

#### 2. API Compatibility
**Claude Code needs clear specifications:**
- How API responses are structured
- What fields are required vs optional
- Pagination behavior
- Error response formats

**Approach:** Provide API documentation or examples, review generated code against API.

---

#### 3. Integration Testing
**Some issues require live API debugging:**
- Authentication edge cases
- Rate limiting behavior
- Large dataset queries
- Network timeout scenarios

**Approach:** Use Claude Code for code analysis, combine with manual API testing.

---

#### 4. Python Version Compatibility
**Claude Code may not catch all version issues:**
- Subtle syntax differences
- Standard library changes
- Dependency compatibility
- Type hint variations

**Approach:** Use tox to test across Python 3.8-3.13, review errors.

---

#### 5. Package Distribution
**Release process requires careful steps:**
- Version bumping strategy
- Changelog generation accuracy
- Package metadata correctness
- Wheel/sdist building

**Approach:** Have Claude Code prepare, human verifies before publishing.

---

## Real-World Examples

### Example 1: Adding New Resource

**Task:** Add DatasetVersion resource with list and create operations

**Workflow:**
1. "Read the Dataset resource class to understand the mixin pattern"
2. "Create a DatasetVersion resource with ListableAPIResource and CreateableAPIResource mixins"
3. "Set RESOURCE_VERSION = 2 and register in resource/__init__.py types dict"
4. "Add a restore() method that POSTs to instance_url() + '/restore/'"
5. "Write integration tests using QuartzBioTestCase"
6. "Run tests with live API credentials"
7. **Human Review:** Test with various API scenarios, verify URL construction

**Time Saved:** ~1.5 hours
**Risk Level:** Low

---

### Example 2: Debugging Query Pagination

**Task:** Query iteration stops after first page

**Workflow:**
1. "Show me how pagination works in the Query class"
2. "The query is not fetching additional pages. Check the __iter__ and _fetch_page methods"
3. "I see the issue - _next_url is not being updated. Fix the pagination logic"
4. "Write a test that verifies multi-page iteration works correctly"
5. "Run the test and verify it passes"
6. **Human Review:** Test with large result sets, verify memory usage

**Time Saved:** ~1 hour
**Risk Level:** Low

---

### Example 3: Adding CLI Export Command

**Task:** Add 'quartzbio export' command for dataset export

**Workflow:**
1. "Read the 'quartzbio import' command to understand the CLI pattern"
2. "Design a 'quartzbio export' command with dataset-id, output-file, and format arguments"
3. "Add to subcommands dict in cli/main.py with proper argument specs"
4. "Implement export logic with query iteration and file writing"
5. "Add progress bar using pyprind"
6. "Test the command with a small dataset"
7. **Human Review:** Test with large datasets, verify output formats, check error handling

**Time Saved:** ~2 hours
**Risk Level:** Medium (affects user workflow)

---

### Example 4: Fixing Credential Resolution

**Task:** Credentials not loading from ~/.quartzbio/credentials

**Workflow:**
1. "Show me the credential resolution logic in auth.py"
2. "The client says 'No token found' but the credential file exists. Trace the lookup order"
3. "Check the netrc parsing in cli/credentials.py"
4. "I found the issue - the host matching is case-sensitive. Fix it"
5. "Add tests for credential resolution from all sources"
6. **Human Review:** Test on multiple OS (Linux, Mac, Windows), verify file permissions

**Time Saved:** ~45 minutes
**Risk Level:** Medium (affects authentication)

---

### Example 5: Performance Optimization

**Task:** Query iteration is slow for large result sets

**Workflow:**
1. "Profile the Query iteration for performance bottlenecks"
2. "Found: excessive type conversion on every item. Optimize convert_to_quartzbio_object()"
3. "Cache type registry lookups to reduce dict access"
4. "Add lazy conversion - only convert accessed attributes"
5. "Benchmark before/after with 10K record query"
6. "Write tests to ensure correctness"
7. **Human Review:** Profile with real workloads, verify memory usage, check edge cases

**Time Saved:** ~3 hours
**Risk Level:** Medium (affects core functionality)

---

## Best Practices Summary

### ✅ Do:
- Use Claude Code for resource boilerplate and test writing
- Start with reading existing code before making changes
- Run integration tests after every code change
- Ask for explanations of the mixin architecture
- Request multiple implementation options
- Provide API examples when adding features

### ❌ Don't:
- Publish to PyPI without human review
- Test with production credentials
- Make breaking changes without deprecation
- Skip integration testing with live API
- Assume Claude knows specific API behavior
- Modify authentication without security review

### ⚡ Pro Tips:
- Iterate: Start simple, refine, optimize
- Test frequently: Catch issues early with live API
- Provide examples: Show Claude similar patterns in codebase
- Be specific: Reference files, classes, methods
- Ask "why": Understand design decisions
- Use tox: Test across Python versions

---

## Measuring Success

Track these metrics to evaluate Claude Code effectiveness:

- **Time saved per task** (compare with manual implementation)
- **Code quality** (fewer bugs, better test coverage)
- **Integration test pass rate** (improved with Claude assistance)
- **Documentation completeness** (docstrings, examples)
- **Developer onboarding time** (faster with Claude explanations)

---

## Feedback and Iteration

As you use Claude Code with QuartzBio Python client:
1. Document what works well (add to Quick Wins)
2. Track issues and limitations (update Guardrails)
3. Share effective prompts with team (add to CLAUDE_PROMPTING_GUIDE.md)
4. Refine workflows based on usage
5. Update this document quarterly

---

## Getting Started

**New to Claude Code?** Start with these safe, high-value tasks:
1. "Explain the mixin-based resource architecture"
2. "Write tests for the GenomicFilter class"
3. "Fix flake8 violations in quartzbio/query.py"
4. "Add docstrings to quartzbio/client.py public methods"

**Ready for more?** Try:
1. "Add a new DatasetTemplate resource"
2. "Implement a query result caching feature"
3. "Add a --json output option to CLI commands"
4. "Optimize query iteration for large result sets"

---

**Questions or suggestions?** Update this document or discuss with the team.
