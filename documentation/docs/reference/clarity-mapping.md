# Clarity Mapping

Complete reference of how StxScript constructs map to Clarity output.

## Declarations

| StxScript | Clarity |
|-----------|---------|
| `let x: uint = 42u;` | `(define-data-var x uint u42)` |
| `const X: uint = 42u;` | `(define-constant X u42)` |
| `map balances<principal, uint>;` | `(define-map balances principal uint)` |
| `type Amount = uint;` | (resolved at compile time, no output) |

## Functions

| StxScript | Clarity |
|-----------|---------|
| `function foo(): uint { }` | `(define-private (foo) ...)` |
| `@public function foo(): Response<bool, uint> { }` | `(define-public (foo) ...)` |
| `@readonly function foo(): uint { }` | `(define-read-only (foo) ...)` |

### Parameters

```typescript
function add(a: uint, b: uint): uint { }
```
```lisp
(define-private (add (a uint) (b uint)) ...)
```

## Types

| StxScript | Clarity |
|-----------|---------|
| `int` | `int` |
| `uint` | `uint` |
| `bool` | `bool` |
| `string` | `(string-utf8 N)` |
| `principal` | `principal` |
| `buffer<N>` | `(buff N)` |
| `Optional<T>` | `(optional T)` |
| `Response<T, E>` | `(response T E)` |
| `List<T>` | `(list N T)` |
| `{ a: T, b: U }` | `{ a: T, b: U }` |

## Literals

| StxScript | Clarity |
|-----------|---------|
| `42` | `42` |
| `42u` | `u42` |
| `-42` | `-42` |
| `true` / `false` | `true` / `false` |
| `"hello"` | `u"hello"` |
| `tx-sender` | `tx-sender` |
| `'SP2J6...` | `'SP2J6...` |
| `0x1234` | `0x1234` |

## Values

| StxScript | Clarity |
|-----------|---------|
| `ok(value)` | `(ok value)` |
| `err(value)` | `(err value)` |
| `some(value)` | `(some value)` |
| `none` | `none` |
| `[1u, 2u, 3u]` | `(list u1 u2 u3)` |
| `{ a: 1u, b: 2u }` | `{ a: u1, b: u2 }` |

## Arithmetic Operators

| StxScript | Clarity |
|-----------|---------|
| `a + b` | `(+ a b)` |
| `a - b` | `(- a b)` |
| `a * b` | `(* a b)` |
| `a / b` | `(/ a b)` |
| `a % b` | `(mod a b)` |

## Comparison Operators

| StxScript | Clarity |
|-----------|---------|
| `a == b` | `(is-eq a b)` |
| `a != b` | `(not (is-eq a b))` |
| `a < b` | `(< a b)` |
| `a <= b` | `(<= a b)` |
| `a > b` | `(> a b)` |
| `a >= b` | `(>= a b)` |

## Logical Operators

| StxScript | Clarity |
|-----------|---------|
| `a && b` | `(and a b)` |
| `a \|\| b` | `(or a b)` |
| `!a` | `(not a)` |

## Bitwise Operators

| StxScript | Clarity |
|-----------|---------|
| `a & b` | `(bit-and a b)` |
| `a \| b` | `(bit-or a b)` |
| `a ^ b` | `(bit-xor a b)` |
| `~a` | `(bit-not a)` |
| `a << n` | `(bit-shift-left a n)` |
| `a >> n` | `(bit-shift-right a n)` |

## Control Flow

### If/Else

```typescript
if (condition) {
    expr1;
} else {
    expr2;
}
```
```lisp
(if condition expr1 expr2)
```

### Ternary

```typescript
condition ? value1 : value2
```
```lisp
(if condition value1 value2)
```

### Match on Optional

```typescript
match opt {
    some(v) => v,
    none => default
}
```
```lisp
(match opt v v default)
;; or: (default-to default opt)
```

### Match on Response

```typescript
match result {
    ok(v) => v,
    err(e) => fallback
}
```
```lisp
(match result v v e fallback)
```

## Loops

### For Loop

```typescript
for (let i = 0; i < 5; i = i + 1) {
    body;
}
```
```lisp
(fold fold-helper (list 0 1 2 3 4) initial-state)
```

### While Loop

```typescript
while (condition) {
    body;
}
```
```lisp
(fold while-helper bounded-list initial-state)
```

## Map Operations

| StxScript | Clarity |
|-----------|---------|
| `map.get(key)` | `(map-get? map-name key)` |
| `map.set(key, value)` | `(map-set map-name key value)` |
| `map.delete(key)` | `(map-delete map-name key)` |

## Variable Operations

| StxScript | Clarity |
|-----------|---------|
| Reading `variable` | `(var-get variable)` |
| `variable = value;` | `(var-set variable value)` |

## Unwrap Operators

| StxScript | Clarity |
|-----------|---------|
| `value!` | `(unwrap-panic value)` |
| `value ?? default` | `(default-to default value)` |
| `try!(expr)` | `(try! expr)` |

## Traits

```typescript
trait Token {
    transfer(to: principal, amount: uint): Response<bool, uint>;
}
```
```lisp
(define-trait Token
  ((transfer (principal uint) (response bool uint))))
```

```typescript
@implements(Token)
contract MyToken { }
```
```lisp
(impl-trait .Token)
```

## List Operations

| StxScript | Clarity |
|-----------|---------|
| `map(list, fn)` | `(map fn list)` |
| `filter(list, fn)` | `(filter fn list)` |
| `fold(list, init, fn)` | `(fold fn list init)` |

## Contract Calls

```typescript
OtherContract.method(arg1, arg2)
```
```lisp
(contract-call? .OtherContract method arg1 arg2)
```

## Name Conversion

| StxScript | Clarity |
|-----------|---------|
| `getBalance` (camelCase) | `get-balance` (kebab-case) |
| `get_balance` (snake_case) | `get-balance` (kebab-case) |
| `MAX_SUPPLY` (constant) | `MAX_SUPPLY` (preserved) |
