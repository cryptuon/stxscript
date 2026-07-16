# StxScript

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](https://github.com/cryptuon/stxscript)
[![Tests](https://img.shields.io/badge/tests-146%20passing-brightgreen.svg)](https://github.com/cryptuon/stxscript)

**[🌐 Site](https://stxscript.cryptuon.com/) · [📚 Docs](https://docs.cryptuon.com/stxscript/) · [📦 PyPI package](https://pypi.org/project/stxscript/) · [🔬 Cryptuon Research](https://github.com/cryptuon)**

A TypeScript-inspired transpiler for writing Clarity smart contracts on the Stacks blockchain.

Write contracts with familiar syntax — static types, decorators, and match expressions. Get valid, audit-ready Clarity output.

## Why this matters in 2026

Bitcoin is becoming a settlement layer for real applications, and Stacks is the L2 that gives Bitcoin an expressive, decidable smart-contract language: Clarity. As Bitcoin DeFi, RWA settlement, and Bitcoin-secured L2s grow, the bottleneck is people who can write Clarity. Clarity is deliberately Lisp-like and interpreted-on-chain for safety and decidability — powerful, but unfamiliar to the millions of developers who already write TypeScript.

StxScript is a **chain-abstraction / developer-tooling** layer for that gap. It gives the large TypeScript developer base an ergonomic, typed path to Clarity: familiar `function`/`const`/`match` syntax and static types up front, with predictable, reviewable Clarity as the compiled output. The Clarity you ship is what auditors read — StxScript is a front-end for authoring, not a runtime you have to trust in production.

- **For Bitcoin DeFi / RWA teams** — move faster on Stacks without hiring exclusively for Clarity experience.
- **For TypeScript developers** — a low-friction on-ramp to Bitcoin-secured smart contracts.
- **Honest framing** — StxScript covers a growing subset of Clarity, not 100%. See [Limitations & coverage](#limitations--coverage) and [ROADMAP.md](ROADMAP.md).

## Quick Start

```bash
# Install
pip install stxscript

# Transpile a contract
stxscript build contract.stx contract.clar

# Create a new project
stxscript new my-token --template token
```

## Overview

StxScript provides a multi-stage transpilation pipeline:

1. **Parsing** - Lark-based LALR grammar
2. **AST Generation** - Typed abstract syntax tree
3. **Semantic Analysis** - Type checking, scope validation, trait compliance
4. **Code Generation** - Optimized Clarity output

### Language Example

**StxScript input:**
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

**Clarity output:**
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

## Language Features

- **Variables and constants** with `let` and `const`
- **Functions** with `@public`, `@readonly` decorators
- **Type system** - int, uint, bool, string, principal, buffer, Optional, Response, List, Map, tuples
- **Type aliases and generics** - `type Amount = uint;`, `function identity<T>(x: T): T`
- **Control flow** - if/else, match expressions, for loops, while loops
- **Lambda expressions** - `(x: uint) => x * 2u`
- **Traits and interfaces** - trait definitions and `@implements` contracts
- **Maps** - declaration and get/set/delete operations
- **Error handling** - Response types, unwrap (`!`), default (`??`), `try!`
- **Imports** - module system with contract calls
- **Bitwise operations** - `&`, `|`, `^`, `~`, `<<`, `>>`

## StxScript vs. writing raw Clarity

StxScript is not a replacement for understanding Clarity — it is a faster, safer way to author it. An honest comparison:

| Concern | Writing raw Clarity | StxScript |
|---------|---------------------|-----------|
| Syntax familiarity | Lisp/S-expressions; new for most devs | TypeScript-style `function`, `const`, `match`, decorators |
| Type errors | Surfaced at `clarinet check` / deploy time | Caught earlier by static analysis before code generation |
| Onboarding a TS team | Learn a new paradigm first | Productive on familiar syntax; learn Clarity semantics gradually |
| Audit surface | You audit what you wrote | You audit the generated Clarity — output stays readable and reviewable |
| Feature coverage | 100% of Clarity, always | Growing subset of Clarity (see limitations) |
| Runtime trust | None added | None added — StxScript is compile-time only; nothing ships to chain but Clarity |
| Toolchain | Clarinet, Clarity LSP | StxScript CLI + LSP + VS Code extension, emits Clarity for Clarinet |

The tradeoff is deliberate: you trade full, immediate access to every Clarity primitive for ergonomics, static typing, and a shorter path from a TypeScript background to a deployable contract. When StxScript doesn't yet cover a construct, you drop down to hand-written Clarity — the output is designed to be edited.

## CLI Commands

| Command | Description |
|---------|-------------|
| `stxscript build <input> [output]` | Transpile StxScript to Clarity |
| `stxscript fmt <files>` | Format code |
| `stxscript lint <files>` | Static analysis |
| `stxscript check <files>` | Syntax validation |
| `stxscript new <name>` | Create new project (basic/token/nft/defi templates) |
| `stxscript watch <path>` | Watch mode with auto-rebuild |
| `stxscript doc <input>` | Generate documentation |
| `stxscript test [path]` | Run contract tests |
| `stxscript pkg <command>` | Package management (init/add/remove/install/list) |

## Python API

```python
from stxscript import StxScriptTranspiler

transpiler = StxScriptTranspiler()

# Basic transpilation
clarity = transpiler.transpile('let balance: uint = 1000u;')
print(clarity)  # (define-data-var balance uint u1000)

# With error handling
result = transpiler.transpile_with_error_handling(code)
if result['success']:
    print(result['code'])
else:
    print(result['errors'])
```

## IDE Support

- **VS Code Extension** - syntax highlighting, snippets, integrated LSP
- **LSP Server** - diagnostics, autocomplete, hover info, go-to-definition
- **Vim/Neovim, Sublime, Emacs** - LSP client configuration available

Run the language server:
```bash
stxscript-lsp
```

## Limitations & coverage

StxScript compiles a growing subset of Clarity. Being specific about what it does *not* do yet is part of keeping the generated output audit-ready:

- **Clarity feature coverage is partial.** Common contract patterns (tokens, NFTs, DeFi primitives, traits, maps, Response/Optional handling) are supported. Newer or niche Clarity built-ins may not have a StxScript surface yet — you drop down to hand-written Clarity for those.
- **Output review is on you.** The transpiler emits readable Clarity, but StxScript does not replace an audit. Treat the generated `.clar` as the source of truth you review and test.
- **Not a formal verifier.** StxScript performs static type checking and linting; it does not prove functional correctness.
- **Loop constructs are bounded.** `for`/`while` compile to bounded `fold`, matching Clarity's decidability model — unbounded iteration is intentionally impossible.

For the current coverage matrix, milestones, and production-readiness plan, see **[ROADMAP.md](ROADMAP.md)**.

## Documentation

Full documentation is available in the `documentation/` directory, built with mkdocs-material:

```bash
# Serve docs locally
cd documentation && mkdocs serve
```

- [Getting Started](documentation/docs/getting-started.md) - Installation and first contract
- [Language Guide](documentation/docs/language-guide.md) - Complete language reference
- [CLI Reference](documentation/docs/cli-reference.md) - All CLI commands
- [Examples](documentation/docs/examples.md) - Real-world contract examples
- [Testing](documentation/docs/testing.md) - Contract testing framework
- [API Reference](documentation/docs/api-reference.md) - Python API
- [IDE Setup](documentation/docs/ide-setup.md) - VS Code extension and LSP
- [Contributing](documentation/docs/contributing.md) - How to contribute

## Development

### Setup

```bash
git clone https://github.com/cryptuon/stxscript.git
cd stxscript
uv venv && uv pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests
uv run python -m pytest tests/

# Run with coverage
uv run python -m pytest tests/ --cov=stxscript

# Run specific test file
uv run python -m pytest tests/test_transpiler.py -v
```

### Code Quality

```bash
uv run black stxscript/
uv run flake8 stxscript/
uv run mypy stxscript/
```

### Building Documentation

```bash
cd documentation
uv run mkdocs build    # Build static site
uv run mkdocs serve    # Local dev server at http://127.0.0.1:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and add tests
4. Run the test suite: `uv run python -m pytest tests/`
5. Submit a pull request

See [Contributing Guide](documentation/docs/contributing.md) for details.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Links

- [GitHub Repository](https://github.com/cryptuon/stxscript)
- [Issue Tracker](https://github.com/cryptuon/stxscript/issues)
- [Stacks Blockchain](https://www.stacks.co/)
- [Clarity Language](https://docs.stacks.co/docs/clarity/)

---

## Part of Cryptuon Research

`stxscript` is one of [20 open-source blockchain-infrastructure projects](https://www.cryptuon.com/projects) from **[Cryptuon Research](https://www.cryptuon.com)** — blockchain theory, shipped as protocols.

**Related projects:** [SolScript](https://solscript.cryptuon.com/) · [Zig-EVM](https://zig-evm.cryptuon.com/) · [commit-reveal](https://commit-reveal.cryptuon.com/)

Docs: [docs.cryptuon.com/stxscript](https://docs.cryptuon.com/stxscript/) · Contact: [contact@cryptuon.com](mailto:contact@cryptuon.com)
