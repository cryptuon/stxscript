# Error Handling

StxScript uses Clarity's type-safe error handling model with `Response` and `Optional` types instead of exceptions.

## Response Type

`Response<T, E>` represents either a success (`ok`) or failure (`err`):

```typescript
let success: Response<uint, string> = ok(100u);
let failure: Response<uint, string> = err("failed");
```

**Generated Clarity:**
```lisp
(ok u100)
(err u"failed")
```

### In Public Functions

All public functions must return a Response:

```typescript
@public
function divide(a: uint, b: uint): Response<uint, uint> {
    if (b == 0u) {
        return err(ERR_DIVISION_BY_ZERO);
    }
    return ok(a / b);
}
```

**Generated Clarity:**
```lisp
(define-public (divide (a uint) (b uint))
  (if (is-eq b u0)
    (err ERR_DIVISION_BY_ZERO)
    (ok (/ a b))))
```

### Error Code Pattern

Define error codes as constants for consistent error reporting:

```typescript
const ERR_UNAUTHORIZED: uint = 100u;
const ERR_INSUFFICIENT_BALANCE: uint = 101u;
const ERR_INVALID_AMOUNT: uint = 102u;
const ERR_NOT_FOUND: uint = 103u;
const ERR_ALREADY_EXISTS: uint = 104u;

@public
function transfer(to: principal, amount: uint): Response<bool, uint> {
    if (amount == 0u) {
        return err(ERR_INVALID_AMOUNT);
    }
    let balance = get_balance(tx-sender);
    if (balance < amount) {
        return err(ERR_INSUFFICIENT_BALANCE);
    }
    // ... perform transfer
    return ok(true);
}
```

## Optional Type

`Optional<T>` represents a value that may or may not exist:

```typescript
let present: Optional<uint> = some(42u);
let absent: Optional<uint> = none;
```

**Generated Clarity:**
```lisp
(some u42)
none
```

Optionals are returned by map lookups (`map.get()`) since a key may not exist in the map.

## Unwrap Operators

### Force Unwrap (`!`)

Unwraps an Optional or Response, panicking (aborting the transaction) if the value is `none` or `err`:

```typescript
let value: uint = maybe_value!;
```

**Generated Clarity:**
```lisp
(unwrap-panic maybe_value)
```

Use force unwrap only when you are certain the value exists. If the unwrap fails, the entire transaction is reverted.

### Default Value (`??`)

Provides a fallback value if the Optional is `none`:

```typescript
let value: uint = maybe_value ?? 0u;
let name: string = maybe_name ?? "Unknown";
```

**Generated Clarity:**
```lisp
(default-to u0 maybe_value)
(default-to u"Unknown" maybe_name)
```

This is the safest way to handle optionals in most cases.

### Try Unwrap (`try!`)

Propagates errors up the call stack. If the value is `err` or `none`, the current function immediately returns that error:

```typescript
let value: uint = try!(risky_operation());
```

**Generated Clarity:**
```lisp
(try! (risky-operation))
```

This is equivalent to early-return on error, similar to Rust's `?` operator.

## Matching on Results

Use `match` for exhaustive handling of Response and Optional values:

### Matching Optional

```typescript
@readonly
function get_balance(account: principal): uint {
    match balances.get(account) {
        some(balance) => balance,
        none => 0u
    }
}
```

### Matching Response

```typescript
@public
function process(input: uint): Response<uint, uint> {
    match validate(input) {
        ok(validated) => ok(validated * 2u),
        err(code) => err(code)
    }
}
```

### Nested Matching

```typescript
@public
function transfer_from(from: principal, to: principal, amount: uint): Response<bool, uint> {
    match balances.get(from) {
        some(sender_balance) => {
            if (sender_balance < amount) {
                return err(ERR_INSUFFICIENT_BALANCE);
            }
            balances.set(from, sender_balance - amount);
            match balances.get(to) {
                some(recipient_balance) => {
                    balances.set(to, recipient_balance + amount);
                },
                none => {
                    balances.set(to, amount);
                }
            }
            return ok(true);
        },
        none => err(ERR_NOT_FOUND)
    }
}
```

## Patterns

### Guard Clause Pattern

Check and fail fast:

```typescript
@public
function mint(amount: uint): Response<bool, uint> {
    if (tx-sender != contract_owner) {
        return err(ERR_UNAUTHORIZED);
    }
    if (amount == 0u) {
        return err(ERR_INVALID_AMOUNT);
    }
    if (total_supply + amount > MAX_SUPPLY) {
        return err(ERR_OVERFLOW);
    }
    total_supply = total_supply + amount;
    return ok(true);
}
```

### Safe Map Access Pattern

Always handle the `none` case from map lookups:

```typescript
function safe_get_balance(account: principal): uint {
    return balances.get(account) ?? 0u;
}
```

### Error Wrapping Pattern

Transform errors from one type to another:

```typescript
@public
function wrapped_call(): Response<bool, uint> {
    match external_call() {
        ok(result) => ok(result),
        err(e) => err(ERR_EXTERNAL_FAILURE)  // Map to local error code
    }
}
```

## Semantic Analysis

The semantic analyzer checks:

- Response type consistency in public functions
- Optional handling (warnings for unhandled optionals)
- Type compatibility between ok/err values and declared Response types

## Next Steps

- [Control Flow](control-flow.md) - Match expressions and conditionals
- [Functions](functions.md) - Return types and decorators
- [Data Structures](data-structures.md) - Maps return Optionals
