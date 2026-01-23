# Deployment

Integrating StxScript into your build pipeline and deploying contracts.

## Production Builds

Build optimized Clarity output:

```bash
stxscript build src/ build/
```

This runs the full pipeline: parsing, semantic analysis, and code generation for all `.stx` files in the source directory.

### Pre-build Checks

Run validation before building:

```bash
stxscript check src/       # Syntax validation
stxscript lint src/        # Static analysis
stxscript fmt --check src/ # Formatting check (exit 1 if unformatted)
stxscript build src/ build/
```

## Makefile Integration

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

fmt-check:
	stxscript fmt --check $(CONTRACTS_DIR)

test:
	stxscript test

clean:
	rm -rf $(BUILD_DIR)
```

Usage:

```bash
make all       # Check, lint, build
make test      # Run tests
make fmt       # Format code
make clean     # Remove build output
```

## GitHub Actions

### Basic CI Workflow

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

    - name: Check formatting
      run: stxscript fmt --check src/

    - name: Build
      run: stxscript build src/ build/

    - name: Test
      run: stxscript test

    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: clarity-contracts
        path: build/
```

### With Caching

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'
        cache: 'pip'

    - name: Install StxScript
      run: pip install stxscript

    - name: Quality checks
      run: |
        stxscript check src/
        stxscript lint src/
        stxscript fmt --check src/

    - name: Build and test
      run: |
        stxscript build src/ build/
        stxscript test
```

## Shell Script

For simple automation:

```bash
#!/bin/bash
set -e

echo "Checking syntax..."
stxscript check src/

echo "Running linter..."
stxscript lint src/

echo "Checking formatting..."
stxscript fmt --check src/

echo "Running tests..."
stxscript test

echo "Building contracts..."
stxscript build src/ build/

echo "Build complete!"
```

## package.json Scripts

For projects using Node.js tooling alongside StxScript:

```json
{
  "scripts": {
    "build": "stxscript build src/ build/",
    "check": "stxscript check src/",
    "lint": "stxscript lint src/",
    "fmt": "stxscript fmt src/",
    "test": "stxscript test",
    "watch": "stxscript watch src/ --output build/",
    "ci": "npm run check && npm run lint && npm run fmt -- --check && npm run test && npm run build"
  }
}
```

## Deploying to Stacks

After building your Clarity contracts:

1. The compiled `.clar` files are in your `build/` directory
2. Deploy using the [Stacks CLI](https://docs.stacks.co/docs/clarity/smart-contracts) or [Hiro Platform](https://www.hiro.so/)
3. Test on testnet before mainnet deployment

### Deployment Checklist

- [ ] All tests pass
- [ ] Linting has no errors
- [ ] Code is formatted
- [ ] Build succeeds with no warnings
- [ ] Tested on testnet
- [ ] Contract reviewed for security

## Next Steps

- [Project Setup](project-setup.md) - Project structure and configuration
- [Testing](../tooling/testing.md) - Writing thorough tests
- [CLI Reference](../reference/cli.md) - Build command options
