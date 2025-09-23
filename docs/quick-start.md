# Quick Start Guide

Get up and running with StxScript in 5 minutes! This guide will walk you through installation, your first contract, and basic usage.

## 🚀 Installation

```bash
pip install stxscript
```

That's it! StxScript is now installed and ready to use.

## ✨ Your First Contract

Let's create a simple token contract to demonstrate StxScript basics.

### Step 1: Create the Contract

Create a file called `my-token.stx`:

```typescript
// my-token.stx
// A simple token contract

// Token configuration
const TOKEN_NAME: string = "MyToken";
const TOKEN_SYMBOL: string = "MTK";
const MAX_SUPPLY: uint = 1000000u;

// Contract state
let total_supply: uint = 0u;
let contract_owner: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7;

// Public functions
@public
function get_name(): Response<string, uint> {
    // Returns the token name
}

@public
function get_symbol(): Response<string, uint> {
    // Returns the token symbol
}

@readable
function get_total_supply(): uint {
    // Returns current total supply
}

@readable
function get_max_supply(): uint {
    // Returns maximum supply
}
```

### Step 2: Transpile to Clarity

```bash
stxscript my-token.stx my-token.clar
```

This creates `my-token.clar` with the following Clarity code:

```lisp
(define-constant TOKEN_NAME "MyToken")
(define-constant TOKEN_SYMBOL "MTK")
(define-constant MAX_SUPPLY u1000000)
(define-data-var total_supply uint u0)
(define-data-var contract_owner principal 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7)

(define-public (get_name )
  )

(define-public (get_symbol )
  )

(define-read-only (get_total_supply )
  )

(define-read-only (get_max_supply )
  )
```

### Step 3: Test Your Contract

Let's test the transpilation with Python:

```python
from stxscript import StxScriptTranspiler

# Create transpiler
transpiler = StxScriptTranspiler()

# Test a simple variable
result = transpiler.transpile('let balance: uint = 1000u;')
print(result)
# Output: (define-data-var balance uint u1000)

# Test a constant
result = transpiler.transpile('const MAX_SUPPLY: uint = 1000000u;')
print(result)
# Output: (define-constant MAX_SUPPLY u1000000)
```

## 🎯 Key Concepts

### 1. Variables vs Constants

```typescript
// Variables can change (in Clarity, these are data-vars)
let balance: uint = 1000u;
let owner: principal = tx.sender;

// Constants never change
const MAX_SUPPLY: uint = 1000000u;
const TOKEN_NAME: string = "MyToken";
```

### 2. Type Annotations

```typescript
// Explicit types (recommended)
let count: uint = 42u;
let name: string = "Alice";
let active: boolean = true;

// Type inference also works
let auto_count = 42u;     // Inferred as uint
let auto_name = "Alice";  // Inferred as string
```

### 3. Function Decorators

```typescript
// Public functions (callable by other contracts)
@public
function transfer(to: principal, amount: uint): Response<bool, string> {
    // Implementation
}

// Read-only functions (don't modify state)
@readable
function get_balance(account: principal): uint {
    // Implementation
}

// Private functions (internal only)
function validate_amount(amount: uint): boolean {
    // Implementation
}
```

## 🛠️ Common Patterns

### Configuration Pattern

```typescript
// Contract configuration
const CONTRACT_VERSION: string = "1.0.0";
const DECIMALS: uint = 6u;
const INITIAL_SUPPLY: uint = 1000000u;

// Error codes
const ERR_UNAUTHORIZED: uint = 100u;
const ERR_INSUFFICIENT_BALANCE: uint = 101u;
const ERR_INVALID_AMOUNT: uint = 102u;
```

### State Management Pattern

```typescript
// Owner management
let contract_owner: principal = tx.sender;
let is_paused: boolean = false;

// Token state
let total_supply: uint = 0u;
let total_burned: uint = 0u;
```

### Function Organization Pattern

```typescript
// 1. Constants first
const TOKEN_NAME: string = "MyToken";

// 2. State variables
let total_supply: uint = 0u;

// 3. Public functions
@public
function mint(amount: uint): Response<bool, uint> {
    // Minting logic
}

// 4. Read-only functions
@readable
function get_total_supply(): uint {
    // Return total supply
}

// 5. Private helpers
function validate_caller(): boolean {
    // Validation logic
}
```

