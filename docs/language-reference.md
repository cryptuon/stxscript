# Language Reference

This document provides a comprehensive reference for the StxScript language syntax and features.

## Overview

StxScript is a TypeScript-inspired language that transpiles to Clarity, the smart contract language for the Stacks blockchain. It aims to provide familiar syntax while maintaining full compatibility with Clarity's type system and capabilities.

## Current Implementation Status

**✅ Fully Implemented:**
- Variable declarations
- Constant declarations
- Basic types
- Function declarations
- Type annotations

**🚧 In Progress:**
- Expression evaluation
- Control flow
- Function bodies

**📝 Planned:**
- Classes and traits
- Maps and complex data structures
- Error handling

## Basic Syntax

### Comments

```typescript
// Single-line comment

/*
  Multi-line comment
  (not yet implemented)
*/
```

### Statements

All statements must end with a semicolon:

```typescript
let balance: uint = 100u;
const MAX_SUPPLY: uint = 1000000u;
```

## Data Types

### Primitive Types

| StxScript Type | Clarity Type | Description | Range/Notes |
|----------------|--------------|-------------|-------------|
| `int` | `int` | Signed integer | -2^127 to 2^127-1 |
| `uint` | `uint` | Unsigned integer | 0 to 2^128-1 |
| `boolean` | `bool` | Boolean value | `true` or `false` |
| `string` | `string-utf8` | UTF-8 string | Max length specified |
| `principal` | `principal` | Stacks address | Contract or wallet address |
| `buffer` | `buff` | Byte buffer | Fixed-length byte array |

### Type Literals

```typescript
// Integers
let negative: int = -42;
let positive: int = 42;

// Unsigned integers (note the 'u' suffix)
let count: uint = 100u;
let supply: uint = 1000000u;

// Booleans
let isActive: boolean = true;
let isComplete: boolean = false;

// Strings
let name: string = "Hello, World!";
let symbol: string = "STX";

// Principals (Stacks addresses)
let wallet: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7;
let contract: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7.my-contract;
```

### Complex Types (Planned)

```typescript
// Lists (not yet implemented)
let numbers: list<uint> = [1u, 2u, 3u];

// Tuples (not yet implemented)
let person: {name: string, age: uint} = {name: "Alice", age: 30u};

// Optionals (not yet implemented)
let maybe_value: optional<uint> = some(42u);
let empty_value: optional<uint> = none();

// Response types (not yet implemented)
let result: Response<uint, string> = ok(100u);
let error: Response<uint, string> = err("Invalid input");
```

## Variables and Constants

### Variable Declarations

Variables are declared with `let` and can be reassigned (in future versions):

```typescript
// With type annotation
let balance: uint = 1000u;
let name: string = "Token";

// With type inference
let count = 42u;  // Inferred as uint
let active = true;  // Inferred as boolean
```

**Generated Clarity:**
```lisp
(define-data-var balance uint u1000)
(define-data-var name string "Token")
(define-data-var count uint u42)
(define-data-var active bool true)
```

### Constant Declarations

Constants are declared with `const` and cannot be reassigned:

```typescript
const MAX_SUPPLY: uint = 1000000u;
const TOKEN_NAME: string = "MyToken";
const DECIMALS: uint = 6u;
```

**Generated Clarity:**
```lisp
(define-constant MAX_SUPPLY u1000000)
(define-constant TOKEN_NAME "MyToken")
(define-constant DECIMALS u6)
```

### Naming Conventions

- Use `camelCase` for variables and functions
- Use `UPPER_SNAKE_CASE` for constants
- Use `PascalCase` for types and classes

```typescript
// Good
let tokenBalance: uint = 100u;
const MAX_SUPPLY: uint = 1000000u;

// Avoid
let TokenBalance: uint = 100u;  // Wrong case
let token_balance: uint = 100u;  // Wrong style
```

## Functions

### Function Declarations

Functions are declared with the `function` keyword:

```typescript
// Basic function
function add(a: int, b: int): int {
    // Function body (implementation pending)
}

// Public function (accessible from other contracts)
@public
function transfer(to: principal, amount: uint): Response<bool, string> {
    // Implementation
}

// Read-only function (doesn't modify state)
@readable
function getBalance(account: principal): uint {
    // Implementation
}

// Private function (internal use only)
function validateAmount(amount: uint): boolean {
    // Implementation
}
```

**Generated Clarity:**
```lisp
(define-private (add (a int) (b int))
  )

(define-public (transfer (to principal) (amount uint))
  )

(define-read-only (getBalance (account principal))
  )

(define-private (validateAmount (amount uint))
  )
```

### Function Decorators

| Decorator | Clarity Equivalent | Description |
|-----------|-------------------|-------------|
| `@public` | `define-public` | Publicly callable function |
| `@readable` | `define-read-only` | Read-only function |
| (none) | `define-private` | Private function (default) |

### Parameters and Return Types

```typescript
// Function with multiple parameters
function calculateFee(amount: uint, rate: uint): uint {
    // Implementation
}

// Function with Response return type
@public
function safeDivide(a: uint, b: uint): Response<uint, string> {
    // Implementation
}

// Function with no parameters
@readable
function getContractInfo(): string {
    // Implementation
}
```

## Expressions (Planned)

### Arithmetic Operations

