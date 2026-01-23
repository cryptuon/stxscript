# Examples

Practical examples of StxScript code and the Clarity output they generate.

## Variables and Constants

### Token Configuration

**StxScript:**
```typescript
const TOKEN_NAME: string = "MyToken";
const TOKEN_SYMBOL: string = "MTK";
const MAX_SUPPLY: uint = 1000000u;

let total_supply: uint = 0u;
let contract_owner: principal = tx-sender;
```

**Generated Clarity:**
```lisp
(define-constant TOKEN_NAME u"MyToken")
(define-constant TOKEN_SYMBOL u"MTK")
(define-constant MAX_SUPPLY u1000000)
(define-data-var total_supply uint u0)
(define-data-var contract_owner principal tx-sender)
```

### Type Aliases

```typescript
type Amount = uint;
type Address = principal;
type Balance = { amount: Amount, locked: bool };

let transfer_amount: Amount = 1000u;
```

## Functions

### Public and Read-Only Functions

**StxScript:**
```typescript
@public
function transfer(to: principal, amount: uint): Response<bool, uint> {
    if (amount == 0u) {
        return err(1u);
    }
    return ok(true);
}

@readonly
function get_balance(account: principal): uint {
    return balances.get(account);
}

function validate_amount(amount: uint): bool {
    return amount > 0u && amount <= MAX_SUPPLY;
}
```

**Generated Clarity:**
```lisp
(define-public (transfer (to principal) (amount uint))
  (if (is-eq amount u0)
    (err u1)
    (ok true)))

(define-read-only (get-balance (account principal))
  (map-get? balances account))

(define-private (validate-amount (amount uint))
  (and (> amount u0) (<= amount MAX_SUPPLY)))
```

### Generic Functions

```typescript
function identity<T>(value: T): T {
    return value;
}

function first<T>(list: List<T>): Optional<T> {
    return list[0];
}
```

## Control Flow

### If/Else

```typescript
@public
function safe_transfer(amount: uint, to: principal): Response<bool, uint> {
    if (amount == 0u) {
        return err(1u);
    }

    let balance = get_balance(tx-sender);
    if (balance < amount) {
        return err(2u);
    }

    return ok(true);
}
```

### Match Expressions

```typescript
@public
function process_result(value: Optional<uint>): uint {
    match value {
        some(v) => v,
        none => 0u
    }
}

@public
function handle_response(result: Response<uint, string>): uint {
    match result {
        ok(v) => v,
        err(e) => 0u
    }
}
```

### For Loops

```typescript
@public
function sum_range(limit: uint): uint {
    let sum: uint = 0u;
    for (let i = 0; i < limit; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}
```

## Data Structures

### Maps

```typescript
map balances<principal, uint>;
map allowances<{ owner: principal, spender: principal }, uint>;

@public
function get_allowance(owner: principal, spender: principal): uint {
    let key = { owner: owner, spender: spender };
    match allowances.get(key) {
        some(amount) => amount,
        none => 0u
    }
}

@public
function set_allowance(spender: principal, amount: uint): Response<bool, uint> {
    let key = { owner: tx-sender, spender: spender };
    allowances.set(key, amount);
    return ok(true);
}
```

### Lists and Higher-Order Functions

```typescript
@public
function process_numbers(numbers: List<uint>): uint {
    let evens = filter(numbers, (x) => x % 2u == 0u);
    let doubled = map(evens, (x) => x * 2u);
    let total = fold(doubled, 0u, (acc, x) => acc + x);
    return total;
}
```

## Real-World Contracts

### SIP-010 Fungible Token