## 📁 Project Structure

For larger projects, organize your contracts:

```
my-stacks-project/
├── contracts/
│   ├── token.stx          # Main token contract
│   ├── governance.stx     # Governance contract
│   └── utils.stx         # Shared utilities
├── build/
│   ├── token.clar        # Generated Clarity files
│   └── governance.clar
├── tests/
│   └── token.test.js
└── scripts/
    └── deploy.js
```

### Build Script Example

Create `scripts/build.py`:

```python
#!/usr/bin/env python3
import os
from pathlib import Path
from stxscript import StxScriptTranspiler

def build_contracts():
    """Build all StxScript contracts to Clarity."""
    transpiler = StxScriptTranspiler()

    contracts_dir = Path("contracts")
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    for stx_file in contracts_dir.glob("*.stx"):
        print(f"Building {stx_file.name}...")

        with open(stx_file) as f:
            stx_code = f.read()

        try:
            clarity_code = transpiler.transpile(stx_code)

            output_file = build_dir / stx_file.with_suffix(".clar").name
            with open(output_file, "w") as f:
                f.write(clarity_code)

            print(f"  ✓ Generated {output_file}")

        except Exception as e:
            print(f"  ✗ Error: {e}")

if __name__ == "__main__":
    build_contracts()
```

Run it with:
```bash
python scripts/build.py
```

## 🔍 Development Workflow

### 1. Write StxScript

```typescript
// contracts/counter.stx
let count: uint = 0u;

@public
function increment(): Response<uint, string> {
    // Implementation will be added later
}

@readable
function get_count(): uint {
    // Implementation will be added later
}
```

### 2. Transpile and Check

```bash
# Transpile single file
stxscript contracts/counter.stx build/counter.clar

# Check the output
cat build/counter.clar
```

### 3. Test with Clarinet (Optional)

If you have Clarinet installed:

```bash
# Initialize Clarinet project
clarinet new my-project
cd my-project

# Copy generated Clarity files
cp build/*.clar contracts/

# Run tests
clarinet test
```

## ⚡ CLI Usage

### Basic Commands

```bash
# Transpile a single file
stxscript input.stx output.clar

# Transpile to stdout
stxscript input.stx

# Process multiple files (planned feature)
stxscript contracts/*.stx --output-dir build/

# Check syntax only (planned feature)
stxscript --check contracts/token.stx
```

### Python API

```python
from stxscript import StxScriptTranspiler

# One-time transpilation
transpiler = StxScriptTranspiler()
result = transpiler.transpile("let x: uint = 42u;")
print(result)

# Batch processing
files = ["contract1.stx", "contract2.stx"]
for file_path in files:
    with open(file_path) as f:
        stx_code = f.read()

    clarity_code = transpiler.transpile(stx_code)

    output_path = file_path.replace(".stx", ".clar")
    with open(output_path, "w") as f:
        f.write(clarity_code)
```

## 🚧 Current Limitations

Keep in mind that StxScript is in alpha development:

**✅ Works now:**
- Variable and constant declarations
- Function signatures
- Basic types (int, uint, string, boolean, principal)
- Type annotations and inference

**🚧 Coming soon:**
- Function implementations
- Expressions and operators
- Control flow (if/else, loops)
- Maps and complex data structures

**Example of current limitations:**

```typescript
// This works ✅
let balance: uint = 1000u;
const MAX_SUPPLY: uint = 1000000u;

@public
function transfer(to: principal, amount: uint): Response<bool, string> {
    // Function signature works
}

// These don't work yet ❌
function add(a: uint, b: uint): uint {
    return a + b;  // Expressions not implemented
}

if (balance > amount) {    // Control flow not implemented
    // ...
}

let balances: Map<principal, uint>;  // Maps not implemented
```

## 🎓 Next Steps

1. **Read the docs**: Check out the [Language Reference](language-reference.md)
2. **Explore examples**: See [Examples](examples.md) for more patterns
3. **Join development**: Read [Contributing](contributing.md) to help build StxScript
4. **Stay updated**: Watch the GitHub repository for new features

## 🆘 Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/cryptuon/stxscript/issues)
- **Documentation**: Browse the [docs directory](README.md)
- **Examples**: Check [examples.md](examples.md) for code patterns

Happy coding with StxScript! 🎉