```typescript
// Basic arithmetic (not yet implemented)
let sum = a + b;
let difference = a - b;
let product = a * b;
let quotient = a / b;
let remainder = a % b;
```

### Comparison Operations

```typescript
// Comparison operators (not yet implemented)
let isGreater = a > b;
let isEqual = a == b;
let isNotEqual = a != b;
let isLessOrEqual = a <= b;
```

### Logical Operations

```typescript
// Logical operators (not yet implemented)
let both = condition1 && condition2;
let either = condition1 || condition2;
let opposite = !condition;
```

## Control Flow (Planned)

### Conditional Statements

```typescript
// If statements (not yet implemented)
if (balance > amount) {
    // Transfer logic
} else {
    // Insufficient balance
}

// Ternary operator
let result = condition ? value1 : value2;
```

### Loops

```typescript
// For loops (not yet implemented)
for (let i = 0u; i < 10u; i = i + 1u) {
    // Loop body
}

// While loops
while (condition) {
    // Loop body
}
```

## Error Handling (Planned)

### Try-Catch

```typescript
// Error handling (not yet implemented)
try {
    let result = riskyOperation();
} catch (error: string) {
    // Handle error
}
```

### Response Types

```typescript
// Response type handling (not yet implemented)
function divide(a: uint, b: uint): Response<uint, string> {
    if (b == 0u) {
        return err("Division by zero");
    }
    return ok(a / b);
}
```

## Advanced Features (Planned)

### Classes and Traits

```typescript
// Trait definition (not yet implemented)
trait Token {
    transfer(from: principal, to: principal, amount: uint): Response<bool, string>;
    getBalance(account: principal): uint;
}

// Class implementation
@asset
class NFT {
    id: uint;
    owner: principal;
    metadata: string;
}
```

### Maps

```typescript
// Map declarations (not yet implemented)
@map
const balances: Map<principal, uint> = new Map();

@map
const allowances: Map<{owner: principal, spender: principal}, uint> = new Map();
```

## Built-in Functions (Planned)

### Clarity Integration

```typescript
// Direct Clarity function calls (not yet implemented)
let hash = clarity.sha256(data);
let height = clarity.blockHeight();
let sender = tx.sender;
```

### Utility Functions

```typescript
// List operations (not yet implemented)
let mapped = map(numbers, (x) => x * 2);
let filtered = filter(numbers, (x) => x > 10u);
let reduced = fold(numbers, 0u, (acc, x) => acc + x);
```

## Type System

### Type Inference

StxScript can infer types in many cases:

```typescript
let count = 42u;        // Inferred as uint
let name = "Token";     // Inferred as string
let active = true;      // Inferred as boolean
```

### Type Annotations

Explicit type annotations are recommended for clarity:

```typescript
let balance: uint = 0u;
let owner: principal = tx.sender;
```

### Type Conversion (Planned)

```typescript
// Type assertions (not yet implemented)
let value = someValue as uint;

// Type checking
if (value is uint) {
    // Handle as uint
}
```

## Best Practices

### Code Organization

```typescript
// Constants at the top
const TOKEN_NAME: string = "MyToken";
const MAX_SUPPLY: uint = 1000000u;

// State variables
let totalSupply: uint = 0u;
let contractOwner: principal = tx.sender;

// Functions grouped by visibility
@public
function publicFunction1() { }

@public
function publicFunction2() { }

@readable
function readOnlyFunction1() { }

function privateFunction1() { }
```

### Error Handling

```typescript
// Use descriptive error codes
const ERR_UNAUTHORIZED: uint = 100u;
const ERR_INSUFFICIENT_BALANCE: uint = 101u;
const ERR_INVALID_AMOUNT: uint = 102u;
```

### Documentation

```typescript
// Document complex functions
@public
function complexTransfer(
    from: principal,
    to: principal,
    amount: uint,
    memo: string
): Response<bool, uint> {
    // Transfers tokens with validation and event emission
    // Returns ok(true) on success, err(code) on failure
}
```

## Migration from Other Languages

### From TypeScript

StxScript syntax is very similar to TypeScript:

```typescript
// TypeScript
interface Token {
    name: string;
    symbol: string;
    totalSupply: number;
}

// StxScript equivalent (planned)
trait Token {
    getName(): string;
    getSymbol(): string;
    getTotalSupply(): uint;
}
```

### From Clarity

Direct translation is often straightforward:

```lisp
;; Clarity
(define-constant TOKEN_NAME "MyToken")
(define-data-var total-supply uint u0)

(define-public (transfer (amount uint) (recipient principal))
  (ok true))
```

```typescript
// StxScript
const TOKEN_NAME: string = "MyToken";
let totalSupply: uint = 0u;

@public
function transfer(amount: uint, recipient: principal): Response<bool, uint> {
    return ok(true);
}
```

## Limitations

Current limitations of the StxScript implementation:

1. **Function bodies**: Only declarations supported, no implementations
2. **Expressions**: Limited expression evaluation
3. **Control flow**: No if/else, loops, or complex logic
4. **Maps and lists**: Not yet implemented
5. **Error handling**: No try/catch support
6. **Classes**: Not yet implemented

## See Also

- [Examples](examples.md) - Practical code examples
- [API Documentation](api.md) - Python API reference
- [Installation Guide](installation.md) - Setup instructions