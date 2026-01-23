# Package Manager

StxScript includes a built-in package manager for dependency management.

## Overview

The package manager (`stxscript pkg`) handles:

- Project initialization with manifest files
- Adding and removing dependencies
- Installing packages
- Semantic version resolution

## Commands

### Initialize a Project

Create a new `stxscript.toml` manifest:

```bash
stxscript pkg init
stxscript pkg init --name my-project
```

This creates:

```toml
[package]
name = "my-project"
version = "0.1.0"
description = ""
authors = []
license = "MIT"

[dependencies]

[dev-dependencies]
```

### Add Dependencies

Add a package to your project:

```bash
# Add a dependency
stxscript pkg add token-utils

# Add with version constraint
stxscript pkg add token-utils --version "^1.0.0"

# Add as dev dependency
stxscript pkg add test-helpers --dev
```

This updates `stxscript.toml`:

```toml
[dependencies]
token-utils = "^1.0.0"

[dev-dependencies]
test-helpers = "^0.1.0"
```

### Remove Dependencies

```bash
stxscript pkg remove token-utils
stxscript pkg remove test-helpers --dev
```

### Install Dependencies

Download and install all declared dependencies:

```bash
stxscript pkg install
```

### List Dependencies

Show installed packages and their status:

```bash
stxscript pkg list
```

Output:
```
Package          Version    Status
token-utils      1.2.0      installed
math-lib         0.5.3      installed
test-helpers     0.2.1      installed (dev)
```

## Version Constraints

The package manager uses semantic versioning (SemVer):

### Version Format

```
major.minor.patch[-prerelease]
```

Examples: `1.0.0`, `2.3.1`, `0.1.0-beta.1`

### Constraint Syntax

| Syntax | Meaning | Matches |
|--------|---------|---------|
| `"^1.2.0"` | Compatible (same major) | >= 1.2.0, < 2.0.0 |
| `"~1.2.0"` | Patch updates only | >= 1.2.0, < 1.3.0 |
| `"1.2.0"` | Exact version | 1.2.0 only |
| `">=1.0.0"` | Minimum version | >= 1.0.0 |
| `"*"` | Any version | Any |

### Caret (`^`) - Recommended

The caret constraint is the default and most common. It allows changes that don't modify the left-most non-zero digit:

- `^1.2.3` matches `1.2.3` to `1.x.x` (not `2.0.0`)
- `^0.2.3` matches `0.2.3` to `0.2.x` (not `0.3.0`)
- `^0.0.3` matches `0.0.3` only

### Tilde (`~`)

The tilde allows only patch-level changes:

- `~1.2.3` matches `1.2.3` to `1.2.x` (not `1.3.0`)

## Manifest File (stxscript.toml)

### Complete Example

```toml
[package]
name = "my-defi-protocol"
version = "1.0.0"
description = "A decentralized exchange protocol"
authors = [
    "Alice <alice@example.com>",
    "Bob <bob@example.com>"
]
license = "MIT"

[dependencies]
sip-010-trait = "^1.0.0"
sip-009-trait = "^1.0.0"
math-utils = "^0.5.0"

[dev-dependencies]
test-helpers = "^0.2.0"
mock-tokens = "^1.0.0"
```

### Field Reference

#### [package]

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique package identifier |
| `version` | string | Current package version |
| `description` | string | Package description |
| `authors` | list[string] | Author entries |
| `license` | string | License identifier |

#### [dependencies]

Runtime dependencies required for your contract to work.

#### [dev-dependencies]

Development-only dependencies (testing, tooling). Not included when the package is used as a dependency by others.

## Dependency Resolution

When you run `stxscript pkg install`, the package manager:

1. Reads `stxscript.toml`
2. Resolves version constraints for all dependencies
3. Downloads compatible versions
4. Installs to the project's package directory

### Conflict Resolution

If two dependencies require incompatible versions of a shared dependency, the package manager reports the conflict:

```
Error: Version conflict for 'math-utils':
  - my-project requires ^1.0.0
  - token-lib requires ^2.0.0
```

## Workflow

### Starting a New Project

```bash
stxscript new my-project --template token
cd my-project
stxscript pkg init
stxscript pkg add sip-010-trait --version "^1.0.0"
stxscript pkg install
```

### Adding to an Existing Project

```bash
cd existing-project
stxscript pkg add new-dependency --version "^0.5.0"
stxscript pkg install
```

### Updating Dependencies

Edit version constraints in `stxscript.toml`, then reinstall:

```bash
# Edit stxscript.toml to update version
stxscript pkg install
```

## Next Steps

- [Project Setup](../guide/project-setup.md) - Project structure
- [Configuration](../reference/configuration.md) - stxscript.toml reference
- [CLI Reference](../reference/cli.md) - All pkg subcommands
