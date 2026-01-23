# Formatter & Linter

StxScript includes built-in tools for code formatting and static analysis.

## Formatter

The formatter (`stxscript fmt`) normalizes code style for consistency.

### Usage

```bash
# Format files in place
stxscript fmt src/

# Format a single file
stxscript fmt contract.stx

# Check if files are formatted (CI-friendly)
stxscript fmt --check src/

# Show diff of changes without applying
stxscript fmt --diff src/
```

### What It Formats

The formatter handles:

- **Indentation** - Consistent 4-space indentation for nested blocks
- **Spacing** - Spaces around operators, after colons, between parameters
- **Line breaks** - Blank lines between declarations
- **Trailing whitespace** - Removed from all lines
- **Final newline** - Ensures files end with a newline
- **Brace style** - Opening brace on same line as declaration

### Examples

#### Variable Declarations

Before:
```typescript
let   balance:uint=1000u;
const MAX:uint =    100u;
```

After:
```typescript
let balance: uint = 1000u;
const MAX: uint = 100u;
```

#### Functions

Before:
```typescript
@public
function transfer(to:principal,amount:uint):Response<bool,uint>{
if(amount==0u){return err(1u);}
return ok(true);
}
```

After:
```typescript
@public
function transfer(to: principal, amount: uint): Response<bool, uint> {
    if (amount == 0u) {
        return err(1u);
    }
    return ok(true);
}
```

#### Maps and Types

Before:
```typescript
map balances<principal,uint>;
type Amount=uint;
```

After:
```typescript
map balances<principal, uint>;
type Amount = uint;
```

### CI Integration

Use `--check` mode in CI pipelines. It exits with code 1 if any files need formatting:

```bash
stxscript fmt --check src/ || (echo "Run 'stxscript fmt src/' to fix" && exit 1)
```

## Linter

The linter (`stxscript lint`) performs static analysis to catch potential issues.

### Usage

```bash
# Lint files
stxscript lint src/

# Lint with auto-fix
stxscript lint --fix src/

# JSON output (for tool integration)
stxscript lint --format json src/
```

### Rule Categories

#### Naming Conventions

Checks that identifiers follow expected patterns:

| Identifier Type | Expected Pattern | Example |
|----------------|-----------------|---------|
| Variables | camelCase or snake_case | `totalSupply`, `total_supply` |
| Constants | UPPER_SNAKE_CASE | `MAX_SUPPLY`, `ERR_NOT_FOUND` |
| Functions | camelCase or snake_case | `getBalance`, `get_balance` |
| Types | PascalCase | `Amount`, `TokenResult` |

```
src/main.stx:5:7 [warning] naming: Variable 'BadName' should be camelCase or snake_case
```

#### Unused Variables

Detects variables that are declared but never referenced:

```typescript
function example(): uint {
    let unused: uint = 42u;  // Warning: 'unused' is never read
    return 0u;
}
```

#### Code Complexity

Warns when functions become too complex (deep nesting, many branches):

```
src/main.stx:20:1 [warning] complexity: Function 'process' has complexity 12 (threshold: 10)
```

#### Security Checks

Identifies potential security issues:

- **Missing authorization**: Public functions that don't check `tx-sender`
- **Unchecked external calls**: Contract calls without error handling
- **Integer overflow potential**: Arithmetic without bounds checking

```
src/main.stx:15:1 [error] security: Public function 'withdraw' has no authorization check
```

#### Unreachable Code

Code after unconditional return statements:

```typescript
function example(): uint {
    return 42u;
    let x: uint = 0u;  // Warning: unreachable code
}
```

#### Variable Shadowing

Inner scope variables that shadow outer scope:

```typescript
let count: uint = 0u;

function example(): uint {
    let count: uint = 10u;  // Warning: 'count' shadows outer variable
    return count;
}
```

### Output Formats

#### Text (default)

```
src/main.stx:5:7 [warning] naming: Variable 'badName' should use consistent casing
src/main.stx:12:1 [error] security: Missing authorization in public function
```

#### JSON

```bash
stxscript lint --format json src/
```

```json
[
  {
    "file": "src/main.stx",
    "line": 5,
    "column": 7,
    "severity": "warning",
    "rule": "naming",
    "message": "Variable 'badName' should use consistent casing"
  }
]
```

### Severity Levels

| Level | Description | CI Impact |
|-------|-------------|-----------|
| Error | Must be fixed | Causes non-zero exit |
| Warning | Should be fixed | Does not cause non-zero exit |
| Info | Suggestion | Informational only |

### Auto-Fix

Some rules support automatic fixing:

```bash
stxscript lint --fix src/
```

Fixable issues:
- Naming convention violations (renames identifiers)
- Unused variable removal
- Simple formatting issues

Non-fixable issues (require manual review):
- Security warnings
- Complexity issues
- Logic-dependent problems

## Combining Formatter and Linter

A typical development workflow:

```bash
# Format first
stxscript fmt src/

# Then lint
stxscript lint src/

# Fix auto-fixable issues
stxscript lint --fix src/
```

In CI:

```bash
stxscript fmt --check src/ && stxscript lint src/
```

## Next Steps

- [Configuration](../reference/configuration.md) - Config file options
- [CLI Reference](../reference/cli.md) - All command flags
- [Deployment](../guide/deployment.md) - CI/CD integration
