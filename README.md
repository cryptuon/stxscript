# StxScript

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/cryptuon/stxscript)

> A TypeScript-inspired transpiler for writing Stacks blockchain smart contracts

StxScript provides a familiar, expressive syntax for writing Clarity smart contracts on the Stacks blockchain. Write code that looks like TypeScript, compile to optimized Clarity.

## 🚀 Quick Start

```bash
# Install StxScript
pip install stxscript

# Create a simple contract
echo 'let balance: uint = 1000u;' > example.stx

# Transpile to Clarity
stxscript example.stx example.clar
```

## ✨ Features

- **Familiar Syntax**: TypeScript-inspired syntax for Clarity development
- **Type Safety**: Static typing with type inference
- **Zero Runtime**: Compiles to native Clarity with no overhead
- **Developer Friendly**: Clear error messages and helpful tooling

## 📦 Installation

### Using pip

```bash
pip install stxscript
```

### Using Poetry (Development)

```bash
git clone https://github.com/cryptuon/stxscript.git
cd stxscript
poetry install
poetry shell
```

## 🛠️ Usage

### Command Line

```bash
# Basic transpilation
stxscript input.stx output.clar

# Multiple files
stxscript src/*.stx --output-dir build/
```

### Python API

```python
from stxscript import StxScriptTranspiler

transpiler = StxScriptTranspiler()
clarity_code = transpiler.transpile("""
let token_name: string = "MyToken";
const MAX_SUPPLY: uint = 1000000u;
""")
print(clarity_code)
```

## 📝 Language Features

### Variables and Constants

```typescript
// Variables with type annotations
let balance: uint = 1000u;
let name: string = "Alice";

// Type inference
let count = 42;  // inferred as uint

// Constants
const MAX_SUPPLY: uint = 1000000u;
```

### Functions

```typescript
@public
function transfer(to: principal, amount: uint): Response<bool, string> {
    // Function implementation
}

@readable
function get_balance(account: principal): uint {
    // Read-only function
}
```

### Current Language Support

**✅ Implemented:**
- Variable declarations (`let`, `const`)
- Basic types (`int`, `uint`, `bool`, `string`, `principal`)
- Function declarations with decorators
- Type annotations and inference

**🚧 Coming Soon:**
- Control flow (`if/else`, loops)
- Complex expressions and operators
- Classes, traits, and maps
- Error handling (`try/catch`)

## 📖 Documentation

- [Quick Start Guide](docs/quick-start.md) - Get started in 5 minutes
- [Installation Guide](docs/installation.md) - Setup instructions
- [Language Reference](docs/language-reference.md) - Complete syntax guide
- [API Documentation](docs/api.md) - Python API reference
- [CLI Reference](docs/cli.md) - Command-line usage
- [Examples](docs/examples.md) - Real-world code examples
- [Development Roadmap](docs/roadmap.md) - Feature timeline & milestones
- [Contributing Guide](docs/contributing.md) - How to contribute

## 🏗️ Development Status

StxScript is currently in **alpha** development. The core transpiler is functional for basic variable and constant declarations. We're actively working on expanding language features.

### Roadmap

**Current (v0.1.0 - Alpha):**
- ✅ Core transpiler infrastructure
- ✅ Basic variable/constant support
- ✅ Function declarations with decorators
- ✅ CLI and Python API

**Next Major Phases:**
- 🎯 **Phase 1 (v0.2.0)**: Expression System - Arithmetic, comparisons, function bodies
- 🎯 **Phase 2 (v0.3.0)**: Control Flow - If/else, match expressions, error handling
- 🎯 **Phase 3 (v0.4.0)**: Data Structures - Lists, tuples, maps, optionals
- 🎯 **Phase 4 (v0.5.0)**: Advanced Features - Lambdas, traits, modules
- 🎯 **Phase 5 (v1.0.0)**: Developer Experience - IDE support, tooling, formatting

📋 **[View Complete Roadmap](docs/roadmap.md)** for detailed timelines and technical plans.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Stacks Blockchain](https://www.stacks.co/)
- [Clarity Language](https://docs.stacks.co/docs/clarity/)
- [GitHub Issues](https://github.com/cryptuon/stxscript/issues)
- [Documentation](docs/)

---

**Note**: StxScript is experimental software. Use in production at your own risk.