```typescript
const TOKEN_NAME: string = "Example Token";
const TOKEN_SYMBOL: string = "EXAM";
const TOKEN_DECIMALS: uint = 6u;
const TOTAL_SUPPLY: uint = 1000000000000u;

const ERR_UNAUTHORIZED: uint = 100u;
const ERR_INSUFFICIENT_BALANCE: uint = 101u;

let contract_owner: principal = tx-sender;
map balances<principal, uint>;

@public
function transfer(amount: uint, sender: principal, recipient: principal, memo: Optional<buffer<34>>): Response<bool, uint> {
    if (sender != tx-sender) {
        return err(ERR_UNAUTHORIZED);
    }

    let sender_balance = get_balance(sender);
    if (sender_balance < amount) {
        return err(ERR_INSUFFICIENT_BALANCE);
    }

    balances.set(sender, sender_balance - amount);
    balances.set(recipient, get_balance(recipient) + amount);

    return ok(true);
}

@readonly
function get_name(): Response<string, uint> {
    return ok(TOKEN_NAME);
}

@readonly
function get_symbol(): Response<string, uint> {
    return ok(TOKEN_SYMBOL);
}

@readonly
function get_decimals(): Response<uint, uint> {
    return ok(TOKEN_DECIMALS);
}

@readonly
function get_balance(account: principal): uint {
    match balances.get(account) {
        some(balance) => balance,
        none => 0u
    }
}

@readonly
function get_total_supply(): Response<uint, uint> {
    return ok(TOTAL_SUPPLY);
}
```

### Simple NFT Contract

```typescript
const CONTRACT_NAME: string = "My NFT Collection";

const ERR_NOT_OWNER: uint = 1u;
const ERR_NOT_FOUND: uint = 2u;

let last_token_id: uint = 0u;
map nft_owners<uint, principal>;
map nft_metadata<uint, string>;

@public
function mint(metadata_uri: string): Response<uint, uint> {
    let token_id = last_token_id + 1u;
    last_token_id = token_id;

    nft_owners.set(token_id, tx-sender);
    nft_metadata.set(token_id, metadata_uri);

    return ok(token_id);
}

@public
function transfer(token_id: uint, recipient: principal): Response<bool, uint> {
    match nft_owners.get(token_id) {
        some(owner) => {
            if (owner != tx-sender) {
                return err(ERR_NOT_OWNER);
            }
            nft_owners.set(token_id, recipient);
            return ok(true);
        },
        none => err(ERR_NOT_FOUND)
    }
}

@readonly
function get_owner(token_id: uint): Response<principal, uint> {
    match nft_owners.get(token_id) {
        some(owner) => ok(owner),
        none => err(ERR_NOT_FOUND)
    }
}
```

## Python API Usage

### Basic Transpilation

```python
from stxscript import StxScriptTranspiler

transpiler = StxScriptTranspiler()

result = transpiler.transpile('let balance: uint = 1000u;')
print(result)
# Output: (define-data-var balance uint u1000)
```

### Batch Transpilation

```python
from stxscript import StxScriptTranspiler
from pathlib import Path

def transpile_directory(src_dir: str, output_dir: str):
    transpiler = StxScriptTranspiler()
    src_path = Path(src_dir)
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    for stx_file in src_path.glob("*.stx"):
        with open(stx_file) as f:
            stx_code = f.read()

        try:
            clarity_code = transpiler.transpile(stx_code)
            output_file = out_path / f"{stx_file.stem}.clar"
            with open(output_file, "w") as f:
                f.write(clarity_code)
            print(f"Transpiled: {stx_file.name}")
        except Exception as e:
            print(f"Error in {stx_file.name}: {e}")

transpile_directory("src/contracts", "build/contracts")
```

## CLI Workflow

### Development Workflow

```bash
# Create a new token project
stxscript new my-token --template token
cd my-token

# Start development mode
stxscript watch src/ --output build/

# In another terminal, run tests
stxscript test

# Format and lint
stxscript fmt src/
stxscript lint src/

# Build for production
stxscript build src/ build/
```

### Package Management

```bash
# Initialize a new package
stxscript pkg init --name my-project

# Add dependencies
stxscript pkg add token-lib --version "^1.0.0"
stxscript pkg add utils --dev

# Install all dependencies
stxscript pkg install

# List installed packages
stxscript pkg list
```
