# Functions

Functions define the interface of your contract. StxScript supports three visibility levels through decorators, along with generic functions and lambda expressions.

## Function Declarations

A basic function has a name, parameters with types, a return type, and a body:

```typescript
function add(a: uint, b: uint): uint {
    return a + b;
}
```

**Generated Clarity:**
```lisp
(define-private (add (a uint) (b uint))
  (+ a b))
```

By default, functions are private (internal to the contract).

## Decorators

Decorators control function visibility:

| Decorator | Clarity | Description |
|-----------|---------|-------------|
| (none) | `define-private` | Internal only, not callable from outside |
| `@public` | `define-public` | Callable externally, must return Response |
| `@readonly` | `define-read-only` | Callable externally, cannot modify state |

### Public Functions

Public functions are the external interface of your contract. They must return a `Response` type:

```typescript
@public
function transfer(to: principal, amount: uint): Response<bool, uint> {
    if (amount == 0u) {
        return err(1u);
    }
    return ok(true);
}
```

**Generated Clarity:**
```lisp
(define-public (transfer (to principal) (amount uint))
  (if (is-eq amount u0)
    (err u1)
    (ok true)))
```

### Read-Only Functions

Read-only functions can be called externally but cannot modify contract state (no `var-set`, no map mutations):

```typescript
@readonly
function get_balance(account: principal): uint {
    match balances.get(account) {
        some(balance) => balance,
        none => 0u
    }
}
```

**Generated Clarity:**
```lisp
(define-read-only (get-balance (account principal))
  (default-to u0 (map-get? balances account)))
```

### Private Functions

Functions without a decorator are private. They can only be called by other functions in the same contract:

```typescript
function validate_amount(amount: uint): bool {
    return amount > 0u && amount <= MAX_SUPPLY;
}
```

**Generated Clarity:**
```lisp
(define-private (validate-amount (amount uint))
  (and (> amount u0) (<= amount MAX_SUPPLY)))
```

## Parameters

Parameters require explicit type annotations:

```typescript
function process(
    sender: principal,
    amount: uint,
    memo: Optional<string>
): Response<bool, uint> {
    return ok(true);
}
```

The semantic analyzer checks argument counts at call sites:

```typescript
process(tx-sender, 100u);  // Error: Expected 3 arguments, got 2
```

## Return Types

All functions must declare a return type:

```typescript
function get_count(): uint {
    return counter;
}

@public
function reset(): Response<bool, uint> {
    counter = 0u;
    return ok(true);
}
```

The semantic analyzer validates return types match the declared type.

## Name Conversion

StxScript converts camelCase function names to kebab-case in Clarity output:

| StxScript | Clarity |
|-----------|---------|
| `getBalance` | `get-balance` |
| `transferFrom` | `transfer-from` |
| `totalSupply` | `total-supply` |

snake_case names are also converted:

| StxScript | Clarity |
|-----------|---------|
| `get_balance` | `get-balance` |
| `transfer_from` | `transfer-from` |

## Lambda Expressions

Lambda expressions (arrow functions) define inline functions:

```typescript
let double = (x: uint): uint => x * 2u;
let add = (a: uint, b: uint): uint => a + b;
```

Lambdas are commonly used with higher-order list operations:

```typescript
let doubled = map(numbers, (x) => x * 2u);
let evens = filter(numbers, (x) => x % 2u == 0u);
let sum = fold(numbers, 0u, (acc, x) => acc + x);
```

**Generated Clarity (fold example):**
```lisp
(fold + numbers u0)
```

## Generic Functions

Functions can be parameterized over types using angle brackets:

```typescript
function identity<T>(value: T): T {
    return value;
}

function swap<T, U>(a: T, b: U): { first: U, second: T } {
    return { first: b, second: a };
}
```

### Multiple Type Parameters

```typescript
function pair<T, U>(first: T, second: U): { a: T, b: U } {
    return { a: first, b: second };
}
```

### Calling Generic Functions

Type parameters can be explicitly specified:

```typescript
let x = identity<uint>(42u);
let p = pair<uint, string>(1u, "hello");
```

## Function Patterns

### Guard Pattern

Check preconditions early and return errors:

```typescript
@public
function withdraw(amount: uint): Response<bool, uint> {
    if (amount == 0u) {
        return err(ERR_INVALID_AMOUNT);
    }
    if (amount > get_balance(tx-sender)) {
        return err(ERR_INSUFFICIENT_BALANCE);
    }
    // ... proceed with withdrawal
    return ok(true);
}
```

### Delegation Pattern

Private helpers called by public functions:

```typescript
function is_authorized(caller: principal): bool {
    return caller == contract_owner;
}

@public
function admin_action(): Response<bool, uint> {
    if (!is_authorized(tx-sender)) {
        return err(ERR_UNAUTHORIZED);
    }
    return ok(true);
}
```

## Next Steps

- [Expressions](expressions.md) - Operators used in function bodies
- [Control Flow](control-flow.md) - Branching and looping
- [Error Handling](error-handling.md) - Response types in detail
