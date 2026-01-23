# Data Structures

StxScript provides maps, lists, and tuples for organizing data in contracts.

## Maps

Maps are key-value stores declared at the contract level. They are the primary mechanism for persistent storage in Clarity contracts.

### Declaration

```typescript
map balances<principal, uint>;
map allowances<{ owner: principal, spender: principal }, uint>;
map metadata<uint, { name: string, uri: string }>;
```

**Generated Clarity:**
```lisp
(define-map balances principal uint)
(define-map allowances { owner: principal, spender: principal } uint)
(define-map metadata uint { name: (string-utf8 ...), uri: (string-utf8 ...) })
```

### Reading from Maps

`get` returns an `Optional` value since the key may not exist:

```typescript
let balance = balances.get(account);  // Returns Optional<uint>
```

**Generated Clarity:**
```lisp
(map-get? balances account)
```

Use `match` or unwrap operators to handle the Optional:

```typescript
@readonly
function get_balance(account: principal): uint {
    match balances.get(account) {
        some(b) => b,
        none => 0u
    }
}
```

### Writing to Maps

`set` inserts or updates a value:

```typescript
balances.set(account, 1000u);
```

**Generated Clarity:**
```lisp
(map-set balances account u1000)
```

### Deleting from Maps

`delete` removes a key-value pair:

```typescript
balances.delete(account);
```

**Generated Clarity:**
```lisp
(map-delete balances account)
```

### Composite Keys

Maps can have tuple keys for multi-dimensional lookups:

```typescript
map allowances<{ owner: principal, spender: principal }, uint>;

@public
function approve(spender: principal, amount: uint): Response<bool, uint> {
    let key = { owner: tx-sender, spender: spender };
    allowances.set(key, amount);
    return ok(true);
}

@readonly
function get_allowance(owner: principal, spender: principal): uint {
    let key = { owner: owner, spender: spender };
    match allowances.get(key) {
        some(amount) => amount,
        none => 0u
    }
}
```

## Lists

Lists are fixed-length sequences of values of the same type.

### List Literals

```typescript
let numbers: List<uint> = [1u, 2u, 3u, 4u, 5u];
let names: List<string> = ["Alice", "Bob", "Charlie"];
let flags: List<bool> = [true, false, true];
```

**Generated Clarity:**
```lisp
(list u1 u2 u3 u4 u5)
(list u"Alice" u"Bob" u"Charlie")
(list true false true)
```

### Higher-Order Functions

StxScript provides `map`, `filter`, and `fold` for list processing:

#### map

Apply a function to each element, producing a new list:

```typescript
let doubled = map(numbers, (x) => x * 2u);
```

**Generated Clarity:**
```lisp
(map double-fn numbers)
```

#### filter

Keep elements matching a predicate:

```typescript
let evens = filter(numbers, (x) => x % 2u == 0u);
```

#### fold

Reduce a list to a single value with an accumulator:

```typescript
let sum = fold(numbers, 0u, (acc, x) => acc + x);
let product = fold(numbers, 1u, (acc, x) => acc * x);
```

**Generated Clarity:**
```lisp
(fold + numbers u0)
(fold * numbers u1)
```

### Combining Operations

```typescript
@public
function process(numbers: List<uint>): Response<uint, uint> {
    let evens = filter(numbers, (x) => x % 2u == 0u);
    let doubled = map(evens, (x) => x * 2u);
    let total = fold(doubled, 0u, (acc, x) => acc + x);
    return ok(total);
}
```

## Tuples

Tuples are named-field structures, similar to objects in TypeScript or structs in Rust.

### Creating Tuples

```typescript
let user = { name: "Alice", balance: 1000u, active: true };
let point = { x: 10, y: 20 };
```

**Generated Clarity:**
```lisp
{ name: u"Alice", balance: u1000, active: true }
{ x: 10, y: 20 }
```

### Typed Tuples

```typescript
let user: { name: string, balance: uint } = {
    name: "Alice",
    balance: 1000u
};
```

### Accessing Fields

Use dot notation to read fields:

```typescript
let userName = user.name;
let userBalance = user.balance;
```

**Generated Clarity:**
```lisp
(get name user)
(get balance user)
```

### Tuples as Function Parameters

```typescript
@public
function update_user(data: { name: string, balance: uint }): Response<bool, uint> {
    let name = data.name;
    let balance = data.balance;
    return ok(true);
}
```

### Tuples as Map Keys

Tuples are commonly used as composite map keys:

```typescript
map trades<{ maker: principal, id: uint }, { amount: uint, price: uint }>;
```

## Patterns

### Token Balance Pattern

```typescript
map balances<principal, uint>;

function credit(account: principal, amount: uint): bool {
    let current = match balances.get(account) {
        some(b) => b,
        none => 0u
    };
    balances.set(account, current + amount);
    return true;
}

function debit(account: principal, amount: uint): Response<bool, uint> {
    let current = match balances.get(account) {
        some(b) => b,
        none => 0u
    };
    if (current < amount) {
        return err(ERR_INSUFFICIENT_BALANCE);
    }
    balances.set(account, current - amount);
    return ok(true);
}
```

### Registry Pattern

```typescript
map registry<uint, { owner: principal, data: string }>;
let next_id: uint = 0u;

@public
function register(data: string): Response<uint, uint> {
    let id = next_id + 1u;
    next_id = id;
    registry.set(id, { owner: tx-sender, data: data });
    return ok(id);
}
```

## Next Steps

- [Error Handling](error-handling.md) - Handling Optional from map lookups
- [Control Flow](control-flow.md) - Iterating with for/while
- [Functions](functions.md) - Using data structures in functions
