# StxScript: Language Specification

## 1. Basic Types

### 1.1 Primitive Types
- `int`: Maps to Clarity's `int`
  - Range: -2^127 to 2^127 - 1
- `uint`: Maps to Clarity's `uint`
  - Range: 0 to 2^128 - 1
- `boolean`: Maps to Clarity's `bool`
  - Values: `true` or `false`
- `string`: Maps to Clarity's `(string-utf8 <max-len>)`
  - UTF-8 encoded
  - Maximum length must be specified during declaration
- `buffer`: Maps to Clarity's `(buff <max-len>)`
  - Fixed-length byte buffers
  - Declared with max length, e.g., `let buf: buffer = buffer(10);`

### 1.2 Complex Types
- `list`: Maps to Clarity's `list`
  - Homogeneous lists only
  - Fixed length, defined at creation time
  - Syntax: `let myList: list<int> = [1, 2, 3];`
- `tuple`: Maps to Clarity's `tuple`
  - Defined using object literal syntax: `{ key1: value1, key2: value2 }`
- `optional`: Maps to Clarity's `optional`
  - Represents a value that may or may not be present
  - Syntax: `let optValue: optional<int> = some(5);` or `let optValue: optional<int> = none();`

### 1.3 Special Types
- `principal`: Represents a Stacks address or contract identifier
  - Syntax: `let addr: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7';`
- `trait`: Represents a set of function signatures
  - Defined using the `trait` keyword

## 2. Variables and Constants

- Use `let` for variable declaration (immutable by default)
- Use `const` for explicitly constant values
- Variables must be initialized at declaration

Example:
```typescript
let x: int = 5;
const MAX_VALUE: uint = 100;
```

# StxScript: Language Specification

## 3. Functions

### 3.1 Function Declaration
- Use `function` keyword for named function declaration
- Use arrow syntax for lambda functions
- Functions are private by default

Example:
```typescript
// Named function
function add(a: int, b: int): int {
  return a + b;
}

// Lambda function
const multiply = (a: int, b: int): int => a * b;

// Lambda function with block body
const divide = (a: int, b: int): int => {
  if (b === 0) {
    throw "Division by zero";
  }
  return a / b;
};
```

### 3.2 Function Decorators
- `@public`: Exposes function as a public contract call
- `@readable`: Marks function as read-only
- `@private`: Explicitly marks a function as private (default behavior)

Example:
```typescript
@public
function transfer(sender: principal, recipient: principal, amount: uint): boolean {
  // Implementation
}

@readable
function getBalance(account: principal): uint {
  // Implementation
}
```

## 4. Control Structures

### 4.1 Conditionals
- `if`, `else if`, `else` statements
- Ternary operator: `condition ? trueValue : falseValue`

### 4.2 Loops and Iteration
- `map`: Applies a function to each element of a list
- `filter`: Creates a new list with elements that pass a test
- `fold`: Reduces a list to a single value

Example:
```typescript
let doubled: list<int> = map([1, 2, 3], (x: int): int => x * 2);
let evens: list<int> = filter([1, 2, 3, 4], (x: int): boolean => x % 2 == 0);
let sum: int = fold([1, 2, 3, 4], 0, (acc: int, x: int): int => acc + x);
```

## 5. Error Handling

- Use `throw` keyword to raise errors
- Use `try`/`catch` for error handling

Example:
```typescript
if (amount > balance) {
  throw "Insufficient balance";
}

try {
  // code that might throw an error
} catch (error: string) {
  // handle error
}
```

## 6. Clarity-specific Features

### 6.1 Built-in Functions
- Clarity's built-in functions are available with a `clarity.` prefix

Example:
```typescript
let hash: buffer = clarity.keccak256(data);
let tx_sender: principal = clarity.txSender();
```

### 6.2 Contract Calls
- Use `Contract.function()` syntax for contract calls

Example:
```typescript
let result: boolean = TokenContract.transfer(sender, recipient, amount);
```

### 6.3 Traits
- Define traits using the `trait` keyword

Example:
```typescript
trait TokenTrait {
  transfer(sender: principal, recipient: principal, amount: uint): boolean;
  getBalance(account: principal): uint;
}
```

