# Examples

This page contains practical examples of StxScript code and their Clarity output.

## Basic Variables and Constants

### Example 1: Token Configuration

**StxScript:**
```typescript
// Token configuration
const TOKEN_NAME: string = "MyToken";
const TOKEN_SYMBOL: string = "MTK";
const MAX_SUPPLY: uint = 1000000u;

// State variables
let total_supply: uint = 0u;
let contract_owner: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7;
```

**Generated Clarity:**
```lisp
(define-constant TOKEN_NAME "MyToken")
(define-constant TOKEN_SYMBOL "MTK")
(define-constant MAX_SUPPLY u1000000)
(define-data-var total_supply uint u0)
(define-data-var contract_owner principal 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7)
```

### Example 2: Counter Contract

**StxScript:**
```typescript
// Simple counter contract
let counter: uint = 0u;
const MAX_COUNT: uint = 100u;

@public
function increment(): Response<uint, string> {
    // Implementation would go here
}

@readable
function get_counter(): uint {
    // Implementation would go here
}
```

**Generated Clarity:**
```lisp
(define-data-var counter uint u0)
(define-constant MAX_COUNT u100)

(define-public (increment )
  )

(define-read-only (get_counter )
  )
```

## Function Examples

### Example 3: Basic Functions

**StxScript:**
```typescript
@public
function transfer(to: principal, amount: uint): Response<bool, uint> {
    // Function body would contain logic
}

@readable
function get_balance(account: principal): uint {
    // Read-only function to get balance
}

function internal_helper(value: uint): uint {
    // Private helper function
}
```

**Generated Clarity:**
```lisp
(define-public (transfer (to principal) (amount uint))
  )

(define-read-only (get_balance (account principal))
  )

(define-private (internal_helper (value uint))
  )
```

## Real-World Contract Examples

### Example 4: Basic Token Contract Structure

**StxScript:**
```typescript
// Basic SIP-010 Token Contract
const TOKEN_NAME: string = "Example Token";
const TOKEN_SYMBOL: string = "EXAM";
const TOKEN_DECIMALS: uint = 6u;
const TOTAL_SUPPLY: uint = 1000000000000u;

// Contract deployer
let contract_owner: principal = tx.sender;

// Token balances and allowances would be implemented as maps
// (Currently simplified for demonstration)

@public
function transfer(amount: uint, sender: principal, recipient: principal): Response<bool, uint> {
    // Transfer logic would go here
}

@readable
function get_name(): Response<string, uint> {
    // Return token name
}

@readable
function get_symbol(): Response<string, uint> {
    // Return token symbol
}

@readable
function get_decimals(): Response<uint, uint> {
    // Return token decimals
}

@readable
function get_total_supply(): Response<uint, uint> {
    // Return total supply
}
```

## Type Examples

### Example 5: Different Data Types

**StxScript:**
```typescript
// Numeric types
let signed_number: int = -42;
let unsigned_number: uint = 42u;

// Text types
let message: string = "Hello, Stacks!";

// Blockchain types
let wallet_address: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7;

// Boolean
let is_active: boolean = true;
```

**Generated Clarity:**
```lisp
(define-data-var signed_number int -42)
(define-data-var unsigned_number uint u42)
(define-data-var message string "Hello, Stacks!")
(define-data-var wallet_address principal 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7)
(define-data-var is_active bool true)
```

## Development Patterns

### Example 6: Using the CLI

```bash
# Create a simple contract
cat > my-token.stx << 'EOF'
const TOKEN_NAME: string = "MyToken";
let total_supply: uint = 1000000u;

@public
function mint(amount: uint): Response<bool, string> {
    // Minting logic
}
EOF

# Transpile to Clarity
stxscript my-token.stx my-token.clar

# View the output
cat my-token.clar
```

### Example 7: Using the Python API

```python
from stxscript import StxScriptTranspiler

# Create transpiler instance
transpiler = StxScriptTranspiler()

# Define StxScript code
stx_code = """
const GREETING: string = "Hello, World!";
let visitor_count: uint = 0u;

@public
function say_hello(): Response<string, string> {
    // Return greeting
}
"""

# Transpile to Clarity
clarity_code = transpiler.transpile(stx_code)
print("Generated Clarity:")
print(clarity_code)

# Save to file
with open("hello-world.clar", "w") as f:
    f.write(clarity_code)
```

## Testing Examples

### Example 8: Setting up Tests

```python
import unittest
from stxscript import StxScriptTranspiler

class TestMyContract(unittest.TestCase):
    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_basic_variable(self):
        stx_code = "let balance: uint = 100u;"
        result = self.transpiler.transpile(stx_code)
        expected = "(define-data-var balance uint u100)"
        self.assertEqual(result.strip(), expected)

    def test_constant_declaration(self):
        stx_code = "const MAX_SUPPLY: uint = 1000000u;"
        result = self.transpiler.transpile(stx_code)
        expected = "(define-constant MAX_SUPPLY u1000000)"
        self.assertEqual(result.strip(), expected)

if __name__ == "__main__":
    unittest.main()
```

## Common Patterns

### Example 9: Error Codes

```typescript
// Define error codes as constants
const ERR_UNAUTHORIZED: uint = 100u;
const ERR_INSUFFICIENT_BALANCE: uint = 101u;
const ERR_INVALID_AMOUNT: uint = 102u;

@public
function safe_transfer(amount: uint, to: principal): Response<bool, uint> {
    // Would use error codes in implementation
}
```

### Example 10: Configuration Pattern

```typescript
// Contract configuration
const CONTRACT_VERSION: string = "1.0.0";
const MAINTENANCE_MODE: boolean = false;

// Feature flags
const TRANSFERS_ENABLED: boolean = true;
const MINTING_ENABLED: boolean = true;

let contract_admin: principal = tx.sender;
```

## Next Steps

- Learn more about [Language Reference](language-reference.md)
- Check out the [API Documentation](api.md)
- Read about [Contributing](contributing.md) to add more examples

## Community Examples

Have a great StxScript example? We'd love to include it! Please:

1. Fork the repository
2. Add your example to this file
3. Include both StxScript and generated Clarity code
4. Add a brief explanation
5. Submit a pull request

---

**Note**: Some examples show planned features that may not be fully implemented yet. Check the current feature status in the main README.