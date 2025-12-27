# StxScript Language Guide

Complete reference for the StxScript language.

## Basics

### Comments

```typescript
// Single-line comment

/* Multi-line
   comment */

/// Documentation comment
```

### Statements

All statements end with semicolons:

```typescript
let balance: uint = 100u;
const MAX_SUPPLY: uint = 1000000u;
```

## Types

### Primitive Types

| Type | Clarity | Description |
|------|---------|-------------|
| `int` | `int` | Signed 128-bit integer |
| `uint` | `uint` | Unsigned 128-bit integer |
| `bool` | `bool` | Boolean (true/false) |
| `string` | `string-utf8` | UTF-8 string |
| `principal` | `principal` | Stacks address |
| `buffer<N>` | `(buff N)` | Fixed-size byte buffer |

### Literals

```typescript
// Integers
let negative: int = -42;
let positive: uint = 42u;      // 'u' suffix for uint

// Booleans
let active: bool = true;

// Strings
let name: string = "Hello";

// Principals
let wallet: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7;

// Buffers
let data: buffer<32> = 0x1234abcd;
```

### Complex Types

```typescript
// Lists
let numbers: List<uint> = [1u, 2u, 3u];

// Tuples
let user: { name: string, age: uint } = { name: "Alice", age: 30u };

// Optionals
let maybe: Optional<uint> = some(42u);
let empty: Optional<uint> = none;

// Responses
let success: Response<uint, string> = ok(100u);
let failure: Response<uint, string> = err("failed");

// Maps
map balances<principal, uint>;
```

### Type Aliases

```typescript
type Amount = uint;
type Address = principal;
type UserBalance = { address: Address, amount: Amount };

let transfer: Amount = 1000u;
```

### Generics

```typescript
function identity<T>(value: T): T {
    return value;
}

function pair<T, U>(first: T, second: U): { a: T, b: U } {
    return { a: first, b: second };
}
```

## Variables

### Constants

```typescript
const TOKEN_NAME: string = "MyToken";
const MAX_SUPPLY: uint = 1000000u;
const DECIMALS: uint = 6u;
```

### Variables

```typescript
let total_supply: uint = 0u;
let owner: principal = tx-sender;

// Type inference
let count = 42u;  // Inferred as uint
```

## Functions

### Declaration

```typescript
// Private function (default)
function add(a: uint, b: uint): uint {
    return a + b;
}

// Public function
@public
function transfer(to: principal, amount: uint): Response<bool, uint> {
    return ok(true);
}

// Read-only function
@readonly
function get_balance(account: principal): uint {
    return 0u;
}
```

### Decorators

| Decorator | Clarity | Description |
|-----------|---------|-------------|
| `@public` | `define-public` | Callable externally |
| `@readonly` | `define-read-only` | No state changes |
| (none) | `define-private` | Internal only |

## Expressions

### Arithmetic

```typescript
let sum = a + b;
let diff = a - b;
let product = a * b;
let quotient = a / b;
let remainder = a % b;
```

### Comparison

```typescript
let eq = a == b;
let neq = a != b;
let lt = a < b;
let lte = a <= b;
let gt = a > b;
let gte = a >= b;
```

### Logical

```typescript
let and_result = a && b;
let or_result = a || b;
let not_result = !a;
```

### Bitwise

```typescript
let bit_and = a & b;
let bit_or = a | b;
let bit_xor = a ^ b;
let bit_not = ~a;
let left_shift = a << 2;
let right_shift = a >> 2;
```

## Control Flow

### If/Else

```typescript
if (balance > amount) {
    // transfer
} else {
    // error
}

// Ternary
let result = condition ? value1 : value2;
```

### Match

```typescript
// Match on Optional
match maybe_value {
    some(v) => v,
    none => 0u
}

// Match on Response
match result {
    ok(value) => value,
    err(e) => 0u
}
```

### Loops

```typescript
// For loop (compiles to fold)
for (let i = 0; i < 10; i = i + 1) {
    sum = sum + i;
}

// While loop (bounded)
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
let balance = balances.get(account);  // Returns Optional
balances.set(account, 100u);
balances.delete(account);
```

### Lists

```typescript
let numbers: List<uint> = [1u, 2u, 3u];

// Higher-order functions
let doubled = map(numbers, (x) => x * 2u);
let evens = filter(numbers, (x) => x % 2u == 0u);
let sum = fold(numbers, 0u, (acc, x) => acc + x);
```

### Tuples

```typescript
let user = { name: "Alice", balance: 100u };
let name = user.name;
let balance = user.balance;
```

## Lambda Expressions

```typescript
let double = (x: uint) => x * 2u;
let add = (a: uint, b: uint) => a + b;

// With higher-order functions
let result = map(numbers, (x) => x * 2u);
```

## Traits

```typescript
trait Token {
    transfer(from: principal, to: principal, amount: uint): Response<bool, uint>;
    get_balance(account: principal): uint;
}

@implements(Token)
contract MyToken {
    // Implementation
}
```

## Error Handling

### Response Types

```typescript
@public
function divide(a: uint, b: uint): Response<uint, string> {
    if (b == 0u) {
        return err("division by zero");
    }
    return ok(a / b);
}
```

### Unwrapping

```typescript
// Force unwrap (panics on none/err)
let value = maybe_value!;

// Default value
let value = maybe_value ?? 0u;

// Propagate errors
let value = try!(risky_operation());
```

## Imports

```typescript
import { TokenTrait } from "./traits";
import { utils } from "../lib/utils";

// Contract calls
let result = OtherContract.method(arg1, arg2);
```

## Best Practices

### Code Organization

```typescript
// 1. Constants
const TOKEN_NAME: string = "MyToken";
const ERR_UNAUTHORIZED: uint = 100u;

// 2. Type aliases
type Amount = uint;

// 3. Maps
map balances<principal, Amount>;

// 4. State variables
let total_supply: Amount = 0u;

// 5. Public functions
@public
function mint(amount: Amount): Response<bool, uint> { }

// 6. Read-only functions
@readonly
function get_supply(): Amount { }

// 7. Private helpers
function validate(amount: Amount): bool { }
```
