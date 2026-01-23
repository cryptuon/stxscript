# Configuration

Configuration files and options for StxScript projects.

## Package Manifest (stxscript.toml)

Every StxScript project has a `stxscript.toml` manifest file:

```toml
[package]
name = "my-project"
version = "0.1.0"
description = "A StxScript smart contract"
authors = ["Your Name <your@email.com>"]
license = "MIT"

[dependencies]
token-utils = "^1.0.0"

[dev-dependencies]
test-helpers = "^0.2.0"
```

### Package Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Package identifier (lowercase, hyphens allowed) |
| `version` | string | Yes | Semantic version (e.g., "1.2.3") |
| `description` | string | No | Short description |
| `authors` | list | No | Author strings ("Name <email>") |
| `license` | string | No | License identifier (e.g., "MIT") |

### Dependencies Section

Dependencies use semantic versioning constraints:

| Constraint | Meaning | Example Matches |
|------------|---------|-----------------|
| `"^1.2.0"` | Compatible with 1.2.0 | 1.2.0, 1.3.0, 1.9.9 |
| `"~1.2.0"` | Patch-level changes | 1.2.0, 1.2.1, 1.2.9 |
| `"1.2.0"` | Exact version | 1.2.0 only |
| `">=1.0.0"` | Minimum version | 1.0.0 and above |

### Dev Dependencies

Dependencies only needed during development (testing, linting):

```toml
[dev-dependencies]
test-helpers = "^0.2.0"
mock-contracts = "^1.0.0"
```

## Formatter Configuration

The formatter can be configured via CLI flags or a config file.

### CLI Options

```bash
stxscript fmt src/              # Format in place
stxscript fmt --check src/      # Check only (exit 1 if unformatted)
stxscript fmt --diff src/       # Show formatting diff
stxscript fmt --config .stxfmt  # Use custom config
```

### Formatter Behavior

The formatter normalizes:

- **Indentation**: Consistent 4-space indentation
- **Spacing**: Consistent spacing around operators and after keywords
- **Line length**: Wraps long lines
- **Trailing whitespace**: Removed
- **Final newline**: Ensured at end of file
- **Blank lines**: Normalized between declarations

### Before/After Example

Before:
```typescript
const TOKEN_NAME:string="MyToken";
let   balance :  uint=0u;
@public
function transfer( to:principal,amount:uint):Response<bool,uint>{
return ok(true);
}
```

After:
```typescript
const TOKEN_NAME: string = "MyToken";
let balance: uint = 0u;

@public
function transfer(to: principal, amount: uint): Response<bool, uint> {
    return ok(true);
}
```

## Linter Configuration

The linter runs static analysis with configurable rules.

### CLI Options

```bash
stxscript lint src/              # Run linter
stxscript lint --fix src/        # Auto-fix issues
stxscript lint --format json src/ # JSON output
```

### Lint Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `naming-convention` | Warning | camelCase/snake_case for variables, UPPER_CASE for constants |
| `unused-variable` | Warning | Variables declared but never read |
| `complexity` | Warning | Function complexity exceeds threshold |
| `security-check` | Error | Potential security issues |
| `missing-return-type` | Warning | Functions without explicit return types |
| `unreachable-code` | Warning | Code after return statements |
| `shadowing` | Warning | Variable shadows outer scope |

### Security Rules

The linter checks for:

- Unchecked `tx-sender` usage in authorization
- Missing authorization guards in public functions
- Potential integer overflow patterns
- Unbounded operations

### Example Output

```
src/main.stx:5:1 [warning] naming: Variable 'BadName' should be camelCase or snake_case
src/main.stx:12:5 [warning] unused: Variable 'temp' is never used
src/main.stx:20:1 [error] security: Public function 'admin_reset' has no authorization check
```

## Watch Mode Configuration

```bash
stxscript watch src/ --output build/ --ignore "*.test.stx" --ignore "temp/"
```

### Options

| Flag | Description |
|------|-------------|
| `--output DIR` | Output directory for transpiled files |
| `--ignore PATTERN` | File patterns to ignore (repeatable) |
| `-v, --verbose` | Show detailed rebuild output |

## Global CLI Options

These work with all commands:

| Flag | Description |
|------|-------------|
| `--version` | Show StxScript version |
| `--verbose, -v` | Enable verbose output |
| `--help, -h` | Show help message |

## Environment

StxScript requires:

- Python 3.10+
- No additional system dependencies for core functionality
- Node.js (only for VS Code extension development)

## Next Steps

- [CLI Reference](cli.md) - Complete command reference
- [Formatter & Linter](../tooling/formatter-linter.md) - Detailed tool usage
- [Package Manager](../tooling/package-manager.md) - Dependency management
