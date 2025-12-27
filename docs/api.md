# API Documentation

This document provides comprehensive API documentation for StxScript's Python interface.

## Overview

StxScript provides a Python API for programmatic transpilation, testing, and package management. This is useful for:

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

## StxScriptTranspiler

The main class for transpiling StxScript code to Clarity.

### Constructor

```python
StxScriptTranspiler()
```

Creates a new transpiler instance with default configuration.

### Methods

#### `transpile(stxscript: str) -> str`

Transpiles StxScript source code to Clarity.

**Parameters:**
- `stxscript` (str): The StxScript source code to transpile

**Returns:**
- `str`: The generated Clarity code

**Raises:**
- `lark.exceptions.UnexpectedToken`: If the parser encounters syntax errors

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

#### `transpile_with_error_handling(stxscript: str) -> TranspileResult`

Transpiles with structured error reporting.

**Returns:**
- `TranspileResult`: Object with `success`, `code`, `errors`, and `warnings` fields

**Example:**
```python
result = transpiler.transpile_with_error_handling(code)
if result.success:
    print(result.code)
else:
    for error in result.errors:
        print(f"Error at line {error.line}: {error.message}")
```

## Testing Framework

The testing module provides utilities for testing StxScript contracts.

### Import

```python
from stxscript.testing import (
    ContractTestCase,
    ClarityValue,
    Assertions,
    MockContractCall,
    MockBlockchain,
    TestRunner
)
```

### ContractTestCase

Base class for contract test cases.

```python
class TestMyContract(ContractTestCase):
    def setUp(self):
        self.load_contract_file('contract.stx')

    def test_something(self):
        # Test code here
        pass
```

### ClarityValue

Represents a Clarity value for testing.

```python
# Create values
integer = ClarityValue.int(-42)
unsigned = ClarityValue.uint(100)
boolean = ClarityValue.bool(True)
string = ClarityValue.string("Hello")
principal = ClarityValue.principal("'SP2...")

# Create complex values
optional_some = ClarityValue.some(ClarityValue.uint(42))
optional_none = ClarityValue.none()
response_ok = ClarityValue.ok(ClarityValue.bool(True))
response_err = ClarityValue.err(ClarityValue.uint(1))
list_val = ClarityValue.list([ClarityValue.uint(1), ClarityValue.uint(2)])
tuple_val = ClarityValue.tuple({"name": ClarityValue.string("Alice")})
```

### Assertions

Assertion helpers for Clarity types.

```python
# Check response types
Assertions.is_ok(result)
Assertions.is_err(result)
Assertions.ok_equals(result, expected_value)
Assertions.err_equals(result, expected_value)

# Check optional types
Assertions.is_some(optional)
Assertions.is_none(optional)

# Check equality
Assertions.equals(actual, expected)
```

### MockBlockchain

Mock blockchain state for testing.

```python
from stxscript.testing import MockBlockchain

blockchain = MockBlockchain()

# Set block height
blockchain.set_block_height(100)

# Set balances
blockchain.set_stx_balance("'SP2...", 1000000)

# Set data variables
blockchain.set_var("total_supply", ClarityValue.uint(1000))

# Set map entries
blockchain.set_map_entry("balances", "'SP2...", ClarityValue.uint(500))

# Mine blocks
blockchain.mine_block(10)
```

### MockContractCall

Mock for contract calls.

```python
from stxscript.testing import MockContractCall

mock = MockContractCall()

# Set up mock response
mock.when("Token", "transfer").returns(ClarityValue.ok(ClarityValue.bool(True)))

# Verify calls
mock.verify_called("Token", "transfer", times=1)
```

### TestRunner

Runs test suites.

```python
from stxscript.testing import TestRunner

runner = TestRunner()
results = runner.run_suite(TestMyContract)
runner.print_results()

# Export as JSON
json_output = runner.to_json()
```

## Package Manager

The package manager provides dependency management.

### Import

```python
from stxscript.package_manager import (
    PackageManager,
    Version,
    VersionRequirement,
    PackageManifest
)
```

### PackageManager

```python
pm = PackageManager(".")

# Initialize a new project
pm.init(name="my-project")

# Load existing project
pm.load()

# Add a dependency
pm.add("some-package", version="^1.0.0")

# Remove a dependency
pm.remove("some-package")

# Install all dependencies
pm.install()

# List packages
packages = pm.list()
for name, version, status in packages:
    print(f"{name}: {version} ({status})")
```

### Version

```python
from stxscript.package_manager import Version

v = Version.parse("1.2.3-beta.1")
print(v.major)       # 1
print(v.minor)       # 2
print(v.patch)       # 3
print(v.prerelease)  # "beta.1"

# Compare versions
v1 = Version.parse("1.0.0")
v2 = Version.parse("2.0.0")
print(v1 < v2)  # True
```

### VersionRequirement

```python
from stxscript.package_manager import VersionRequirement, Version

req = VersionRequirement.parse("^1.2.0")
v1 = Version.parse("1.3.0")
v2 = Version.parse("2.0.0")

print(req.satisfies(v1))  # True (same major, >= 1.2.0)
print(req.satisfies(v2))  # False (different major)
```

## LSP Server

The LSP server provides IDE integration.

### Running the Server

```bash
stxscript-lsp
```

Or programmatically:

```python
from stxscript.lsp_server import main
main()
```

## Error Handling

```python
from stxscript import StxScriptTranspiler
from lark.exceptions import LarkError

def safe_transpile(stx_code):
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
```

## Complete Example

```python
from stxscript import StxScriptTranspiler
from stxscript.testing import ContractTestCase, ClarityValue, Assertions
from stxscript.package_manager import PackageManager

# Transpile a contract
transpiler = StxScriptTranspiler()
code = """
const MAX_SUPPLY: uint = 1000000u;
let total_supply: uint = 0u;

@public
function mint(amount: uint): Response<bool, uint> {
    if (total_supply + amount > MAX_SUPPLY) {
        return err(1u);
    }
    total_supply = total_supply + amount;
    return ok(true);
}
"""
clarity = transpiler.transpile(code)
print(clarity)

# Test the contract
class TestMint(ContractTestCase):
    def setUp(self):
        self.load_contract(code)

    def test_mint_within_limit(self):
        result = ClarityValue.ok(ClarityValue.bool(True))
        Assertions.is_ok(result)

# Run tests
from stxscript.testing import TestRunner
runner = TestRunner()
runner.run_suite(TestMint)
runner.print_results()
```

## See Also

- [Language Reference](language-reference.md) - StxScript language syntax
- [Examples](examples.md) - Code examples and patterns
- [CLI Reference](cli.md) - Command-line interface
