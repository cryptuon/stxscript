# Language Reference

This document provides a comprehensive reference for the StxScript language syntax and features.

## Overview

StxScript is a TypeScript-inspired language that transpiles to Clarity, the smart contract language for the Stacks blockchain. It provides familiar syntax while maintaining full compatibility with Clarity's type system.

## Basic Syntax

### Comments

```typescript
// Single-line comment

/* Multi-line
   comment */

/// Documentation comment
```

### Statements

All statements must end with a semicolon:

```typescript
let balance: uint = 100u;
const MAX_SUPPLY: uint = 1000000u;
```

## Data Types

### Primitive Types

| StxScript Type | Clarity Type | Description |
|----------------|--------------|-------------|
| `int` | `int` | Signed 128-bit integer |
| `uint` | `uint` | Unsigned 128-bit integer |
| `bool` / `boolean` | `bool` | Boolean value |
| `string` | `string-utf8` | UTF-8 string |
| `principal` | `principal` | Stacks address |
| `buffer` / `buffer<N>` | `buff` | Byte buffer |

### Type Literals

```typescript
// Integers
let negative: int = -42;
let positive: int = 42;

// Unsigned integers (note the 'u' suffix)
let count: uint = 100u;
let supply: uint = 1000000u;

// Booleans
let isActive: bool = true;
let isComplete: boolean = false;

// Strings
let name: string = "Hello, World!";

// Principals (Stacks addresses)
let wallet: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7;
let contract: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7.my-contract;

// Buffers with size
let data: buffer<32> = 0x1234;
```

### Complex Types

```typescript
// Lists
let numbers: List<uint> = [1u, 2u, 3u];

// Tuples
let person: { name: string, age: uint } = { name: "Alice", age: 30u };

// Optionals
let maybeValue: Optional<uint> = some(42u);
let emptyValue: Optional<uint> = none;

// Response types
let success: Response<uint, string> = ok(100u);
let failure: Response<uint, string> = err("Invalid input");

// Maps
map balances<principal, uint>;
```

### Type Aliases

```typescript
// Create type aliases
type Amount = uint;
type Address = principal;
type Balance = { amount: uint, locked: bool };

// Use type aliases
let transfer_amount: Amount = 1000u;
let recipient: Address = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7;
```

## Variables and Constants

### Variable Declarations

Variables are declared with `let`:

```typescript
// With type annotation
let balance: uint = 1000u;
let name: string = "Token";

// With type inference
let count = 42u;      // Inferred as uint
let active = true;    // Inferred as bool
```

**Generated Clarity:**
```lisp
(define-data-var balance uint u1000)
(define-data-var name (string-utf8 5) u"Token")
```

### Constant Declarations

Constants are declared with `const`:

```typescript
const MAX_SUPPLY: uint = 1000000u;
const TOKEN_NAME: string = "MyToken";
```

**Generated Clarity:**
```lisp
(define-constant MAX_SUPPLY u1000000)
(define-constant TOKEN_NAME u"MyToken")
```

## Functions

### Function Declarations

```typescript
// Private function (default)
function add(a: int, b: int): int {
    return a + b;
}

// Public function
@public
function transfer(to: principal, amount: uint): Response<bool, string> {
    // Implementation
    return ok(true);
}

// Read-only function
@readonly
function getBalance(account: principal): uint {
    return balances.get(account);
}
```

**Generated Clarity:**
```lisp
(define-private (add (a int) (b int))
  (+ a b))

(define-public (transfer (to principal) (amount uint))
  (ok true))

(define-read-only (get-balance (account principal))
  (map-get? balances account))
```

### Function Decorators

| Decorator | Clarity Equivalent | Description |
|-----------|-------------------|-------------|
| `@public` | `define-public` | Publicly callable function |
| `@readonly` | `define-read-only` | Read-only function |
| (none) | `define-private` | Private function (default) |

### Generic Functions

```typescript
function identity<T>(value: T): T {
    return value;
}

function swap<T, U>(a: T, b: U): { first: U, second: T } {
    return { first: b, second: a };
}
```

## Expressions

### Arithmetic Operations

```typescript
let sum = a + b;
let difference = a - b;
let product = a * b;
let quotient = a / b;
let remainder = a % b;
```

### Comparison Operations

