# Types

StxScript has a static type system that maps directly to Clarity's type system. All types are known at compile time.

## Primitive Types

| StxScript | Clarity | Description | Example |
|-----------|---------|-------------|---------|
| `int` | `int` | Signed 128-bit integer | `-42` |
| `uint` | `uint` | Unsigned 128-bit integer | `42u` |
| `bool` | `bool` | Boolean | `true`, `false` |
| `string` | `(string-utf8 N)` | UTF-8 string | `"hello"` |
| `principal` | `principal` | Stacks address | `tx-sender` |
| `buffer<N>` | `(buff N)` | Fixed-size byte buffer | `0x1234` |

### Integer Literals

Unsigned integers require the `u` suffix. Signed integers have no suffix:

```typescript
let signed: int = -42;        // Signed
let unsigned: uint = 42u;     // Unsigned (note the 'u')
let large: uint = 1000000u;   // Large unsigned
```

**Generated Clarity:**
```lisp
(define-data-var signed int -42)
(define-data-var unsigned uint u42)
(define-data-var large uint u1000000)
```

Clarity integers are 128-bit, so the valid range is:
- `int`: -2^127 to 2^127 - 1
- `uint`: 0 to 2^128 - 1

### Boolean Literals

Both `bool` and `boolean` are accepted as type names:

```typescript
let active: bool = true;
let complete: boolean = false;  // 'boolean' also works
```

### String Literals

Strings are UTF-8 encoded. The Clarity output includes the string length:

```typescript
let name: string = "Hello";
```

**Generated Clarity:**
```lisp
(define-data-var name (string-utf8 5) u"Hello")
```

### Principal Literals

Principals represent Stacks addresses. Standard principals start with `SP` (mainnet) or `ST` (testnet):

```typescript
let wallet: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7;
let contract: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7.my-contract;
```

The special value `tx-sender` refers to the transaction sender:

```typescript
let owner: principal = tx-sender;
```

### Buffer Literals

Buffers are fixed-size byte arrays. Specify the size in the type:

```typescript
let small: buffer<4> = 0x1234abcd;
let hash: buffer<32> = 0xabcdef;
```

**Generated Clarity:**
```lisp
(define-data-var small (buff 4) 0x1234abcd)
(define-data-var hash (buff 32) 0xabcdef)
```

If no size is specified, a default size is used:

```typescript
let data: buffer = 0x1234;  // Default buffer size
```

## Complex Types

### Optional

Represents a value that may or may not be present. Equivalent to Clarity's `optional` type:

```typescript
let maybe: Optional<uint> = some(42u);
let empty: Optional<uint> = none;
```

**Generated Clarity:**
```lisp
(define-data-var maybe (optional uint) (some u42))
(define-data-var empty (optional uint) none)
```

See [Error Handling](error-handling.md) for unwrapping optionals.

### Response

Represents a success or failure result. Every public function in Clarity must return a Response:

```typescript
let success: Response<uint, string> = ok(100u);
let failure: Response<uint, string> = err("failed");
```

**Generated Clarity:**
```lisp
(ok u100)
(err u"failed")
```

The first type parameter is the success type, the second is the error type.

### List

Fixed-length sequences of values of the same type:

```typescript
let numbers: List<uint> = [1u, 2u, 3u];
let names: List<string> = ["Alice", "Bob"];
```

**Generated Clarity:**
```lisp
(list u1 u2 u3)
(list u"Alice" u"Bob")
```

### Tuple

Named field collections (similar to structs or objects):

```typescript
let user: { name: string, age: uint } = { name: "Alice", age: 30u };
```

Access fields with dot notation:

```typescript
let userName: string = user.name;
let userAge: uint = user.age;
```

**Generated Clarity:**
```lisp
(define-data-var user { name: (string-utf8 5), age: uint } { name: u"Alice", age: u30 })
(get name user)
(get age user)
```

### Map

Key-value storage declared at the contract level:

```typescript
map balances<principal, uint>;
map allowances<{ owner: principal, spender: principal }, uint>;
```

**Generated Clarity:**
```lisp
(define-map balances principal uint)
(define-map allowances { owner: principal, spender: principal } uint)
```

See [Data Structures](data-structures.md) for map operations.

## Type Aliases

Create named types for better readability:

```typescript
type Amount = uint;
type Address = principal;
type UserBalance = { address: Address, amount: Amount };
```

Type aliases are resolved at compile time and have no runtime overhead:

```typescript
let transfer: Amount = 1000u;
// Compiles identically to: let transfer: uint = 1000u;
```

You can alias complex types:

```typescript
type TokenResult = Response<bool, uint>;
type MaybeAmount = Optional<uint>;
type Balances = List<uint>;
```

## Generics

Functions can be parameterized over types:

```typescript
function identity<T>(value: T): T {
    return value;
}

function pair<T, U>(first: T, second: U): { a: T, b: U } {
    return { a: first, b: second };
}
```

Generic type parameters are resolved at the call site:

```typescript
let x = identity<uint>(42u);
let p = pair<uint, string>(1u, "hello");
```

## Type Inference

StxScript can infer types from literal values:

```typescript
let count = 42u;      // Inferred as uint
let active = true;    // Inferred as bool
let name = "Token";   // Inferred as string
```

Explicit type annotations are recommended for clarity and documentation, but not always required.

## Next Steps

- [Variables & Constants](variables.md) - Using types in declarations
- [Functions](functions.md) - Types in function signatures
- [Error Handling](error-handling.md) - Working with Optional and Response
