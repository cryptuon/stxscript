# API Reference

Python API documentation for programmatic use of StxScript.

## StxScriptTranspiler

The main class for transpiling StxScript code to Clarity.

### Import

```python
from stxscript import StxScriptTranspiler
```

### Constructor

```python
StxScriptTranspiler()
```

Creates a new transpiler instance. The parser is initialized with caching for performance.

### Methods

#### `transpile(stxscript: str) -> str`

Transpiles StxScript source code to Clarity.

**Parameters:**

- `stxscript` (str): The StxScript source code to transpile

**Returns:** Generated Clarity code as a string.

**Raises:** `lark.exceptions.UnexpectedToken` if the parser encounters syntax errors.

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

#### `transpile_with_error_handling(stxscript: str) -> dict`

Transpiles with structured error and warning reporting.

**Returns:** A dictionary with:

- `success` (bool): Whether transpilation succeeded
- `code` (str): Generated Clarity code (if successful)
- `errors` (list): List of error objects with `message`, `line`, `column`
- `warnings` (list): List of warning objects

```python
result = transpiler.transpile_with_error_handling(code)
if result['success']:
    print(result['code'])
else:
    for error in result['errors']:
        print(f"Error: {error}")
    for warning in result['warnings']:
        print(f"Warning: {warning}")
```

#### `parse_only(stxscript: str) -> object`

Parses StxScript and returns the AST without generating Clarity code. Useful for validation.

```python
ast = transpiler.parse_only("let x: uint = 42u;")
```

## ClarityGenerator

Converts AST nodes to Clarity code.

### Import

```python
from stxscript import ClarityGenerator
```

### Usage

```python
from stxscript import ClarityGenerator
from stxscript.ast_nodes import Program

generator = ClarityGenerator()
clarity_code = generator.generate(program_node)
```

## Testing Framework

Utilities for testing StxScript contracts.

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
        # or
        self.load_contract('const X: uint = 1u;')

    def test_something(self):
        pass
```

### ClarityValue

Factory for creating Clarity values in tests.

```python
# Primitives
integer = ClarityValue.int(-42)
unsigned = ClarityValue.uint(100)
boolean = ClarityValue.bool(True)
string = ClarityValue.string("Hello")
principal = ClarityValue.principal("'SP2J...")

# Optionals
some_value = ClarityValue.some(ClarityValue.uint(42))
none_value = ClarityValue.none()

# Responses
ok_result = ClarityValue.ok(ClarityValue.bool(True))
err_result = ClarityValue.err(ClarityValue.uint(1))

# Collections
list_value = ClarityValue.list([
    ClarityValue.uint(1),
    ClarityValue.uint(2)
])

tuple_value = ClarityValue.tuple({
    "name": ClarityValue.string("Alice"),
    "balance": ClarityValue.uint(100)
})
```

### Assertions

Assertion helpers for Clarity types.

```python
# Response assertions
Assertions.is_ok(result)
Assertions.is_err(result)
Assertions.ok_equals(result, expected_value)
Assertions.err_equals(result, expected_value)

# Optional assertions
Assertions.is_some(optional)
Assertions.is_none(optional)

# Equality
Assertions.equals(actual, expected)
```

### MockBlockchain

Simulate blockchain state for testing.

```python
blockchain = MockBlockchain()

blockchain.set_block_height(100)
blockchain.set_stx_balance("'SP2...", 1000000)
blockchain.set_var("total_supply", ClarityValue.uint(1000))
blockchain.set_map_entry("balances", "'SP2...", ClarityValue.uint(500))
blockchain.mine_block(10)
```

### MockContractCall

Mock responses from other contracts.

```python
mock = MockContractCall()

mock.when("Token", "transfer").returns(
    ClarityValue.ok(ClarityValue.bool(True))
)

mock.verify_called("Token", "transfer", times=1)
```

### TestRunner

Run test suites programmatically.

```python
runner = TestRunner()
results = runner.run_suite(TestMyContract)
runner.print_results()

# Export as JSON
json_output = runner.to_json()
```

## Package Manager

Dependency management for StxScript projects.

### Import

```python
from stxscript.package_manager import (
    PackageManager,
    Version,
    VersionRequirement
)
```

### PackageManager

```python
pm = PackageManager(".")

pm.init(name="my-project")
pm.load()
pm.add("some-package", version="^1.0.0")
pm.remove("some-package")
pm.install()

packages = pm.list()
for name, version, status in packages:
    print(f"{name}: {version} ({status})")
```

### Version

Semantic version parsing and comparison.

```python
from stxscript.package_manager import Version

v = Version.parse("1.2.3-beta.1")
print(v.major, v.minor, v.patch)  # 1 2 3

v1 = Version.parse("1.0.0")
v2 = Version.parse("2.0.0")
print(v1 < v2)  # True
```

### VersionRequirement

Version constraint matching.

```python
from stxscript.package_manager import VersionRequirement, Version

req = VersionRequirement.parse("^1.2.0")
print(req.satisfies(Version.parse("1.3.0")))  # True
print(req.satisfies(Version.parse("2.0.0")))  # False
```

## LSP Server

The Language Server Protocol implementation for IDE integration.

### Running

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

def safe_transpile(stx_code: str) -> dict:
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
