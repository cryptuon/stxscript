# CLI Reference

The StxScript command-line interface provides comprehensive tools for transpiling, testing, and managing StxScript projects.

## Installation

The CLI is automatically available after installing StxScript:

```bash
pip install stxscript
```

## Quick Reference

```bash
stxscript build <input> [output]   # Transpile to Clarity
stxscript fmt <files>              # Format code
stxscript lint <files>             # Static analysis
stxscript check <files>            # Syntax validation
stxscript new <name>               # Create new project
stxscript watch <path>             # Watch mode
stxscript doc <input>              # Generate docs
stxscript test [path]              # Run tests
stxscript pkg <command>            # Package management
```

## Commands

### build - Transpile StxScript to Clarity

```bash
stxscript build <input> [output]

# Examples
stxscript build contract.stx                    # Output to stdout
stxscript build contract.stx contract.clar      # Output to file
stxscript build src/                            # Transpile directory
stxscript build - output.clar                   # Read from stdin

# Options
--check         Check syntax only, don't generate output
--optimize      Enable code optimizations
-v, --verbose   Verbose output
```

### fmt - Format Code

```bash
stxscript fmt <files>

# Examples
stxscript fmt contract.stx           # Format single file
stxscript fmt src/                   # Format directory
stxscript fmt *.stx                  # Format with glob

# Options
--check         Check if files are formatted (exit 1 if not)
--diff          Show diff of formatting changes
--config FILE   Path to formatter config file
```

### lint - Static Analysis

```bash
stxscript lint <files>

# Examples
stxscript lint contract.stx          # Lint single file
stxscript lint src/                  # Lint directory

# Options
--fix           Automatically fix issues where possible
--config FILE   Path to linter config file
--format FORMAT Output format (text or json)
```

### check - Syntax Validation

```bash
stxscript check <files>

# Examples
stxscript check contract.stx         # Check single file
stxscript check src/                 # Check directory
```

### new - Create New Project

```bash
stxscript new <name>

# Examples
stxscript new my-project             # Create with basic template
stxscript new my-token --template token    # Use token template
stxscript new my-nft --template nft        # Use NFT template

# Options
--template TYPE  Template to use (basic, nft, token, defi)
--path DIR       Directory to create project in
```

### watch - Development Mode

```bash
stxscript watch [path]

# Examples
stxscript watch                      # Watch current directory
stxscript watch src/                 # Watch specific directory

# Options
--output DIR     Output directory for transpiled files
--ignore PATTERN Patterns to ignore (can repeat)
```

### doc - Generate Documentation

```bash
stxscript doc <input>

# Examples
stxscript doc contract.stx           # Generate docs for file
stxscript doc src/                   # Generate docs for directory

# Options
--output DIR     Output directory (default: docs/)
--format FORMAT  Output format (html or markdown)
```

### test - Run Contract Tests

```bash
stxscript test [path]

# Examples
stxscript test                       # Run tests in tests/
stxscript test tests/                # Specify test directory
stxscript test tests/test_token.py   # Run specific test file

# Options
--pattern PATTERN  Test file pattern (default: test_*.py)
--coverage         Enable coverage tracking
--json             Output results as JSON
```

### pkg - Package Management

```bash
stxscript pkg <command>

# Initialize a new package
stxscript pkg init
stxscript pkg init --name my-package

# Add a dependency
stxscript pkg add some-package
stxscript pkg add some-package --version "^1.0.0"
stxscript pkg add some-package --dev    # Add as dev dependency

# Remove a dependency
stxscript pkg remove some-package
stxscript pkg remove some-package --dev

# Install all dependencies
stxscript pkg install

# List installed packages
stxscript pkg list
```

## Global Options

These options work with all commands:

```bash
--version       Show version information
--verbose, -v   Enable verbose output
--help, -h      Show help message
```

## Examples

### Basic File Transpilation

```bash
# Create a simple contract
cat > token.stx << 'EOF'
const TOKEN_NAME: string = "MyToken";
let total_supply: uint = 1000u;

@public
function get_name(): Response<string, uint> {
    return ok(TOKEN_NAME);
}
EOF

# Transpile to Clarity
stxscript build token.stx token.clar

# Check the output
cat token.clar
```

### Development Workflow

```bash
# Create a new project
stxscript new my-token --template token

# Navigate to project
cd my-token

# Start watch mode for development
stxscript watch src/ --output build/

# In another terminal, run tests
stxscript test
```

### CI/CD Integration

```bash
# Check syntax only
stxscript check src/

# Lint code
stxscript lint src/

# Ensure formatting
stxscript fmt --check src/

# Build all contracts
stxscript build src/ build/
```

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (syntax, file not found, etc.) |
| 130 | Interrupted by user (Ctrl+C) |

## Integration Examples

### Makefile Integration

```makefile
CONTRACTS_DIR = src
BUILD_DIR = build

.PHONY: all build check lint fmt test clean

all: check lint build

build:
	stxscript build $(CONTRACTS_DIR) $(BUILD_DIR)

check:
	stxscript check $(CONTRACTS_DIR)

lint:
	stxscript lint $(CONTRACTS_DIR)

fmt:
	stxscript fmt $(CONTRACTS_DIR)

test:
	stxscript test

clean:
	rm -rf $(BUILD_DIR)
```

### GitHub Actions Workflow

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install StxScript
      run: pip install stxscript

    - name: Check syntax
      run: stxscript check src/

    - name: Lint
      run: stxscript lint src/

    - name: Build
      run: stxscript build src/ build/

    - name: Test
      run: stxscript test
```

### Package.json Scripts

```json
{
  "scripts": {
    "build": "stxscript build src/ build/",
    "check": "stxscript check src/",
    "lint": "stxscript lint src/",
    "fmt": "stxscript fmt src/",
    "test": "stxscript test",
    "watch": "stxscript watch src/ --output build/"
  }
}
```

## Configuration

### Package Manifest (stxscript.toml)

```toml
[package]
name = "my-stxscript-project"
version = "0.1.0"
description = "A StxScript project"
authors = ["Your Name <your.email@example.com>"]
license = "MIT"

[dependencies]
# Add your dependencies here
# example = "^1.0.0"

[dev-dependencies]
# Add development dependencies here
```

## See Also

- [Quick Start Guide](quick-start.md) - Get started quickly
- [API Documentation](api.md) - Python API reference
- [Examples](examples.md) - Code examples and patterns