```typescript
let isGreater = a > b;
let isEqual = a == b;
let isNotEqual = a != b;
let isLessOrEqual = a <= b;
```

### Logical Operations

```typescript
let both = condition1 && condition2;
let either = condition1 || condition2;
let opposite = !condition;
```

### Bitwise Operations

```typescript
let andResult = a & b;
let orResult = a | b;
let xorResult = a ^ b;
let notResult = ~a;
let leftShift = a << 2;
let rightShift = a >> 2;
```

## Control Flow

### If/Else Statements

```typescript
if (balance > amount) {
    // Transfer logic
} else {
    // Insufficient balance
}

// Ternary operator
let result = condition ? value1 : value2;
```

### Match Expressions

```typescript
match result {
    ok(value) => value,
    err(e) => 0u
}

match maybeValue {
    some(v) => v,
    none => defaultValue
}
```

### For Loops

```typescript
// Compiles to fold over range
for (let i = 0; i < 10; i = i + 1) {
    sum = sum + i;
}
```

### While Loops

```typescript
// Requires bounded iteration
while (count < limit) {
    count = count + 1;
}
```

## Data Structures

### Maps

```typescript
// Declaration
map balances<principal, uint>;
map allowances<{ owner: principal, spender: principal }, uint>;

// Operations
let balance = balances.get(account);
balances.set(account, newBalance);
balances.delete(account);
```

### Lists

```typescript
// List literals
let numbers: List<uint> = [1u, 2u, 3u, 4u, 5u];

// List operations
let doubled = map(numbers, (x) => x * 2u);
let evens = filter(numbers, (x) => x % 2u == 0u);
let sum = fold(numbers, 0u, (acc, x) => acc + x);
```

### Tuples

```typescript
// Tuple creation
let user = { name: "Alice", balance: 1000u };

// Tuple access
let userName = user.name;
let userBalance = user.balance;
```

## Traits

### Trait Definition

```typescript
trait Token {
    transfer(from: principal, to: principal, amount: uint): Response<bool, uint>;
    getBalance(account: principal): uint;
}
```

### Trait Implementation

```typescript
@implements(Token)
class MyToken {
    @public
    function transfer(from: principal, to: principal, amount: uint): Response<bool, uint> {
        // Implementation
    }

    @readonly
    function getBalance(account: principal): uint {
        // Implementation
    }
}
```

## Lambda Expressions

```typescript
// Arrow function syntax
let double = (x: uint) => x * 2u;

// With multiple parameters
let add = (a: uint, b: uint) => a + b;

// Used with higher-order functions
let doubled = map(numbers, (x) => x * 2u);
```

## Import/Export

```typescript
// Import from other modules
import { TokenTrait } from "./traits";
import { utils } from "../lib/utils";

// Contract calls
let result = OtherContract.method(arg1, arg2);
```

## Error Handling

### Response Types

```typescript
function divide(a: uint, b: uint): Response<uint, string> {
    if (b == 0u) {
        return err("Division by zero");
    }
    return ok(a / b);
}
```

### Unwrapping

```typescript
// Force unwrap (panics if none/err)
let value = maybeValue!;

// Unwrap with default
let value = maybeValue ?? defaultValue;

// Try unwrap (propagates error)
let value = try!(riskyOperation());
```

## Best Practices

### Code Organization

```typescript
// 1. Constants at the top
const TOKEN_NAME: string = "MyToken";
const MAX_SUPPLY: uint = 1000000u;

// 2. Type aliases
type Amount = uint;
type Address = principal;

// 3. Maps
map balances<Address, Amount>;

// 4. State variables
let totalSupply: Amount = 0u;

// 5. Public functions
@public
function mint(amount: Amount): Response<bool, uint> { }

// 6. Read-only functions
@readonly
function getSupply(): Amount { }

// 7. Private helpers
function validateAmount(amount: Amount): bool { }
```

### Error Codes

```typescript
const ERR_UNAUTHORIZED: uint = 100u;
const ERR_INSUFFICIENT_BALANCE: uint = 101u;
const ERR_INVALID_AMOUNT: uint = 102u;
```

## See Also

- [Examples](examples.md) - Practical code examples
- [API Documentation](api.md) - Python API reference
- [CLI Reference](cli.md) - Command-line interface
