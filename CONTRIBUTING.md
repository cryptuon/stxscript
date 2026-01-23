# Contributing to StxScript

Thank you for your interest in contributing to StxScript. This document provides guidelines and information for contributors.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git

### Development Setup

```bash
git clone https://github.com/cryptuon/stxscript.git
cd stxscript
uv venv && uv pip install -e ".[dev]"
```

### Running Tests

```bash
# All tests (146 tests)
uv run python -m pytest tests/

# With coverage
uv run python -m pytest tests/ --cov=stxscript

# Specific test file
uv run python -m pytest tests/test_transpiler.py -v
```

### Code Quality

```bash
uv run black stxscript/       # Format
uv run flake8 stxscript/      # Lint
uv run mypy stxscript/        # Type check
```

## How to Contribute

### Reporting Bugs

Open an issue with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- StxScript version (`stxscript --version`)
- Python version and OS

### Suggesting Features

Open an issue with:

- Description of the feature
- Use case and motivation
- Example of how it would work (StxScript input and expected Clarity output)

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Add or update tests
5. Ensure all tests pass: `uv run python -m pytest tests/`
6. Ensure code is formatted: `uv run black stxscript/`
7. Commit with a clear message
8. Push and open a pull request

### Commit Messages

Use conventional commit format:

```
<type>: <description>

[optional body]
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `test` - Adding or updating tests
- `refactor` - Code refactoring
- `style` - Code style/formatting
- `chore` - Maintenance tasks

Examples:
```
feat: add buffer size validation to type checker
fix: correct kebab-case conversion for multi-word identifiers
docs: update CLI reference with new pkg commands
test: add property-based tests for expression parsing
```

## Development Guide

### Project Structure

```
stxscript/
├── stxscript/               # Main package
│   ├── transpiler.py        # Transpilation orchestrator
│   ├── working_grammar.lark # Production grammar (Lark LALR)
│   ├── ast_nodes.py         # AST node definitions
│   ├── ast_builder.py       # Parse tree → AST transformer
│   ├── semantic_analyzer.py # Type checking and validation
│   ├── clarity_generator.py # AST → Clarity code generation
│   ├── error_handler.py     # Error reporting with suggestions
│   ├── cli.py               # CLI with subcommands
│   ├── formatter.py         # Code formatter
│   ├── linter.py            # Static analysis
│   ├── lsp_server.py        # Language Server Protocol
│   ├── testing.py           # Contract testing framework
│   └── package_manager.py   # Dependency management
├── tests/                   # Test suite
├── documentation/           # User-facing docs (mkdocs)
└── vscode-extension/        # VS Code extension
```

### Adding a Language Feature

1. **Grammar**: Add rules to `stxscript/working_grammar.lark`
2. **AST Nodes**: Define nodes in `stxscript/ast_nodes.py`
3. **AST Builder**: Add transformer methods in `stxscript/ast_builder.py`
4. **Semantic Analysis**: Add checks in `stxscript/semantic_analyzer.py`
5. **Code Generation**: Add generation in `stxscript/clarity_generator.py`
6. **Tests**: Add test cases in `tests/`

### Testing Guidelines

- Test both successful transpilation and error cases
- Include the expected Clarity output in assertions
- Use descriptive test method names: `test_for_loop_range_extraction`
- Add property-based tests for parser robustness when appropriate

```python
import unittest
from stxscript import StxScriptTranspiler

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_feature_produces_correct_clarity(self):
        stx_code = 'let x: uint = 42u;'
        result = self.transpiler.transpile(stx_code)
        self.assertIn('(define-data-var x uint u42)', result)
```

### Code Style

- Follow PEP 8
- Use type hints for function signatures
- Use Black for formatting (line length 100)
- Keep functions focused and testable

## Pull Request Checklist

Before submitting:

- [ ] Tests pass: `uv run python -m pytest tests/`
- [ ] Code formatted: `uv run black stxscript/`
- [ ] Linting passes: `uv run flake8 stxscript/`
- [ ] New tests added for new functionality
- [ ] Documentation updated if applicable
- [ ] Commit messages follow conventional format

## License

By contributing to StxScript, you agree that your contributions will be licensed under the [MIT License](LICENSE).