### 6.4 Implementing Traits
- Use `implements` keyword to indicate a contract implements a trait

Example:
```typescript
@contract
class MyToken implements TokenTrait {
  // Implementation of trait functions
}
```

## 7. Data Persistence

### 7.1 Data Variables
- Declare persistent variables with `@data` decorator

Example:
```typescript
@data
let totalSupply: uint = 1000000;
```

### 7.2 Data Maps
- Declare data maps with `@map` decorator

Example:
```typescript
@map({ key: principal, value: uint })
const balances: Map<principal, uint> = new Map<principal, uint>();

function getBalance(account: principal): uint {
  return balances.get(account) ?? 0;
}

function setBalance(account: principal, newBalance: uint): void {
  balances.set(account, newBalance);
}
```

## 8. Assets

- Define assets using the `@asset` decorator

Example:
```typescript
@asset
class NFT {
  id: uint;
  owner: principal;
}
```

## 9. Comments

- Single-line comments: `// Comment`
- Multi-line comments: `/* Comment */`
- Documentation comments: `/** Documentation */`

## 10. Modules and Imports

- No module system (to align with Clarity's single-file contracts)
- All code for a contract must be in a single file

## 11. Type Assertions and Checks

- Use `as` for type assertions (compile-time check)
- Use `is` for type checks (runtime check)

Example:
```typescript
let value: unknown = someFunction();
let numValue: int = value as int; // Type assertion

if (value is int) {
  // value is treated as int within this block
  let result: int = value + 1;
}
```

## 12. Constants and Literal Syntax

- Support for hex literals: `0xff`
- Support for binary literals: `0b1010`
- Support for underscores in numeric literals: `1_000_000`

## 13. Block Heights and Times

- Access block information using `clarity.block`

Example:
```typescript
let currentHeight: uint = clarity.block.height;
let currentTime: uint = clarity.block.time;
```

## 14. Response Constructors

- Use `ok()` and `err()` for creating responses
- Responses are used for return values of public functions

Example:
```typescript
@public
function divideIfEven(a: int, b: int): Response<int, string> {
  if (a % 2 !== 0) {
    return err("First argument must be even");
  }
  if (b === 0) {
    return err("Cannot divide by zero");
  }
  return ok(a / b);
}
```

## 15. Unwrapping Optional and Response Types

- Use `!` operator to unwrap optional values (throws an error if `none`)
- Use `.unwrap()` method to unwrap response values (throws an error if `err`)
- Use `??` operator for optional chaining

Example:
```typescript
let optValue: optional<int> = some(5);
let value: int = optValue!;  // Unwraps to 5

let response: Response<int, string> = ok(10);
let result: int = response.unwrap();  // Unwraps to 10

let deepOptional: optional<{x: optional<int>}> = some({x: some(5)});
let deepValue: int = deepOptional?.x ?? 0;  // Returns 5 if all optionals are some, 0 otherwise
```

## 16. List Operations

- `list:append`: Append an element to a list
- `list:len`: Get the length of a list
- `list:element-at?`: Safely get an element at a specific index

Example:
```typescript
let myList: list<int> = [1, 2, 3];
let longerList: list<int> = clarity.listAppend(myList, 4);
let listLength: uint = clarity.listLen(longerList);
let thirdElement: optional<int> = clarity.listElementAt(longerList, 2);
```

## 17. Bitwise Operations

- Support for bitwise operations: `&`, `|`, `^`, `~`, `<<`, `>>`

Example:
```typescript
let a: int = 5;  // 101 in binary
let b: int = 3;  // 011 in binary
let bitwiseAnd: int = a & b;  // 001 (1 in decimal)
let bitwiseOr: int = a | b;   // 111 (7 in decimal)
let bitwiseXor: int = a ^ b;  // 110 (6 in decimal)
let bitwiseNot: int = ~a;     // 11111010 (-6 in decimal, assuming 8-bit integers)
let leftShift: int = a << 1;  // 1010 (10 in decimal)
let rightShift: int = a >> 1; // 10 (2 in decimal)
```

## 18. Contract Calls with Block Limits

- Specify block height or time limits for contract calls

Example:
```typescript
let result: boolean = TokenContract.transfer(sender, recipient, amount).limitHeight(10);
let otherResult: int = OtherContract.someFunction().limitTime(1000);
```

## 19. Read-only Calls

- Use `.readonly` for read-only contract calls

Example:
```typescript
let balance: uint = TokenContract.getBalance(account).readonly();
```

## 20. Named Arguments

- Support for named arguments in function calls

Example:
```typescript
function transfer(from: principal, to: principal, amount: uint): boolean {
  // Implementation
}

let result: boolean = transfer({from: sender, to: recipient, amount: 100});
```

## 21. Tuple Operations

- Access tuple elements using dot notation
- Destructure tuples in function parameters

Example:
```typescript
let person: {name: string, age: uint} = {name: "Alice", age: 30};
let name: string = person.name;

function printPerson({name, age}: {name: string, age: uint}): void {
  clarity.print(`Name: ${name}, Age: ${age}`);
}
```

## 22. Parsing

- Functions for parsing strings to other types

Example:
```typescript
let intValue: int = clarity.toInt("123");
let uintValue: uint = clarity.toUint("456");
```

## 23. Composable Functions

- Support for function composition using the `compose` keyword

Example:
```typescript
const double = (x: int): int => x * 2;
const addOne = (x: int): int => x + 1;
const doublePlusOne: (x: int) => int = compose(addOne, double);
// doublePlusOne(3) would return 7
```

## 24. Memoization

- Support for memoization of pure functions using the `@memo` decorator

Example:
```typescript
@memo
function fibonacci(n: uint): uint {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}
```

## 25. Constant Time Comparison

- Provide a method for constant-time comparison of buffers (important for cryptographic operations)

Example:
```typescript
let buffer1: buffer = buffer(10);
let buffer2: buffer = buffer(10);
let areEqual: boolean = clarity.constantTimeBufferEq(buffer1, buffer2);
```

## 26. Asynchronous Mint

- Support for asynchronous minting of tokens (specific to certain Clarity use cases)

Example:
```typescript
@async
function mint(recipient: principal, amount: uint): void {
  // Implementation
}
```

## 27. Lexical Structure

- Keywords: `let`, `const`, `function`, `if`, `else`, `return`, `throw`, `try`, `catch`, `class`, `trait`, `implements`, `as`, `is`, `true`, `false`, `none`, `some`, `ok`, `err`
- Operators: `+`, `-`, `*`, `/`, `%`, `&`, `|`, `^`, `~`, `<<`, `>>`, `&&`, `||`, `!`, `<`, `>`, `<=`, `>=`, `==`, `!=`, `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `|=`, `^=`, `<<=`, `>>=`, `?`, `:`, `=>`, `??`
- Delimiters: `(`, `)`, `{`, `}`, `[`, `]`, `,`, `.`, `;`
- Literals:
  - Integer: `123`, `-456`
  - Unsigned Integer: `123u`
  - Hexadecimal: `0xff`
  - Binary: `0b1010`
  - String: `"Hello, world!"`
  - Boolean: `true`, `false`
  - Principal: `'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7`

## 28. Precedence and Associativity

[Add a table showing operator precedence and associativity]

1. Member access (`.`) - left-to-right
2. Function call (`()`) - left-to-right
3. Unary operators (`!`, `~`, `+`, `-`) - right-to-left
4. Multiplicative (`*`, `/`, `%`) - left-to-right
5. Additive (`+`, `-`) - left-to-right
6. Shift (`<<`, `>>`) - left-to-right
7. Relational (`<`, `>`, `<=`, `>=`) - left-to-right
8. Equality (`==`, `!=`) - left-to-right
9. Bitwise AND (`&`) - left-to-right
10. Bitwise XOR (`^`) - left-to-right
11. Bitwise OR (`|`) - left-to-right
12. Logical AND (`&&`) - left-to-right
13. Logical OR (`||`) - left-to-right
14. Ternary (`?:`) - right-to-left
15. Assignment (`=`, `+=`, `-=`, etc.) - right-to-left
