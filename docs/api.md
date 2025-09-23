# API Documentation

This document provides comprehensive API documentation for StxScript's Python interface.

## Overview

StxScript provides a Python API for programmatic transpilation of StxScript code to Clarity. This is useful for:

- Building development tools
- Integrating with build systems
- Creating custom workflows
- Testing and validation

## Installation

```bash
pip install stxscript
```

## Basic Usage

```python
from stxscript import StxScriptTranspiler

# Create transpiler instance
transpiler = StxScriptTranspiler()

# Transpile StxScript code
stx_code = "let balance: uint = 100u;"
clarity_code = transpiler.transpile(stx_code)
print(clarity_code)  # Output: (define-data-var balance uint u100)
```

## API Reference

### StxScriptTranspiler

The main class for transpiling StxScript code to Clarity.

#### Constructor

```python
StxScriptTranspiler()
```

Creates a new transpiler instance with default configuration.

**Example:**
```python
transpiler = StxScriptTranspiler()
```

#### Methods

##### `transpile(stxscript: str) -> str`

Transpiles StxScript source code to Clarity.

**Parameters:**
- `stxscript` (str): The StxScript source code to transpile

**Returns:**
- `str`: The generated Clarity code

**Raises:**
- `ValueError`: If the source code contains syntax errors
- `lark.exceptions.UnexpectedToken`: If the parser encounters unexpected tokens

**Example:**
```python
transpiler = StxScriptTranspiler()

# Simple variable
result = transpiler.transpile("let x: uint = 42u;")
print(result)  # (define-data-var x uint u42)

# Multiple statements
code = """
const MAX_SUPPLY: uint = 1000000u;
let total_minted: uint = 0u;
"""
result = transpiler.transpile(code)
print(result)
```

## Advanced Usage

### Error Handling

```python
from stxscript import StxScriptTranspiler
from lark.exceptions import UnexpectedToken

transpiler = StxScriptTranspiler()

try:
    result = transpiler.transpile("invalid syntax here")
except UnexpectedToken as e:
    print(f"Syntax error: {e}")
except ValueError as e:
    print(f"Semantic error: {e}")
```

### Processing Multiple Files

```python
import os
from stxscript import StxScriptTranspiler

def transpile_directory(input_dir, output_dir):
    """Transpile all .stx files in a directory."""
    transpiler = StxScriptTranspiler()

    for filename in os.listdir(input_dir):
        if filename.endswith('.stx'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace('.stx', '.clar'))

            with open(input_path, 'r') as f:
                stx_code = f.read()

            try:
                clarity_code = transpiler.transpile(stx_code)

                with open(output_path, 'w') as f:
                    f.write(clarity_code)

                print(f"Transpiled {filename} -> {os.path.basename(output_path)}")

            except Exception as e:
                print(f"Error transpiling {filename}: {e}")

# Usage
transpile_directory('src/contracts', 'build/contracts')
```

### Integration with Build Systems

#### Using with Make

```python
# build.py
import sys
from stxscript import StxScriptTranspiler

def main():
    if len(sys.argv) != 3:
        print("Usage: python build.py <input.stx> <output.clar>")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]

    transpiler = StxScriptTranspiler()

    try:
        with open(input_file, 'r') as f:
            stx_code = f.read()

        clarity_code = transpiler.transpile(stx_code)

        with open(output_file, 'w') as f:
            f.write(clarity_code)

        print(f"Successfully transpiled {input_file} to {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

#### Using with Poetry Scripts

Add to your `pyproject.toml`:

```toml
[tool.poetry.scripts]
build-contracts = "scripts.build:main"
```

### Custom Transpiler Wrapper

```python
from stxscript import StxScriptTranspiler
from pathlib import Path
import json

class StxScriptBuilder:
    """Enhanced wrapper around StxScriptTranspiler with additional features."""

    def __init__(self, config_file=None):
        self.transpiler = StxScriptTranspiler()
        self.config = self._load_config(config_file)

    def _load_config(self, config_file):
        """Load configuration from JSON file."""
        if config_file and Path(config_file).exists():
            with open(config_file) as f:
                return json.load(f)
        return {}

    def transpile_with_metadata(self, stx_code, source_file=None):
        """Transpile code and return metadata about the process."""
        try:
            clarity_code = self.transpiler.transpile(stx_code)

            return {
                'success': True,
                'clarity_code': clarity_code,
                'source_file': source_file,
                'line_count': len(stx_code.splitlines()),
                'output_size': len(clarity_code)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source_file': source_file
            }

    def batch_transpile(self, files):
        """Transpile multiple files and return results."""
        results = []

        for file_path in files:
            with open(file_path) as f:
                content = f.read()

            result = self.transpile_with_metadata(content, file_path)
            results.append(result)

        return results

