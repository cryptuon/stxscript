# Control Flow

StxScript provides familiar control flow constructs that compile to Clarity's functional equivalents.

## If/Else

Conditional branching with `if` and optional `else`:

```typescript
if (balance > amount) {
    balance = balance - amount;
} else {
    return err(ERR_INSUFFICIENT_BALANCE);
}
```

**Generated Clarity:**
```lisp
(if (> (var-get balance) amount)
  (var-set balance (- (var-get balance) amount))
  (err ERR_INSUFFICIENT_BALANCE))
```

In Clarity, `if` is an expression that always requires both branches. If you omit the `else`, the compiler generates an appropriate default.

### Nested If/Else

```typescript
if (amount == 0u) {
    return err(1u);
} else if (amount > MAX_SUPPLY) {
    return err(2u);
} else {
    return ok(true);
}
```

### Ternary Operator

For simple conditional expressions:

```typescript
let result = condition ? value1 : value2;
let fee = amount > 1000u ? 10u : 5u;
```

**Generated Clarity:**
```lisp
(if condition value1 value2)
(if (> amount u1000) u10 u5)
```

## Match Expressions

Pattern matching on Optional and Response types:

### Matching Optionals

```typescript
match maybe_value {
    some(v) => v,
    none => 0u
}
```

**Generated Clarity:**
```lisp
(match maybe_value
  v v
  u0)
```

This is equivalent to Clarity's `match` on optional values. The `some` branch binds the inner value to the variable name.

### Matching Responses

```typescript
match result {
    ok(value) => value,
    err(e) => 0u
}
```

**Generated Clarity:**
```lisp
(match result
  value value
  e u0)
```

### Match in Functions

Match is commonly used in read-only functions to handle optional map lookups:

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

## For Loops

For loops compile to Clarity's `fold` operation over a generated list. Since Clarity has no unbounded iteration, the loop bounds must be known:

```typescript
for (let i = 0; i < 10; i = i + 1) {
    sum = sum + i;
}
```

**Generated Clarity:**
```lisp
(fold fold-helper (list 0 1 2 3 4 5 6 7 8 9) u0)
```

The compiler generates a helper function and a list of the iteration range.

### Loop Structure

The for loop syntax is:

```
for (let <var> = <start>; <var> < <end>; <var> = <var> + <step>) {
    <body>
}
```

- `start`: Initial value (must be an integer literal)
- `end`: Upper bound (must be deterministic)
- `step`: Increment amount

### Practical Example

```typescript
@public
function sum_to(limit: uint): Response<uint, uint> {
    let total: uint = 0u;
    for (let i = 0; i < limit; i = i + 1) {
        total = total + i;
    }
    return ok(total);
}
```

## While Loops

While loops also compile to bounded iteration using `fold`. The compiler generates a bounded fold with a maximum iteration count:

```typescript
while (count < limit) {
    count = count + 1;
}
```

**Generated Clarity:**
```lisp
(fold while-helper
  (list true true true ... true)  ;; bounded iteration list
  { count: (var-get count) })
```

### Bounded Execution

Since Clarity does not allow unbounded loops, while loops have a compile-time maximum iteration count. The compiler generates a list of that length for the fold:

```typescript
// This compiles to at most N iterations
while (condition) {
    // body
}
```

### Practical Example

```typescript
@public
function find_threshold(target: uint): Response<uint, uint> {
    let value: uint = 1u;
    while (value < target) {
        value = value * 2u;
    }
    return ok(value);
}
```

## Control Flow in Public Functions

Public functions commonly combine control flow with error handling:

```typescript
@public
function safe_transfer(to: principal, amount: uint): Response<bool, uint> {
    // Guard: check amount
    if (amount == 0u) {
        return err(ERR_INVALID_AMOUNT);
    }

    // Guard: check balance
    let sender_balance = get_balance(tx-sender);
    if (sender_balance < amount) {
        return err(ERR_INSUFFICIENT_BALANCE);
    }

    // Perform transfer
    balances.set(tx-sender, sender_balance - amount);
    balances.set(to, get_balance(to) + amount);

    return ok(true);
}
```

## Next Steps

- [Error Handling](error-handling.md) - Response and Optional patterns
- [Data Structures](data-structures.md) - Iterating over collections
- [Expressions](expressions.md) - Conditions and comparisons
