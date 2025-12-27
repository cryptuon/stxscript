# Contributing to StxScript

Thank you for your interest in contributing to StxScript! We welcome contributions from the community.

## Quick Start for Contributors

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Set up** the development environment
4. **Make** your changes
5. **Test** your changes
6. **Submit** a pull request

## Development Setup

### Prerequisites

- Python 3.10+
- uv (recommended) or pip
- Git

### Setting Up Your Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/stxscript.git
cd stxscript

# Add upstream remote
git remote add upstream https://github.com/cryptuon/stxscript.git

# Install dependencies with uv
uv venv && uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests (146 tests)
uv run python -m pytest tests/

# Run with coverage
uv run python -m pytest tests/ --cov=stxscript

# Run specific test file
uv run python -m pytest tests/test_transpiler.py -v

# Run linting
uv run flake8 stxscript
uv run mypy stxscript
```

## Ways to Contribute

### 1. Bug Reports

If you find a bug, please create an issue with:

- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, StxScript version)
- **Code samples** that demonstrate the issue

### 2. Feature Requests

For new features, please:

- **Check existing issues** to avoid duplicates
- **Describe the feature** and its use case
- **Provide examples** of how it would work

### 3. Code Contributions

#### Areas to Contribute

- **Language Features**: New syntax, operators, types
- **Testing**: Add test cases, improve coverage
- **Documentation**: Improve docs, add examples
- **Performance**: Optimize parsing, transpilation
- **Tooling**: IDE support, formatting, linting

## Development Guidelines

### Code Style

We follow Python PEP 8 with type hints:

```python
def transform_type(self, type_annotation: str) -> str:
    """Transform StxScript type to Clarity type."""
    return type_annotation

class StxScriptTranspiler:
    """Transpiles StxScript code to Clarity."""

    def transpile(self, stxscript: str) -> str:
        """Transpile StxScript source code to Clarity.

        Args:
            stxscript: The StxScript source code

        Returns:
            Generated Clarity code
        """
```

### Git Workflow

1. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Make commits** with clear messages:
   ```bash
   git commit -m "feat: add support for buffer sizes

   - Implement buffer<N> syntax
   - Add tests for sized buffers
   - Update documentation"
   ```

3. **Keep your branch updated**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/new-feature-name
   ```

### Commit Message Format

```
<type>: <description>

<optional body>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

### Testing Guidelines

```python
import unittest
from stxscript import StxScriptTranspiler

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_feature_basic_case(self):
        """Test basic functionality."""
        stx_code = "your test code here"
        expected = "expected clarity output"
        result = self.transpiler.transpile(stx_code)
        self.assertIn(expected, result)
```

## Project Structure

```
stxscript/
├── stxscript/              # Main package
│   ├── __init__.py         # Package exports
│   ├── transpiler.py       # Main transpiler class
│   ├── working_grammar.lark # Current grammar
│   ├── ast_nodes.py        # AST node definitions
│   ├── ast_builder.py      # Parse tree to AST
│   ├── semantic_analyzer.py # Type checking
│   ├── clarity_generator.py # Code generation
│   ├── cli.py              # CLI interface
│   ├── lsp_server.py       # Language server
│   ├── testing.py          # Testing framework
│   └── package_manager.py  # Package management
├── vscode-extension/       # VS Code extension
├── docs/                   # Documentation
├── tests/                  # Test suite
└── pyproject.toml          # Project config
```

## Working with the Grammar

### Understanding the Grammar Files

StxScript uses [Lark](https://lark-parser.readthedocs.io/) for parsing:

```lark
// Grammar rules use lowercase
variable_declaration: "let" IDENTIFIER ":" type "=" expression ";"

// Tokens use UPPERCASE
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
```

### Adding New Language Features

1. **Add grammar rules** to `working_grammar.lark`
2. **Add AST nodes** to `ast_nodes.py`
3. **Update AST builder** in `ast_builder.py`
4. **Add semantic checks** in `semantic_analyzer.py`
5. **Add code generation** in `clarity_generator.py`
6. **Add tests** in `tests/`

## Pull Request Process

### Before Submitting

1. **Run all tests** and ensure they pass
2. **Add tests** for new functionality
3. **Update documentation** as needed
4. **Check code style** with linting tools

### PR Checklist

- [ ] Tests pass (`uv run python -m pytest tests/`)
- [ ] Linting passes (`uv run flake8 stxscript`)
- [ ] Documentation updated
- [ ] Examples added if applicable

## Recognition

Contributors will be:
- **Added to CONTRIBUTORS.md**
- **Mentioned in release notes**
- **Given credit in documentation**

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to StxScript!