# Usage
builder = StxScriptBuilder('config.json')
files = ['contract1.stx', 'contract2.stx']
results = builder.batch_transpile(files)

for result in results:
    if result['success']:
        print(f"✓ {result['source_file']}: {result['output_size']} chars")
    else:
        print(f"✗ {result['source_file']}: {result['error']}")
```

## Testing with the API

```python
import unittest
from stxscript import StxScriptTranspiler

class TestStxScriptAPI(unittest.TestCase):
    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def assert_transpiles_to(self, stx_code, expected_clarity):
        """Helper method for testing transpilation."""
        result = self.transpiler.transpile(stx_code)
        self.assertEqual(result.strip(), expected_clarity.strip())

    def test_variable_declaration(self):
        self.assert_transpiles_to(
            "let balance: uint = 100u;",
            "(define-data-var balance uint u100)"
        )

    def test_constant_declaration(self):
        self.assert_transpiles_to(
            "const MAX_SUPPLY: uint = 1000000u;",
            "(define-constant MAX_SUPPLY u1000000)"
        )

    def test_multiple_statements(self):
        stx_code = """
        const NAME: string = "Token";
        let supply: uint = 0u;
        """
        expected = """(define-constant NAME "Token")
(define-data-var supply uint u0)"""

        self.assert_transpiles_to(stx_code, expected)

    def test_error_handling(self):
        with self.assertRaises(Exception):
            self.transpiler.transpile("invalid syntax")

if __name__ == '__main__':
    unittest.main()
```

## Environment Variables

The API respects these environment variables:

- `STXSCRIPT_DEBUG`: Enable debug logging
- `STXSCRIPT_CACHE_DIR`: Directory for caching compiled grammars

```python
import os
os.environ['STXSCRIPT_DEBUG'] = '1'

from stxscript import StxScriptTranspiler
transpiler = StxScriptTranspiler()  # Now with debug logging
```

## Performance Considerations

### Reusing Transpiler Instances

```python
# Good: Reuse transpiler instance
transpiler = StxScriptTranspiler()
for code in code_samples:
    result = transpiler.transpile(code)

# Avoid: Creating new instances repeatedly
for code in code_samples:
    transpiler = StxScriptTranspiler()  # Expensive!
    result = transpiler.transpile(code)
```

### Memory Usage

For large batches of files, consider processing in chunks:

```python
def process_large_batch(files, chunk_size=100):
    transpiler = StxScriptTranspiler()

    for i in range(0, len(files), chunk_size):
        chunk = files[i:i + chunk_size]
        for file_path in chunk:
            # Process file
            pass
        # Optional: Force garbage collection
        import gc
        gc.collect()
```

## Integration Examples

### Flask Web API

```python
from flask import Flask, request, jsonify
from stxscript import StxScriptTranspiler

app = Flask(__name__)
transpiler = StxScriptTranspiler()

@app.route('/transpile', methods=['POST'])
def transpile_endpoint():
    try:
        stx_code = request.json['code']
        clarity_code = transpiler.transpile(stx_code)
        return jsonify({
            'success': True,
            'clarity_code': clarity_code
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)
```

### Django Integration

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from stxscript import StxScriptTranspiler
import json

transpiler = StxScriptTranspiler()

@csrf_exempt
@require_http_methods(["POST"])
def transpile_view(request):
    try:
        data = json.loads(request.body)
        stx_code = data['code']
        clarity_code = transpiler.transpile(stx_code)

        return JsonResponse({
            'success': True,
            'clarity_code': clarity_code
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
```

## Error Reference

### Common Exceptions

| Exception | Description | Common Causes |
|-----------|-------------|---------------|
| `UnexpectedToken` | Parser encountered unexpected syntax | Invalid StxScript syntax |
| `ValueError` | Semantic analysis failed | Type errors, undefined variables |
| `FileNotFoundError` | Grammar file not found | Installation issues |
| `MemoryError` | Out of memory | Very large files |

### Error Handling Best Practices

```python
from stxscript import StxScriptTranspiler
from lark.exceptions import LarkError

def safe_transpile(stx_code):
    """Safely transpile code with comprehensive error handling."""
    transpiler = StxScriptTranspiler()

    try:
        return {
            'success': True,
            'result': transpiler.transpile(stx_code)
        }
    except LarkError as e:
        return {
            'success': False,
            'error_type': 'syntax_error',
            'message': str(e)
        }
    except ValueError as e:
        return {
            'success': False,
            'error_type': 'semantic_error',
            'message': str(e)
        }
    except Exception as e:
        return {
            'success': False,
            'error_type': 'unknown_error',
            'message': str(e)
        }
```

## See Also

- [Language Reference](language-reference.md) - StxScript language syntax
- [Examples](examples.md) - Code examples and patterns
- [CLI Reference](cli.md) - Command-line interface