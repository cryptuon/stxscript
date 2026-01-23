# CLI Reference

Complete reference for StxScript command-line tools.

## Installation

```bash
pip install stxscript
```

## Commands Overview

```bash
stxscript build <input> [output]   # Transpile to Clarity
stxscript fmt <files>              # Format code
stxscript lint <files>             # Static analysis
stxscript check <files>            # Syntax validation
stxscript new <name>               # Create project
stxscript watch <path>             # Watch mode
stxscript doc <input>              # Generate docs
stxscript test [path]              # Run tests
stxscript pkg <command>            # Package management
```

## build

Transpile StxScript to Clarity.

```bash
stxscript build <input> [output]

# Examples
stxscript build contract.stx                    # Output to stdout
stxscript build contract.stx contract.clar      # Output to file
stxscript build src/                            # Transpile directory

# Options
--check         Syntax check only
--optimize      Enable optimizations
-v, --verbose   Verbose output
```

## fmt

Format StxScript code.

```bash
stxscript fmt <files>

# Examples
stxscript fmt contract.stx           # Format file
stxscript fmt src/                   # Format directory
stxscript fmt --check src/           # Check formatting

# Options
--check         Check only (exit 1 if unformatted)
--diff          Show diff of changes
```

## lint

Run static analysis.

```bash
stxscript lint <files>

# Examples
stxscript lint contract.stx
stxscript lint src/

# Options
--fix           Auto-fix issues
--format FORMAT Output format (text/json)
```

## check

Validate syntax without generating output.

```bash
stxscript check <files>

# Examples
stxscript check contract.stx
stxscript check src/
```

## new

Create a new project.

```bash
stxscript new <name>

# Examples
stxscript new my-project                     # Basic template
stxscript new my-token --template token      # Token template
stxscript new my-nft --template nft          # NFT template
stxscript new my-defi --template defi        # DeFi template

# Options
--template TYPE  Template (basic/token/nft/defi)
--path DIR       Target directory
```

## watch

Development mode with auto-rebuild.

```bash
stxscript watch [path]

# Examples
stxscript watch                      # Watch current directory
stxscript watch src/                 # Watch specific directory
stxscript watch src/ --output build/ # Specify output

# Options
--output DIR     Output directory
--ignore PATTERN Patterns to ignore
```

## doc

Generate documentation.

```bash
stxscript doc <input>

# Examples
stxscript doc contract.stx
stxscript doc src/ --output docs/
stxscript doc src/ --format markdown

# Options
--output DIR     Output directory (default: docs/)
--format FORMAT  Format (html/markdown)
```

## test

Run contract tests.

```bash
stxscript test [path]

# Examples
stxscript test                       # Run tests in tests/
stxscript test tests/                # Specify directory
stxscript test --coverage            # With coverage

# Options
--pattern PATTERN  File pattern (default: test_*.py)
--coverage         Enable coverage
--json             JSON output
```

## pkg

Package management.

### pkg init

Initialize a new package.

```bash
stxscript pkg init
stxscript pkg init --name my-package
```

### pkg add

Add a dependency.

```bash
stxscript pkg add <package>
stxscript pkg add some-package --version "^1.0.0"
stxscript pkg add some-package --dev
```

### pkg remove

Remove a dependency.

```bash
stxscript pkg remove <package>
stxscript pkg remove some-package --dev
```

### pkg install

Install all dependencies.

```bash
stxscript pkg install
```

### pkg list

List installed packages.

```bash
stxscript pkg list
```

## Global Options

```bash
--version       Show version
--verbose, -v   Verbose output
--help, -h      Show help
```

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error |
| 130 | Interrupted (Ctrl+C) |

## Configuration

### stxscript.toml

```toml
[package]
name = "my-project"
version = "0.1.0"
description = "My StxScript project"
authors = ["Your Name <email@example.com>"]
license = "MIT"

[dependencies]
# package = "^1.0.0"

[dev-dependencies]
# test-utils = "^0.1.0"
```

## Examples

### Development Workflow

```bash
# Create project
stxscript new my-token --template token
cd my-token

# Development
stxscript watch src/ --output build/

# Quality checks
stxscript fmt src/
stxscript lint src/
stxscript check src/

# Testing
stxscript test

# Build
stxscript build src/ build/
```

### CI/CD

```bash
#!/bin/bash
set -e

stxscript check src/
stxscript lint src/
stxscript fmt --check src/
stxscript test
stxscript build src/ build/
```

### Makefile

```makefile
.PHONY: all build check lint fmt test clean

all: check lint build

build:
	stxscript build src/ build/

check:
	stxscript check src/

lint:
	stxscript lint src/

fmt:
	stxscript fmt src/

test:
	stxscript test

clean:
	rm -rf build/
```
