# Quick Start Guide

Get up and running with StxScript in 5 minutes!

## Installation

```bash
pip install stxscript
```

## Your First Contract

Let's create a simple token contract.

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

// Type alias for clarity
type Amount = uint;

// Map for balances
map balances<principal, Amount>;

// Public functions
@public
function mint(amount: Amount): Response<bool, uint> {
    if (total_supply + amount > MAX_SUPPLY) {
        return err(1u);
    }
    total_supply = total_supply + amount;
    return ok(true);
}

@readonly
function get_name(): string {
    return TOKEN_NAME;
}

@readonly
function get_total_supply(): Amount {
    return total_supply;
}
```

### Step 2: Transpile to Clarity

```bash
stxscript build my-token.stx my-token.clar
```

### Step 3: View the Output

```bash
cat my-token.clar
```

## Key Concepts

### Variables vs Constants

```typescript
// Variables can change (data-vars in Clarity)
let balance: uint = 1000u;

// Constants never change
const MAX_SUPPLY: uint = 1000000u;
```

### Type Annotations

```typescript
// Explicit types (recommended)
let count: uint = 42u;
let name: string = "Alice";
let active: bool = true;

// Type inference also works
let auto_count = 42u;     // Inferred as uint
```

### Function Decorators

```typescript
// Public functions (callable externally)
@public
function transfer(to: principal, amount: uint): Response<bool, uint> {
    // Implementation
}

// Read-only functions (don't modify state)
@readonly
function get_balance(account: principal): uint {
    // Implementation
}

// Private functions (internal only, default)
function validate_amount(amount: uint): bool {
    // Implementation
}
```

### Type Aliases

```typescript
type Amount = uint;
type Address = principal;

let transfer_amount: Amount = 1000u;
```

### Generic Types

```typescript
function identity<T>(value: T): T {
    return value;
}
```

## Project Setup

### Create a New Project

```bash
# Create a new project with the token template
stxscript new my-token --template token
cd my-token
```

### Project Structure

```
my-token/
├── src/
│   └── main.stx
├── tests/
├── build/
├── stxscript.toml
└── README.md
```

### Development Workflow

```bash
# Watch for changes and auto-build
stxscript watch src/ --output build/

# Run tests
stxscript test

# Format code
stxscript fmt src/

# Lint code
stxscript lint src/
```

## Using the Package Manager

```bash
# Initialize a package
stxscript pkg init

# Add a dependency
stxscript pkg add some-package --version "^1.0.0"

# Install dependencies
stxscript pkg install

# List packages
stxscript pkg list
```

## Using the Python API

```python
from stxscript import StxScriptTranspiler

# Create transpiler
transpiler = StxScriptTranspiler()

# Transpile code
result = transpiler.transpile('let balance: uint = 1000u;')
print(result)
# Output: (define-data-var balance uint u1000)
```

## Testing Contracts

Create a test file `tests/test_token.py`:

```python
from stxscript.testing import ContractTestCase, ClarityValue, Assertions

class TestToken(ContractTestCase):
    def setUp(self):
        self.load_contract_file('src/main.stx')

    def test_mint_success(self):
        # Test minting tokens
        result = ClarityValue.ok(ClarityValue.bool(True))
        Assertions.is_ok(result)

    def test_get_name(self):
        # Test getting token name
        pass
```

Run tests:

```bash
stxscript test
```

## Common Patterns

### Configuration Pattern

```typescript
const CONTRACT_VERSION: string = "1.0.0";
const DECIMALS: uint = 6u;

// Error codes
const ERR_UNAUTHORIZED: uint = 100u;
const ERR_INSUFFICIENT_BALANCE: uint = 101u;
```

### State Management

```typescript
let contract_owner: principal = tx-sender;
let is_paused: bool = false;
let total_supply: uint = 0u;
```

## CLI Commands

```bash
stxscript build <file>           # Transpile to Clarity
stxscript fmt <files>            # Format code
stxscript lint <files>           # Lint code
stxscript check <files>          # Check syntax
stxscript new <name>             # Create project
stxscript watch <path>           # Watch mode
stxscript test                   # Run tests
stxscript pkg <command>          # Package management
```

## Next Steps

1. **Read the docs**: Check out the [Language Reference](language-reference.md)
2. **Explore examples**: See [Examples](examples.md)
3. **Join development**: Read [Contributing](contributing.md)

## Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/cryptuon/stxscript/issues)
- **Documentation**: Browse the [docs](README.md)

Happy coding with StxScript!
