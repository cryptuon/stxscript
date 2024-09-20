# StxScript: A High-Level Language for Stacks Smart Contracts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/stxscript.svg)](https://pypi.org/project/stxscript/)

StxScript is a high-level language and transpiler for writing smart contracts on the Stacks blockchain. It provides a more familiar and expressive syntax compared to Clarity, while still compiling down to valid Clarity code.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
- [Language Overview](#language-overview)
  - [Basic Types](#basic-types)
  - [Variables and Constants](#variables-and-constants)
  - [Functions](#functions)
  - [Control Structures](#control-structures)
  - [Error Handling](#error-handling)
  - [Clarity-specific Features](#clarity-specific-features)
  - [Advanced Features](#advanced-features)
- [Examples](#examples)
- [Development](#development)
  - [Setting Up the Development Environment](#setting-up-the-development-environment)
  - [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

## Features

- Familiar syntax inspired by modern programming languages
- Static typing with type inference
- First-class support for Clarity concepts like traits, maps, and assets
- Enhanced readability and maintainability compared to raw Clarity code
- Comprehensive error messages and static analysis
- Support for complex data structures and operations
- Built-in support for common smart contract patterns

## Installation

You can install StxScript using pip:

```bash
pip install stxscript
```

For development, we recommend using Poetry:

```bash
poetry add stxscript
```

## Usage

### Command Line Interface

After installation, you can use the `stxscript` command to transpile StxScript files to Clarity:

```bash
stxscript input.stx output.clar
```

### Python API

You can also use StxScript as a library in your Python projects:

```python
from stxscript import StxScriptTranspiler

transpiler = StxScriptTranspiler()
clarity_code = transpiler.transpile(stxscript_code)
```

## Language Overview

### Basic Types

StxScript supports all Clarity types:

- `int`: Signed 128-bit integer
- `uint`: Unsigned 128-bit integer
- `bool`: Boolean (true or false)
- `principal`: Stacks address or contract identifier
- `string`: UTF-8 string
- `buffer`: Byte buffer
- `list<T>`: List of elements of type T
- `optional<T>`: Optional value of type T
- `Response<T, E>`: Response type with ok (T) and error (E) variants
- `tuple`: Named fields of varying types

### Variables and Constants

```typescript
let myVariable: int = 42;
const MY_CONSTANT: uint = 100;
```

### Functions

```typescript
@public
function add(a: int, b: int): int {
    return a + b;
}
```

### Control Structures

```typescript
if (condition) {
    // do something
} else if (otherCondition) {
    // do something else
} else {
    // fallback
}

// List operations
let doubled = map([1, 2, 3], (x) => x * 2);
let evens = filter([1, 2, 3, 4], (x) => x % 2 == 0);
let sum = fold([1, 2, 3, 4], 0, (acc, x) => acc + x);
```

### Error Handling

```typescript
try {
    // code that might throw an error
} catch (error) {
    // handle error
}

throw "Custom error message";
```

### Clarity-specific Features

```typescript
// Traits
trait Token {
    transfer(from: principal, to: principal, amount: uint): Response<bool, uint>;
    getBalance(account: principal): Response<uint, uint>;
}

// Maps
@map({ key: principal, value: uint })
const balances = new Map<principal, uint>();

// Assets
@asset
class NFT {
    id: uint;
    owner: principal;
}

// Contract calls
let result = TokenContract.transfer(sender, recipient, amount);
```

### Advanced Features

- List comprehensions
- Type assertions and checks
- Async operations (where supported by Clarity)
- Import and export declarations for modular contract development

## Examples

Here's a simple token contract written in StxScript:

```typescript
@map({ key: principal, value: uint })
const balances = new Map<principal, uint>();

@public
function transfer(to: principal, amount: uint): Response<bool, uint> {
    let sender = tx.sender;
    let senderBalance = balances.get(sender) ?? 0;
    
    if (senderBalance < amount) {
        return err(1); // Insufficient balance
    }
    
    let recipientBalance = balances.get(to) ?? 0;
    balances.set(sender, senderBalance - amount);
    balances.set(to, recipientBalance + amount);
    
    return ok(true);
}

@readable
function getBalance(account: principal): Response<uint, uint> {
    return ok(balances.get(account) ?? 0);
}
```

## Development

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/cryptuon/stxscript.git
   cd stxscript
   ```

2. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install the project dependencies:
   ```bash
   poetry install
   ```

4. Activate the virtual environment:
   ```bash
   poetry shell
   ```

### Running Tests

To run the test suite:

```bash
poetry run python -m unittest stxscript.test_transpiler
```

To run linting and type checking:

```bash
poetry run flake8 stxscript
poetry run mypy stxscript
```

## Contributing

We welcome contributions to StxScript! Please see our [Contributing Guide](CONTRIBUTING.md) for more details on how to get started.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.