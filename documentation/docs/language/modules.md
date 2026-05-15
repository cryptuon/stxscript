# Modules & Imports

StxScript supports a module system for organizing code across files and making inter-contract calls.

## Import Syntax

Import declarations bring symbols from other modules into scope:

```typescript
import { TokenTrait } from "./traits";
import { utils } from "../lib/utils";
import { SIP010 } from "@sips/sip-010";
```

### Import Forms

```typescript
// Named imports
import { Transfer, Mint } from "./events";

// Module import
import { math } from "./lib/math";
```

Imports are resolved relative to the current file or from packages.

## Contract Calls

Call functions on other deployed contracts using dot notation:

```typescript
let result = OtherContract.transfer(sender, recipient, amount);
let balance = TokenContract.get_balance(account);
```

**Generated Clarity:**
```lisp
(contract-call? .OtherContract transfer sender recipient amount)
(contract-call? .TokenContract get-balance account)
```

### Handling Contract Call Results

Contract calls return Response types that should be handled:

```typescript
@public
function swap(amount: uint): Response<bool, uint> {
    // Use try! to propagate errors
    let transferred = try!(TokenA.transfer(tx-sender, contract_address, amount));

    // Or match explicitly
    match TokenB.transfer(contract_address, tx-sender, amount) {
        ok(success) => ok(true),
        err(code) => err(code)
    }
}
```

### Fully Qualified Contract References

For contracts deployed at specific addresses:

```typescript
let result = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7.token-contract.transfer(
    tx-sender,
    recipient,
    amount
);
```

**Generated Clarity:**
```lisp
(contract-call? 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7.token-contract
  transfer tx-sender recipient amount)
```

## Module Organization

### Single Contract Per File

The recommended pattern is one contract per `.stx` file:

```
src/
├── token.stx          # Main token contract
├── governance.stx     # Governance contract
├── traits/
│   ├── sip-010.stx    # SIP-010 trait definition
│   └── ownable.stx    # Ownable trait
└── lib/
    └── math.stx       # Utility functions
```

### Trait Modules

Define traits in separate files for reuse:

```typescript
// traits/sip-010.stx
trait SIP010 {
    transfer(amount: uint, sender: principal, recipient: principal, memo: Optional<buffer<34>>): Response<bool, uint>;
    get_balance(account: principal): Response<uint, uint>;
    get_total_supply(): Response<uint, uint>;
}
```

```typescript
// token.stx
import { SIP010 } from "./traits/sip-010";

@contract
class MyToken implements SIP010 {
    // ...
}
```

## Inter-Contract Patterns

### Proxy Pattern

```typescript
@public
function proxy_transfer(token: principal, to: principal, amount: uint): Response<bool, uint> {
    let result = try!(TokenContract.transfer(amount, tx-sender, to, none));
    return ok(result);
}
```

### Callback Pattern

```typescript
@public
function execute_with_callback(action: uint): Response<bool, uint> {
    // Perform action
    let result = try!(perform_action(action));

    // Notify callback contract
    try!(CallbackContract.on_action_complete(action, result));

    return ok(true);
}
```

### Multi-Contract Composition

```typescript
@public
function complex_swap(
    amount_a: uint,
    amount_b: uint
): Response<bool, uint> {
    // Step 1: Transfer token A from user
    try!(TokenA.transfer(amount_a, tx-sender, contract_address, none));

    // Step 2: Transfer token B to user
    try!(TokenB.transfer(amount_b, contract_address, tx-sender, none));

    return ok(true);
}
```

## Next Steps

- [Traits](traits.md) - Defining contract interfaces
- [Functions](functions.md) - Public function signatures
- [Error Handling](error-handling.md) - Handling inter-contract errors
