# Getting Started with StxScript

This guide will help you install StxScript and create your first smart contract.

## Requirements

- Python 3.10 or higher
- pip or uv package manager

## Installation

### From PyPI

```bash
pip install stxscript
```

### From Source (Development)

```bash
git clone https://github.com/cryptuon/stxscript.git
cd stxscript
uv venv && uv pip install -e ".[dev]"
```

### Verify Installation

```bash
stxscript --version
# Output: StxScript 0.3.0 (Phase 10: Ecosystem & Tooling)
```

## Your First Contract

### 1. Create a Project

```bash
stxscript new my-token --template token
cd my-token
```

This creates:
```
my-token/
├── src/
│   └── main.stx
├── tests/
├── build/
├── stxscript.toml
└── README.md
```

### 2. Write Your Contract

Edit `src/main.stx`:

```typescript
// Simple counter contract
const MAX_COUNT: uint = 1000u;

let counter: uint = 0u;

@public
function increment(): Response<uint, uint> {
    if (counter >= MAX_COUNT) {
        return err(1u);
    }
    counter = counter + 1u;
    return ok(counter);
}

@public
function decrement(): Response<uint, uint> {
    if (counter == 0u) {
        return err(2u);
    }
    counter = counter - 1u;
    return ok(counter);
}

@readonly
function get_counter(): uint {
    return counter;
}
```

### 3. Transpile to Clarity

```bash
stxscript build src/main.stx build/main.clar
```

View the output:
```bash
cat build/main.clar
```

### 4. Development Workflow

Start watch mode for automatic rebuilding:

```bash
stxscript watch src/ --output build/
```

Format your code:
```bash
stxscript fmt src/
```

Lint for issues:
```bash
stxscript lint src/
```

## Key Concepts

### Variables vs Constants

```typescript
// Constants (immutable)
const MAX_SUPPLY: uint = 1000000u;

// Variables (mutable state)
let total_supply: uint = 0u;
```

### Function Decorators

```typescript
// Public functions (callable from outside)
@public
function transfer(to: principal, amount: uint): Response<bool, uint> {
    // ...
}

// Read-only functions (no state changes)
@readonly
function get_balance(account: principal): uint {
    // ...
}

// Private functions (internal only)
function validate(amount: uint): bool {
    // ...
}
```

### Type System

```typescript
// Primitive types
let count: uint = 42u;           // Unsigned integer
let value: int = -42;            // Signed integer
let name: string = "Token";      // String
let active: bool = true;         // Boolean
let owner: principal = tx-sender; // Principal (address)

// Complex types
let numbers: List<uint> = [1u, 2u, 3u];
let user: { name: string, balance: uint } = { name: "Alice", balance: 100u };
let maybe: Optional<uint> = some(42u);
let result: Response<bool, uint> = ok(true);

// Maps
map balances<principal, uint>;
```

### Type Aliases

```typescript
type Amount = uint;
type Address = principal;

let transfer_amount: Amount = 1000u;
```

## Next Steps

- [Language Overview](../language/overview.md) - Complete language reference
- [CLI Reference](../reference/cli.md) - All CLI commands
- [Testing](../tooling/testing.md) - Write contract tests
- [IDE Setup](../tooling/ide-setup.md) - Configure VS Code
