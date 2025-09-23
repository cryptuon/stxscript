# CLI Reference

The StxScript command-line interface provides tools for transpiling StxScript files to Clarity.

## Installation

The CLI is automatically available after installing StxScript:

```bash
pip install stxscript
```

## Basic Usage

```bash
# Transpile a file
stxscript input.stx output.clar

# Transpile to stdout
stxscript input.stx

# Read from stdin
echo "let x: uint = 42u;" | stxscript

# Read from stdin explicitly
stxscript - output.clar
```

## Command Reference

### Synopsis

```bash
stxscript [OPTIONS] [INPUT] [OUTPUT]
```

### Arguments

- `INPUT` - Input StxScript file path, or `-` for stdin (optional)
- `OUTPUT` - Output Clarity file path (optional, defaults to stdout)

### Options

| Option | Description |
|--------|-------------|
| `--version` | Show version information and exit |
| `--check` | Check syntax only, don't generate output |
| `--verbose`, `-v` | Enable verbose output |
| `--help`, `-h` | Show help message and exit |

## Examples

### Basic File Transpilation

```bash
# Create a simple contract
cat > token.stx << 'EOF'
const TOKEN_NAME: string = "MyToken";
let total_supply: uint = 1000u;
EOF

# Transpile to Clarity
stxscript token.stx token.clar

# Check the output
cat token.clar
```

**Output:**
```lisp
(define-constant TOKEN_NAME "MyToken")
(define-data-var total_supply uint u1000)
```

### Using Stdin/Stdout

```bash
# Pipe input
echo 'const MAX_SUPPLY: uint = 1000000u;' | stxscript

# Chain with other tools
cat contract.stx | stxscript | clarinet check --stdin
```

### Syntax Checking

```bash
# Check syntax without generating output
stxscript --check contract.stx

# Check with verbose output
stxscript --check --verbose contract.stx
```

### Verbose Mode

```bash
# See detailed processing information
stxscript --verbose contract.stx contract.clar
```

**Sample verbose output:**
```
Reading from contract.stx...
Transpiling contract.stx...
Generated contract.clar
```

## Error Handling

The CLI provides clear error messages for common issues:

### Syntax Errors

```bash
$ echo 'invalid syntax' | stxscript
Error transpiling <stdin>: Unexpected token ...
```

### File Not Found

```bash
$ stxscript nonexistent.stx
Error: File 'nonexistent.stx' not found
```

### Permission Errors

```bash
$ stxscript contract.stx /root/protected.clar
Error writing output: Permission denied
```

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (syntax, file not found, etc.) |

## Integration Examples

### Makefile Integration

```makefile
# Makefile
CONTRACTS_DIR = contracts
BUILD_DIR = build

%.clar: $(CONTRACTS_DIR)/%.stx
	@mkdir -p $(BUILD_DIR)
	stxscript $< $(BUILD_DIR)/$@

all: token.clar governance.clar

clean:
	rm -rf $(BUILD_DIR)

.PHONY: all clean
```

### Shell Script

```bash
#!/bin/bash
# build.sh - Build all contracts

set -e

CONTRACTS_DIR="contracts"
BUILD_DIR="build"

# Create build directory
mkdir -p "$BUILD_DIR"

# Process all .stx files
for stx_file in "$CONTRACTS_DIR"/*.stx; do
    if [[ -f "$stx_file" ]]; then
        filename=$(basename "$stx_file" .stx)
        output_file="$BUILD_DIR/${filename}.clar"

        echo "Building $stx_file -> $output_file"

        if stxscript "$stx_file" "$output_file"; then
            echo "✓ Success"
        else
            echo "✗ Failed"
            exit 1
        fi
    fi
done

echo "All contracts built successfully!"
```

### Poetry Script

Add to your `pyproject.toml`:

```toml
[tool.poetry.scripts]
build-contracts = "scripts.build:main"
stx-check = "scripts.check:main"
```

Create `scripts/build.py`:

```python
import subprocess
import sys
from pathlib import Path

def main():
    """Build all StxScript contracts."""
    contracts_dir = Path("contracts")
    build_dir = Path("build")

    if not contracts_dir.exists():
        print("No contracts directory found")
        return

    build_dir.mkdir(exist_ok=True)

    for stx_file in contracts_dir.glob("*.stx"):
        output_file = build_dir / f"{stx_file.stem}.clar"

        cmd = ["stxscript", str(stx_file), str(output_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✓ {stx_file.name} -> {output_file.name}")
        else:
            print(f"✗ {stx_file.name}: {result.stderr.strip()}")
            sys.exit(1)

if __name__ == "__main__":
    main()
```

### GitHub Actions Workflow

```yaml
# .github/workflows/build.yml
name: Build Contracts

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install StxScript
      run: |
        pip install stxscript

    - name: Build contracts
      run: |
        mkdir -p build
        for contract in contracts/*.stx; do
          filename=$(basename "$contract" .stx)
          stxscript "$contract" "build/${filename}.clar"
        done

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: clarity-contracts
        path: build/
```

## Tips and Best Practices

### File Organization

```bash
# Recommended project structure
project/
├── contracts/          # StxScript source files
│   ├── token.stx
│   └── governance.stx
├── build/             # Generated Clarity files
│   ├── token.clar
│   └── governance.clar
├── scripts/           # Build scripts
└── tests/            # Test files
```

### Batch Processing

```bash
# Process multiple files
for file in contracts/*.stx; do
    output="build/$(basename "$file" .stx).clar"
    stxscript "$file" "$output"
done

# Using find
find contracts -name "*.stx" -exec stxscript {} build/{}.clar \;
```

### Watch Mode (External Tool)

Use `entr` for automatic rebuilding:

```bash
# Install entr first: brew install entr

# Watch for changes and rebuild
find contracts -name "*.stx" | entr -s 'make build'
```

## Troubleshooting

### Common Issues

**Command not found: stxscript**

Solution:
```bash
# Check installation
pip show stxscript

# Reinstall if needed
pip install --force-reinstall stxscript

# Use module syntax as fallback
python -m stxscript
```

**Permission denied**

Solution:
```bash
# Check file permissions
ls -la input.stx

# Check directory permissions
ls -la build/

# Create directory if needed
mkdir -p build
```

**Poetry script warnings**

The warnings about uninstalled scripts are normal in development. To eliminate them:

```bash
poetry install
```

## Advanced Usage

### Configuration File (Planned)

Future versions will support configuration files:

```json
{
  "input_dir": "contracts",
  "output_dir": "build",
  "include": ["*.stx"],
  "exclude": ["**/test/**"],
  "options": {
    "verbose": true,
    "check_only": false
  }
}
```

### Multiple Input Files (Planned)

```bash
# Process multiple files (planned feature)
stxscript contracts/*.stx --output-dir build/

# Watch mode (planned feature)
stxscript --watch contracts/ --output-dir build/
```

## See Also

- [Quick Start Guide](quick-start.md) - Get started quickly
- [API Documentation](api.md) - Python API reference
- [Examples](examples.md) - Code examples and patterns