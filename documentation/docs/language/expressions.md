# Expressions

StxScript supports familiar infix operators that compile to Clarity's prefix S-expressions.

## Arithmetic Operators

| Operator | Description | Clarity |
|----------|-------------|---------|
| `+` | Addition | `(+ a b)` |
| `-` | Subtraction | `(- a b)` |
| `*` | Multiplication | `(* a b)` |
| `/` | Integer division | `(/ a b)` |
| `%` | Modulo | `(mod a b)` |

```typescript
let sum = a + b;
let diff = a - b;
let product = a * b;
let quotient = a / b;
let remainder = a % b;
```

**Generated Clarity:**
```lisp
(+ a b)
(- a b)
(* a b)
(/ a b)
(mod a b)
```

Note: Division is integer division (truncates toward zero). There is no floating-point arithmetic in Clarity.

### Type Requirements

Arithmetic operators require operands of the same numeric type. You cannot mix `int` and `uint`:

```typescript
let a: uint = 10u;
let b: int = 5;
let result = a + b;  // Error: Cannot mix uint and int
```

## Comparison Operators

| Operator | Description | Clarity |
|----------|-------------|---------|
| `==` | Equal | `(is-eq a b)` |
| `!=` | Not equal | `(not (is-eq a b))` |
| `<` | Less than | `(< a b)` |
| `<=` | Less or equal | `(<= a b)` |
| `>` | Greater than | `(> a b)` |
| `>=` | Greater or equal | `(>= a b)` |

```typescript
let isEqual = a == b;
let isNotEqual = a != b;
let isLess = a < b;
let isLessOrEqual = a <= b;
let isGreater = a > b;
let isGreaterOrEqual = a >= b;
```

**Generated Clarity:**
```lisp
(is-eq a b)
(not (is-eq a b))
(< a b)
(<= a b)
(> a b)
(>= a b)
```

Comparisons return `bool` and work with numeric types and principals.

## Logical Operators

| Operator | Description | Clarity |
|----------|-------------|---------|
| `&&` | Logical AND | `(and a b)` |
| `\|\|` | Logical OR | `(or a b)` |
| `!` | Logical NOT | `(not a)` |

```typescript
let both = condition1 && condition2;
let either = condition1 || condition2;
let opposite = !condition;
```

**Generated Clarity:**
```lisp
(and condition1 condition2)
(or condition1 condition2)
(not condition)
```

Logical operators work on `bool` values only. They short-circuit: `&&` stops on the first `false`, `||` stops on the first `true`.

## Bitwise Operators

| Operator | Description | Clarity |
|----------|-------------|---------|
| `&` | Bitwise AND | `(bit-and a b)` |
| `\|` | Bitwise OR | `(bit-or a b)` |
| `^` | Bitwise XOR | `(bit-xor a b)` |
| `~` | Bitwise NOT | `(bit-not a)` |
| `<<` | Left shift | `(bit-shift-left a n)` |
| `>>` | Right shift | `(bit-shift-right a n)` |

```typescript
let andResult = a & b;
let orResult = a | b;
let xorResult = a ^ b;
let notResult = ~a;
let leftShift = a << 2;
let rightShift = a >> 2;
```

**Generated Clarity:**
```lisp
(bit-and a b)
(bit-or a b)
(bit-xor a b)
(bit-not a)
(bit-shift-left a u2)
(bit-shift-right a u2)
```

Bitwise operators work on integer types (`int` and `uint`).

## Operator Precedence

From highest to lowest:

1. `!`, `~` (unary)
2. `*`, `/`, `%`
3. `+`, `-`
4. `<<`, `>>`
5. `<`, `<=`, `>`, `>=`
6. `==`, `!=`
7. `&`
8. `^`
9. `|`
10. `&&`
11. `||`

Use parentheses to override precedence:

```typescript
let result = (a + b) * c;
let check = (x > 0) && (y < 100);
```

## Function Calls

Call functions with parentheses:

```typescript
let valid = validate_amount(100u);
let balance = get_balance(tx-sender);
```

**Generated Clarity:**
```lisp
(validate-amount u100)
(get-balance tx-sender)
```

## Next Steps

- [Control Flow](control-flow.md) - Using expressions in conditions
- [Functions](functions.md) - Expressions in function bodies
- [Data Structures](data-structures.md) - Expressions with collections
