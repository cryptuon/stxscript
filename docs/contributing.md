# Contributing to StxScript

Thank you for your interest in contributing to StxScript! We welcome contributions from the community and are grateful for any help you can provide.

## 🚀 Quick Start for Contributors

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Set up** the development environment
4. **Make** your changes
5. **Test** your changes
6. **Submit** a pull request

## 📋 Development Setup

### Prerequisites

- Python 3.7+
- Poetry (recommended) or pip
- Git

### Setting Up Your Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/stxscript.git
cd stxscript

# Add upstream remote
git remote add upstream https://github.com/cryptuon/stxscript.git

# Install dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell

# Or with pip
pip install -e .
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
poetry run python -m pytest

# Run specific test file
poetry run python -m unittest stxscript.test_transpiler

# Run with coverage
poetry run pytest --cov=stxscript

# Run linting
poetry run flake8 stxscript
poetry run mypy stxscript
```

## 🎯 Ways to Contribute

### 1. Bug Reports

If you find a bug, please create an issue with:

- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, StxScript version)
- **Code samples** that demonstrate the issue

**Bug Report Template:**
```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Create file with content '...'
2. Run command '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.9.0]
- StxScript: [e.g. 0.1.0]

**Additional Context**
Any other context about the problem.
```

### 2. Feature Requests

For new features, please:

- **Check existing issues** to avoid duplicates
- **Describe the feature** and its use case
- **Provide examples** of how it would work
- **Consider implementation** complexity

### 3. Code Contributions

#### Language Features

Help expand StxScript's language support:

- **Expressions**: Arithmetic, logical, comparison operators
- **Control Flow**: If/else statements, loops, match expressions
- **Data Structures**: Lists, tuples, maps, optionals
- **Functions**: Lambda expressions, higher-order functions
- **Types**: Union types, generic types, type inference improvements

#### Infrastructure

- **Testing**: Add more test cases, improve test coverage
- **Documentation**: Improve docs, add examples
- **Performance**: Optimize parsing, transpilation speed
- **Tooling**: IDE support, debugging tools, formatter

#### Grammar Improvements

The grammar files are in `stxscript/`:
- `working_grammar.lark` - Current simplified grammar
- `grammar.lark` - Original complex grammar (has conflicts)
- `simple_grammar.lark` - Alternative grammar approach

## 📝 Development Guidelines

### Code Style

We follow Python PEP 8 with some modifications:

```python
# Use descriptive variable names
def transpile_variable_declaration(items):
    variable_name, variable_type, initial_value = items
    return f"(define-data-var {variable_name} {variable_type} {initial_value})"

# Add type hints
def transform_type(self, type_annotation: str) -> str:
    """Transform StxScript type to Clarity type."""
    return type_annotation

# Use docstrings for classes and public methods
class StxScriptTranspiler:
    """Transpiles StxScript code to Clarity."""

    def transpile(self, stxscript: str) -> str:
        """Transpile StxScript source code to Clarity.

        Args:
            stxscript: The StxScript source code

        Returns:
            Generated Clarity code

        Raises:
            ValueError: If the code contains errors
        """
```

### Git Workflow

1. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Make commits** with clear messages:
   ```bash
   git commit -m "Add support for if/else statements

   - Implement if_statement grammar rule
   - Add transformer for conditional logic
   - Include tests for nested conditions"
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

<optional footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

**Examples:**
- `feat: add support for while loops`
- `fix: handle empty function bodies correctly`
- `docs: update API documentation with new examples`
- `test: add tests for type inference`

### Testing Guidelines

#### Writing Tests

```python
import unittest
from stxscript import StxScriptTranspiler

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_feature_basic_case(self):
        """Test basic functionality of the new feature."""
        stx_code = "your test code here"
        expected = "expected clarity output"
        result = self.transpiler.transpile(stx_code)
        self.assertEqual(result.strip(), expected.strip())

    def test_feature_edge_case(self):
        """Test edge cases and error conditions."""
        with self.assertRaises(ValueError):
            self.transpiler.transpile("invalid code")
```

#### Test Categories

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test complete transpilation workflow
- **Grammar Tests**: Test parsing of language constructs
- **Error Tests**: Test error handling and reporting

### Documentation

When adding new features:

1. **Update the grammar file** with clear comments
2. **Add transformer methods** with docstrings
3. **Include examples** in `docs/examples.md`
4. **Update language reference** in `docs/language-reference.md`
5. **Add API documentation** if needed

## 🔧 Working with the Grammar

### Understanding the Grammar Files

StxScript uses [Lark](https://lark-parser.readthedocs.io/) for parsing:

```lark
// Grammar rules use lowercase
variable_declaration: "let" IDENTIFIER ":" type "=" expression ";"

// Tokens use UPPERCASE
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
```

### Adding New Language Features

1. **Add grammar rules**:
   ```lark
   // Add to working_grammar.lark
   if_statement: "if" "(" expression ")" block ["else" block]
   ```

2. **Add transformer methods**:
   ```python
   def if_statement(self, items):
       condition, true_block, false_block = items
       if false_block:
           return f"(if {condition}\n  {true_block}\n  {false_block})"
       else:
           return f"(if {condition}\n  {true_block}\n  false)"
   ```

3. **Add tests**:
   ```python
   def test_if_statement(self):
       stx_code = 'if (x > 0) { let y = 1; }'
       expected = '(if (> x 0)\n  (define-data-var y unknown 1)\n  false)'
       self.assert_transpiles_to(stx_code, expected)
   ```

### Debugging Grammar Issues

```bash
# Test grammar parsing
poetry run python -c "
from stxscript import StxScriptTranspiler
t = StxScriptTranspiler()
tree = t.parser.parse('your test code')
print(tree.pretty())
"
```

## 📊 Project Structure

```
stxscript/
├── stxscript/              # Main package
│   ├── __init__.py         # Package exports
│   ├── transpiler.py       # Main transpiler class
│   ├── working_grammar.lark # Current grammar
│   ├── ast_nodes.py        # AST node definitions
│   ├── semantic_analyzer.py # Semantic analysis
│   └── test_transpiler.py  # Test suite
├── docs/                   # Documentation
├── examples/               # Example contracts
├── README.md              # Project overview
├── pyproject.toml         # Dependencies and config
└── LICENSE               # License file
```

## 🏁 Pull Request Process

### Before Submitting

1. **Run all tests** and ensure they pass
2. **Add tests** for new functionality
3. **Update documentation** as needed
4. **Check code style** with linting tools
5. **Test manually** with example contracts

### PR Checklist

- [ ] Tests pass (`poetry run pytest`)
- [ ] Linting passes (`poetry run flake8`)
- [ ] Type checking passes (`poetry run mypy`)
- [ ] Documentation updated
- [ ] Examples added if applicable
- [ ] CHANGELOG updated (for significant changes)

### PR Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Changes Made
- List specific changes
- Include any breaking changes

## Testing
- [ ] Added new tests
- [ ] All tests pass
- [ ] Manual testing completed

## Related Issues
Closes #issue_number
```

## 🎖️ Recognition

Contributors will be:
- **Added to CONTRIBUTORS.md**
- **Mentioned in release notes**
- **Given credit in documentation**

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Discord/Slack**: [Link if available]

## 📄 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our Code of Conduct.

### Our Standards

- **Be respectful** and inclusive
- **Be collaborative** and helpful
- **Focus on what's best** for the community
- **Show empathy** towards other contributors

## 🏷️ License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to StxScript! Your efforts help make blockchain development more accessible to everyone.