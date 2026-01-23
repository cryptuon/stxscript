# Contributing

Thank you for your interest in contributing to StxScript.

## Development Setup

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git

### Getting Started

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/stxscript.git
cd stxscript

# Add upstream remote
git remote add upstream https://github.com/cryptuon/stxscript.git

# Install dependencies
uv venv && uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests (146 tests)
uv run python -m pytest tests/

# Run with coverage
uv run python -m pytest tests/ --cov=stxscript

# Run specific test file
uv run python -m pytest tests/test_transpiler.py -v
```

### Code Quality

```bash
uv run black stxscript/
uv run flake8 stxscript/
uv run mypy stxscript/
```

## Ways to Contribute

### Bug Reports

Create an issue with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, StxScript version)
- Code samples that demonstrate the issue

### Feature Requests

- Check existing issues to avoid duplicates
- Describe the feature and its use case
- Provide examples of how it would work

### Code Contributions

Areas where contributions are welcome:

- **Language Features**: New syntax, operators, types
- **Testing**: Additional test cases, improved coverage
- **Documentation**: Improve docs, add examples
- **Performance**: Optimize parsing, transpilation
- **Tooling**: IDE support, formatting, linting rules

## Development Guidelines

### Code Style

We use Black for formatting and follow PEP 8 with type hints:

```python
def transform_type(self, type_annotation: str) -> str:
    """Transform StxScript type to Clarity type."""
    return type_annotation
```

### Git Workflow

1. Create a branch:
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. Make commits with clear messages:
   ```bash
   git commit -m "feat: add support for buffer sizes"
   ```

3. Keep your branch updated:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

4. Push and create a PR:
   ```bash
   git push origin feature/new-feature-name
   ```

### Commit Message Format

```
<type>: <description>
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

### Adding New Language Features

1. Add grammar rules to `stxscript/working_grammar.lark`
2. Add AST nodes to `stxscript/ast_nodes.py`
3. Update the AST builder in `stxscript/ast_builder.py`
4. Add semantic checks in `stxscript/semantic_analyzer.py`
5. Add code generation in `stxscript/clarity_generator.py`
6. Add tests in `tests/`

### Testing Guidelines

```python
import unittest
from stxscript import StxScriptTranspiler

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_feature_basic_case(self):
        stx_code = "your test code here"
        expected = "expected clarity output"
        result = self.transpiler.transpile(stx_code)
        self.assertIn(expected, result)
```

## Project Structure

```
stxscript/
├── stxscript/               # Main package
│   ├── transpiler.py        # Main transpiler class
│   ├── working_grammar.lark # Production grammar
│   ├── ast_nodes.py         # AST node definitions
│   ├── ast_builder.py       # Parse tree to AST
│   ├── semantic_analyzer.py # Type checking and validation
│   ├── clarity_generator.py # Clarity code generation
│   ├── cli.py               # CLI interface
│   ├── formatter.py         # Code formatter
│   ├── linter.py            # Static analysis
│   ├── lsp_server.py        # Language server
│   ├── testing.py           # Testing framework
│   └── package_manager.py   # Package management
├── tests/                   # Test suite
├── documentation/           # User-facing docs (mkdocs)
├── docs/                    # Additional documentation
├── vscode-extension/        # VS Code extension
└── pyproject.toml           # Project configuration
```

## PR Checklist

Before submitting:

- [ ] Tests pass: `uv run python -m pytest tests/`
- [ ] Linting passes: `uv run flake8 stxscript/`
- [ ] Documentation updated if applicable
- [ ] New tests added for new functionality

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
