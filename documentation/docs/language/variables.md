# Variables & Constants

StxScript provides two kinds of declarations for storing values: mutable variables (`let`) and immutable constants (`const`).

## Variables

Variables are declared with `let` and compile to Clarity's `define-data-var`. They represent mutable contract state.

```typescript
let balance: uint = 1000u;
let owner: principal = tx-sender;
let is_active: bool = true;
```

**Generated Clarity:**
```lisp
(define-data-var balance uint u1000)
(define-data-var owner principal tx-sender)
(define-data-var is-active bool true)
```

### Reading Variables

In the generated Clarity, reading a variable uses `var-get`:

```typescript
// StxScript
let current = balance;

// Generated Clarity equivalent
(var-get balance)
```

### Updating Variables

Assignment uses `=` and compiles to `var-set`:

```typescript
// StxScript
balance = balance + 100u;

// Generated Clarity
(var-set balance (+ (var-get balance) u100))
```

### Type Inference

You can omit the type annotation when the type is obvious from the literal:

```typescript
let count = 42u;       // Inferred as uint
let name = "Token";    // Inferred as string
let active = true;     // Inferred as bool
```

Explicit annotations are recommended for readability:

```typescript
let count: uint = 42u;  // Preferred
```

## Constants

Constants are declared with `const` and compile to Clarity's `define-constant`. They are immutable and evaluated once at deployment.

```typescript
const TOKEN_NAME: string = "MyToken";
const MAX_SUPPLY: uint = 1000000u;
const DECIMALS: uint = 6u;
const CONTRACT_OWNER: principal = tx-sender;
```

**Generated Clarity:**
```lisp
(define-constant TOKEN_NAME u"MyToken")
(define-constant MAX_SUPPLY u1000000)
(define-constant DECIMALS u6)
(define-constant CONTRACT_OWNER tx-sender)
```

### Error Code Pattern

A common pattern is defining error codes as constants:

```typescript
const ERR_UNAUTHORIZED: uint = 100u;
const ERR_INSUFFICIENT_BALANCE: uint = 101u;
const ERR_INVALID_AMOUNT: uint = 102u;
const ERR_NOT_FOUND: uint = 103u;
```

These are used with Response types in public functions:

```typescript
@public
function transfer(amount: uint): Response<bool, uint> {
    if (amount == 0u) {
        return err(ERR_INVALID_AMOUNT);
    }
    return ok(true);
}
```

### Constants vs Variables

| | `const` | `let` |
|---|---------|-------|
| Clarity | `define-constant` | `define-data-var` |
| Mutability | Immutable | Mutable via `var-set` |
| Gas cost | Cheaper to read | Requires `var-get` |
| Use case | Configuration, error codes | Contract state |

Use `const` for values that never change. Use `let` for state that updates during contract execution.

### Semantic Checks

The semantic analyzer catches assignment to constants:

```typescript
const MAX: uint = 100u;
MAX = 200u;  // Error: Cannot assign to constant 'MAX'
```

It also catches duplicate declarations:

```typescript
let x: uint = 1u;
let x: uint = 2u;  // Error: Duplicate variable 'x'
```

## Type Aliases

Type aliases create named types using `type`:

```typescript
type Amount = uint;
type Address = principal;
type Balance = { amount: uint, locked: bool };
```

They can be used anywhere a type is expected:

```typescript
let transfer_amount: Amount = 1000u;
let recipient: Address = tx-sender;

map balances<Address, Amount>;

@public
function send(to: Address, value: Amount): Response<bool, uint> {
    return ok(true);
}
```

Type aliases are resolved at compile time with zero runtime cost. They exist purely for code readability and documentation.

### Aliasing Complex Types

```typescript
type TokenResult = Response<bool, uint>;
type MaybeBalance = Optional<uint>;
type UserRecord = { name: string, balance: uint, active: bool };
```

## Next Steps

- [Functions](functions.md) - Using variables in function bodies
- [Types](types.md) - Full type system reference
- [Data Structures](data-structures.md) - Maps and lists
