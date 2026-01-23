# Language Overview

StxScript is a TypeScript-inspired language that transpiles to Clarity, the smart contract language for the Stacks blockchain. It provides familiar syntax while generating valid, safe Clarity code.

## Relationship to Clarity

Clarity is a decidable, non-Turing-complete language designed for smart contracts. It uses Lisp-like S-expressions. StxScript gives you an imperative, C-style syntax that compiles down to these S-expressions, making Clarity development accessible to developers familiar with TypeScript, JavaScript, or Rust.

Key constraints inherited from Clarity:

- No unbounded loops (for/while compile to bounded `fold`)
- All types are known at compile time
- No dynamic dispatch
- No recursion
- All values are immutable by default (variables use `var-get`/`var-set` under the hood)

## Basic Syntax

### Statements

All statements end with semicolons:

```typescript
let balance: uint = 100u;
const MAX_SUPPLY: uint = 1000000u;
```

### Comments

StxScript supports three comment styles:

```typescript
// Single-line comment

/* Multi-line
   comment */

/// Documentation comment (used by doc generator)
```

Documentation comments (`///`) placed before functions or declarations are extracted by `stxscript doc` for automatic documentation generation.

### Naming Conventions

StxScript uses camelCase for variables and functions, and UPPER_SNAKE_CASE for constants:

```typescript
// Variables: camelCase or snake_case
let totalSupply: uint = 0u;
let total_supply: uint = 0u;  // also valid

// Constants: UPPER_SNAKE_CASE
const MAX_SUPPLY: uint = 1000000u;
const ERR_UNAUTHORIZED: uint = 100u;

// Functions: camelCase or snake_case
function getBalance(account: principal): uint { }
function get_balance(account: principal): uint { }
```

Note: When generating Clarity, camelCase identifiers are converted to kebab-case (e.g., `getBalance` becomes `get-balance`). Constants retain their original casing.

### Code Organization

The recommended order for contract declarations:

```typescript
// 1. Constants (error codes, configuration)
const TOKEN_NAME: string = "MyToken";
const ERR_UNAUTHORIZED: uint = 100u;

// 2. Type aliases
type Amount = uint;

// 3. Map declarations
map balances<principal, Amount>;

// 4. State variables
let total_supply: Amount = 0u;

// 5. Public functions
@public
function mint(amount: Amount): Response<bool, uint> { }

// 6. Read-only functions
@readonly
function get_supply(): Amount { }

// 7. Private helper functions
function validate(amount: Amount): bool { }
```

## How Transpilation Works

StxScript goes through a multi-stage pipeline:

1. **Parsing**: The Lark LALR parser processes your `.stx` file using the grammar
2. **AST Building**: The parse tree is converted into typed AST nodes
3. **Semantic Analysis**: Types are checked, scopes are validated, traits are verified
4. **Code Generation**: The AST is converted to Clarity S-expressions

For example, this StxScript:

```typescript
let counter: uint = 0u;

@public
function increment(): Response<uint, uint> {
    counter = counter + 1u;
    return ok(counter);
}
```

Goes through the pipeline and produces:

```lisp
(define-data-var counter uint u0)

(define-public (increment)
  (begin
    (var-set counter (+ (var-get counter) u1))
    (ok (var-get counter))))
```

## Next Steps

- [Types](types.md) - The type system
- [Variables & Constants](variables.md) - Declaring state
- [Functions](functions.md) - Defining contract interfaces
