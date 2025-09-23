# Installation Guide

This guide will help you install StxScript and get your development environment set up.

## Requirements

- Python 3.7 or higher
- pip or Poetry (for package management)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install stxscript
```

This installs the latest stable release of StxScript from the Python Package Index.

### Method 2: Install from Source (Development)

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/cryptuon/stxscript.git
cd stxscript

# Install with Poetry (recommended for development)
poetry install
poetry shell

# Or install with pip
pip install -e .
```

## Verify Installation

After installation, verify that StxScript is working correctly:

```bash
# Check the version
stxscript --version

# Test basic transpilation
echo 'let test: uint = 42u;' | stxscript
```

You should see output similar to:
```
(define-data-var test uint u42)
```

## Development Setup

If you're planning to contribute to StxScript, set up the development environment:

### 1. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Clone and Setup

```bash
git clone https://github.com/cryptuon/stxscript.git
cd stxscript
poetry install
poetry shell
```

### 3. Install Development Dependencies

```bash
poetry install --extras dev
```

### 4. Run Tests

```bash
# Run the test suite
poetry run python -m pytest

# Run specific test
poetry run python -m unittest stxscript.test_transpiler

# Run linting
poetry run flake8 stxscript
poetry run mypy stxscript
```

## IDE Setup

### VS Code

Install the following extensions for better StxScript development:

1. **Python** - Microsoft's Python extension
2. **Clarity** - Stacks blockchain Clarity language support

### Vim/Neovim

Add syntax highlighting for `.stx` files by adding to your config:

```vim
autocmd BufNewFile,BufRead *.stx set filetype=typescript
```

## Project Structure

When working with StxScript projects, we recommend this structure:

```
my-stacks-project/
├── src/
│   ├── contracts/
│   │   ├── main.stx
│   │   └── token.stx
│   └── lib/
│       └── utils.stx
├── build/
│   └── contracts/
├── tests/
└── stxscript.config.json
```

## Environment Variables

StxScript respects these environment variables:

- `STXSCRIPT_DEBUG` - Enable debug logging
- `STXSCRIPT_OUTPUT_DIR` - Default output directory
- `STXSCRIPT_CONFIG` - Path to configuration file

## Troubleshooting

### Common Issues

**ImportError: No module named 'lark'**
```bash
# Make sure lark is installed
pip install lark
```

**Command not found: stxscript**
```bash
# Check if the install location is in PATH
pip show stxscript

# Or use python module syntax
python -m stxscript
```

**Permission denied**
```bash
# Install in user directory
pip install --user stxscript
```

### Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/cryptuon/stxscript/issues)
2. Look through existing documentation
3. Create a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - StxScript version (`stxscript --version`)
   - Complete error message

## Next Steps

- [Quick Start Guide](quick-start.md) - Get started with your first StxScript contract
- [Language Reference](language-reference.md) - Learn the StxScript syntax
- [Examples](examples.md) - See real-world examples