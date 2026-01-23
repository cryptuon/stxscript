# StxScript

A TypeScript-inspired transpiler for Clarity smart contracts on the Stacks blockchain.

Write contracts with familiar syntax. Get valid, optimized Clarity output.

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

## Getting Started

```bash
pip install stxscript
stxscript new my-token --template token
cd my-token
stxscript build src/main.stx build/main.clar
```

See the [Getting Started](guide/getting-started.md) guide for a full walkthrough.

## Documentation Sections

### Guide

Step-by-step guides for common workflows:

- [Getting Started](guide/getting-started.md) - Installation, first contract, development workflow
- [Project Setup](guide/project-setup.md) - Templates, project structure, package manifest
- [Deployment](guide/deployment.md) - CI/CD, Makefile, GitHub Actions

### Language

Complete language reference, expanded with explanations and Clarity output:

- [Overview](language/overview.md) - Syntax basics, naming, transpilation pipeline
- [Types](language/types.md) - Primitive types, complex types, generics
- [Variables & Constants](language/variables.md) - State declarations, type aliases
- [Functions](language/functions.md) - Decorators, lambdas, generic functions
- [Expressions](language/expressions.md) - Operators and precedence
- [Control Flow](language/control-flow.md) - if/else, match, loops
- [Data Structures](language/data-structures.md) - Maps, lists, tuples
- [Error Handling](language/error-handling.md) - Response, Optional, unwrap
- [Traits](language/traits.md) - Interface definitions, SIP compliance
- [Modules & Imports](language/modules.md) - Cross-contract calls

### Reference

Lookup tables and API documentation:

- [CLI](reference/cli.md) - All commands and options
- [Python API](reference/api.md) - Programmatic usage
- [Clarity Mapping](reference/clarity-mapping.md) - Complete translation table
- [Configuration](reference/configuration.md) - stxscript.toml, formatter, linter config

### Tooling

Developer tools and IDE integration:

- [IDE Setup](tooling/ide-setup.md) - VS Code, Vim, Sublime, Emacs
- [Testing](tooling/testing.md) - Contract testing framework
- [Formatter & Linter](tooling/formatter-linter.md) - Code quality tools
- [Package Manager](tooling/package-manager.md) - Dependency management

## Features

- **Familiar Syntax** - TypeScript-inspired, C-style syntax
- **Type Safety** - Static types with inference, checked at compile time
- **Semantic Analysis** - Scope validation, trait compliance, type checking
- **Zero Runtime** - Compiles to native Clarity with no overhead
- **Modern Tooling** - Formatter, linter, LSP, VS Code extension
- **Testing Framework** - Mock blockchain, contract assertions
- **Package Manager** - Semantic versioning, dependency resolution

## Version

Current version: **0.3.0**

## Links

- [GitHub Repository](https://github.com/cryptuon/stxscript)
- [Issue Tracker](https://github.com/cryptuon/stxscript/issues)
- [Stacks Blockchain](https://www.stacks.co/)
- [Clarity Documentation](https://docs.stacks.co/docs/clarity/)
