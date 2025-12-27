# StxScript Documentation

**StxScript** is a TypeScript-inspired language that transpiles to Clarity, the smart contract language for the Stacks blockchain.

Write smart contracts with familiar syntax, get valid Clarity output.

## Why StxScript?

- **Familiar Syntax**: If you know TypeScript, you know StxScript
- **Type Safety**: Full type inference and checking at compile time
- **Modern Tooling**: LSP server, VS Code extension, formatter, linter
- **Production Ready**: 146 tests, semantic analysis, multi-error reporting

## Quick Example

**StxScript:**
```typescript
const TOKEN_NAME: string = "MyToken";
const MAX_SUPPLY: uint = 1000000u;

let total_supply: uint = 0u;
map balances<principal, uint>;

@public
function mint(amount: uint): Response<bool, uint> {
    if (total_supply + amount > MAX_SUPPLY) {
        return err(1u);
    }
    total_supply = total_supply + amount;
    return ok(true);
}

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
(define-constant TOKEN_NAME u"MyToken")
(define-constant MAX_SUPPLY u1000000)
(define-data-var total_supply uint u0)
(define-map balances principal uint)

(define-public (mint (amount uint))
  (if (> (+ (var-get total_supply) amount) MAX_SUPPLY)
    (err u1)
    (begin
      (var-set total_supply (+ (var-get total_supply) amount))
      (ok true))))

(define-read-only (get-balance (account principal))
  (default-to u0 (map-get? balances account)))
```

## Installation

```bash
pip install stxscript
```

## Quick Start

```bash
# Create a new project
stxscript new my-token --template token

# Transpile a file
stxscript build contract.stx contract.clar

# Start development mode
stxscript watch src/ --output build/
```

## Documentation

- [Getting Started](getting-started.md) - Installation and first contract
- [Language Guide](language-guide.md) - Complete language reference
- [CLI Reference](cli-reference.md) - Command-line tools
- [Testing](testing.md) - Contract testing framework
- [IDE Setup](ide-setup.md) - VS Code extension and LSP

## Features

### Language Features
- Variables and constants
- Functions with `@public`, `@readonly` decorators
- Control flow (if/else, match, for, while)
- Data structures (lists, tuples, maps)
- Generic types and type aliases
- Lambda expressions
- Traits and interfaces
- Import/export system

### Developer Tools
- **CLI**: `build`, `fmt`, `lint`, `check`, `new`, `watch`, `test`, `pkg`
- **LSP Server**: Real-time diagnostics, autocomplete, go to definition
- **VS Code Extension**: Syntax highlighting, snippets, integrated LSP
- **Testing Framework**: Mock blockchain, contract assertions
- **Package Manager**: Semantic versioning, dependency resolution

## Version

Current version: **0.3.0** (Production Ready)

## License

MIT License

## Links

- [GitHub Repository](https://github.com/cryptuon/stxscript)
- [Issue Tracker](https://github.com/cryptuon/stxscript/issues)
