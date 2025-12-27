# Installation Guide

This guide will help you install StxScript and get your development environment set up.

## Requirements

- Python 3.10 or higher
- uv (recommended) or pip for package management

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

# Install with uv (recommended for development)
uv venv && uv pip install -e ".[dev]"

# Or install with pip
pip install -e ".[dev]"
```

## Verify Installation

After installation, verify that StxScript is working correctly:

```bash
# Check the version
stxscript --version

# Should output: StxScript 0.3.0 (Phase 10: Ecosystem & Tooling)

# Test basic transpilation
echo 'let test: uint = 42u;' | stxscript build -
```

You should see output similar to:
```lisp
(define-data-var test uint u42)
```

## Development Setup

If you're planning to contribute to StxScript, set up the development environment:

### 1. Install uv

```bash
# Install uv (fast Python package installer)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup

```bash
git clone https://github.com/cryptuon/stxscript.git
cd stxscript
uv venv && uv pip install -e ".[dev]"
```

### 3. Run Tests

```bash
# Run the test suite
uv run python -m pytest tests/

# Run with coverage
uv run python -m pytest tests/ --cov=stxscript

# Run specific test
uv run python -m pytest tests/test_transpiler.py -v

# Run linting
uv run flake8 stxscript
uv run mypy stxscript
```

## IDE Setup

### VS Code (Recommended)

Install the StxScript VS Code extension for the best development experience:

1. Install the extension from the `vscode-extension/` directory
2. The extension provides:
   - Syntax highlighting for `.stx` files
   - Real-time error reporting
   - Autocomplete for keywords, types, and symbols
   - Go to definition
   - Hover information
   - Code snippets

**To install the extension locally:**

```bash
cd vscode-extension
npm install
npm run compile
# Then open the extension folder in VS Code and press F5 to run
```

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
├── stxscript.toml        # Package manifest
└── stxscript.lock        # Lock file
```

## Initialize a New Project

Use the package manager to initialize a new project:

```bash
# Initialize a new StxScript project
stxscript pkg init --name my-project

# Or create from a template
stxscript new my-project --template token
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
# Make sure all dependencies are installed
uv pip install -e ".[dev]"
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
