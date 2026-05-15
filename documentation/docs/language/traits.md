# Traits

Traits define interfaces that contracts must implement. They are used for contract interoperability and SIP (Stacks Improvement Proposal) compliance.

## Trait Definitions

A trait declares a set of function signatures without implementations:

```typescript
trait Token {
    transfer(from: principal, to: principal, amount: uint): Response<bool, uint>;
    get_balance(account: principal): uint;
    get_total_supply(): uint;
}
```

**Generated Clarity:**
```lisp
(define-trait Token
  ((transfer (principal principal uint) (response bool uint))
   (get-balance (principal) uint)
   (get-total-supply () uint)))
```

### Trait Function Signatures

Each entry in a trait specifies:
- Function name
- Parameter types
- Return type

Traits cannot include variable or map declarations -- they define behavior only.

## Implementing Traits

Use the `@contract` decorator and `implements` keyword on a `class` to declare that a contract satisfies a trait:

```typescript
@contract
class MyToken implements Token {
    @public
    function transfer(from: principal, to: principal, amount: uint): Response<bool, uint> {
        return ok(true);
    }

    @readonly
    function get_balance(account: principal): uint {
        return 0u;
    }

    @readonly
    function get_total_supply(): uint {
        return total_supply;
    }
}
```

**Generated Clarity:**
```lisp
(impl-trait .Token)

(define-public (transfer (from principal) (to principal) (amount uint))
  (ok true))

(define-read-only (get-balance (account principal))
  u0)

(define-read-only (get-total-supply)
  (var-get total-supply))
```

## Trait Compliance Checking

The semantic analyzer verifies that implementations satisfy their traits:

### Missing Methods

```typescript
trait Countable {
    increment(): Response<uint, uint>;
    get_count(): uint;
}

@contract
class Counter implements Countable {
    @public
    function increment(): Response<uint, uint> {
        return ok(1u);
    }
    // Error: Missing trait method 'get_count'
}
```

### Signature Mismatch

The analyzer checks that parameter types and return types match exactly:

```typescript
trait Token {
    transfer(to: principal, amount: uint): Response<bool, uint>;
}

@contract
class BadToken implements Token {
    @public
    function transfer(to: principal, amount: int): Response<bool, uint> {
        // Error: Parameter type mismatch - expected uint, got int
        return ok(true);
    }
}
```

## SIP Compliance

Stacks Improvement Proposals define standard traits for common contract patterns:

### SIP-009 (NFT Standard)

```typescript
trait SIP009 {
    get_last_token_id(): Response<uint, uint>;
    get_token_uri(id: uint): Response<Optional<string>, uint>;
    get_owner(id: uint): Response<Optional<principal>, uint>;
    transfer(id: uint, sender: principal, recipient: principal): Response<bool, uint>;
}
```

### SIP-010 (Fungible Token Standard)

```typescript
trait SIP010 {
    transfer(amount: uint, sender: principal, recipient: principal, memo: Optional<buffer<34>>): Response<bool, uint>;
    get_name(): Response<string, uint>;
    get_symbol(): Response<string, uint>;
    get_decimals(): Response<uint, uint>;
    get_balance(account: principal): Response<uint, uint>;
    get_total_supply(): Response<uint, uint>;
    get_token_uri(): Response<Optional<string>, uint>;
}
```

### Implementing SIP-010

```typescript
@contract
class MyToken implements SIP010 {
    const TOKEN_NAME: string = "My Token";
    const TOKEN_SYMBOL: string = "MTK";
    const DECIMALS: uint = 6u;

    map balances<principal, uint>;
    let total_supply: uint = 0u;

    @public
    function transfer(amount: uint, sender: principal, recipient: principal, memo: Optional<buffer<34>>): Response<bool, uint> {
        if (sender != tx-sender) {
            return err(ERR_UNAUTHORIZED);
        }
        // ... transfer logic
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
        return ok(DECIMALS);
    }

    @readonly
    function get_balance(account: principal): Response<uint, uint> {
        return ok(balances.get(account) ?? 0u);
    }

    @readonly
    function get_total_supply(): Response<uint, uint> {
        return ok(total_supply);
    }

    @readonly
    function get_token_uri(): Response<Optional<string>, uint> {
        return ok(none);
    }
}
```

## Multiple Traits

The grammar permits a single trait after `implements`. To combine behaviors, define a parent trait that includes both contracts' methods, or split the contract into multiple class declarations each implementing one trait.

## Trait as Parameter Types

Traits can be used as parameter types for inter-contract calls:

```typescript
@public
function swap(token_a: <SIP010>, token_b: <SIP010>, amount: uint): Response<bool, uint> {
    // Call methods on any contract implementing SIP010
    return ok(true);
}
```

## Next Steps

- [Modules & Imports](modules.md) - Cross-contract calls
- [Functions](functions.md) - Function decorators
- [Error Handling](error-handling.md) - Response types in trait methods
