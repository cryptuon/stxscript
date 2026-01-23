# Testing StxScript Contracts

StxScript includes a testing framework for writing and running contract tests.

## Quick Start

### Create a Test

Create `tests/test_contract.py`:

```python
from stxscript.testing import ContractTestCase, ClarityValue, Assertions

class TestMyContract(ContractTestCase):
    def setUp(self):
        self.load_contract_file('src/main.stx')

    def test_mint_success(self):
        result = ClarityValue.ok(ClarityValue.bool(True))
        Assertions.is_ok(result)

    def test_get_balance(self):
        expected = ClarityValue.uint(1000)
        actual = ClarityValue.uint(1000)
        Assertions.equals(actual, expected)
```

### Run Tests

```bash
stxscript test
```

## Test Framework

### ContractTestCase

Base class for all contract tests.

```python
from stxscript.testing import ContractTestCase

class TestMyContract(ContractTestCase):
    def setUp(self):
        # Load contract source
        self.load_contract_file('contract.stx')
        # Or load from string
        self.load_contract('const X: uint = 1u;')

    def tearDown(self):
        # Cleanup (automatic)
        pass

    def test_something(self):
        # Your test
        pass
```

### ClarityValue

Create Clarity values for testing.

```python
from stxscript.testing import ClarityValue

# Primitives
integer = ClarityValue.int(-42)
unsigned = ClarityValue.uint(100)
boolean = ClarityValue.bool(True)
string = ClarityValue.string("Hello")
principal = ClarityValue.principal("'SP2J...")

# Optionals
some_value = ClarityValue.some(ClarityValue.uint(42))
none_value = ClarityValue.none()

# Responses
ok_result = ClarityValue.ok(ClarityValue.bool(True))
err_result = ClarityValue.err(ClarityValue.uint(1))

# Collections
list_value = ClarityValue.list([
    ClarityValue.uint(1),
    ClarityValue.uint(2)
])

tuple_value = ClarityValue.tuple({
    "name": ClarityValue.string("Alice"),
    "balance": ClarityValue.uint(100)
})
```

### Assertions

Assert conditions on Clarity values.

```python
from stxscript.testing import Assertions

# Response assertions
Assertions.is_ok(result)
Assertions.is_err(result)
Assertions.ok_equals(result, expected_value)
Assertions.err_equals(result, expected_value)

# Optional assertions
Assertions.is_some(optional)
Assertions.is_none(optional)

# Equality
Assertions.equals(actual, expected)
```

## Mock Blockchain

Simulate blockchain state.

```python
from stxscript.testing import ContractTestCase, ClarityValue

class TestWithBlockchain(ContractTestCase):
    def setUp(self):
        self.load_contract_file('contract.stx')

        # Set block height
        self.blockchain.set_block_height(100)

        # Set STX balances
        self.blockchain.set_stx_balance(
            "'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7",
            1000000
        )

        # Set transaction sender
        self.blockchain.set_tx_sender(
            "'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7"
        )

        # Set data variables
        self.blockchain.set_var(
            "total_supply",
            ClarityValue.uint(1000)
        )

        # Set map entries
        self.blockchain.set_map_entry(
            "balances",
            "'SP2J...",
            ClarityValue.uint(500)
        )

    def test_after_mining(self):
        # Mine blocks
        self.blockchain.mine_block(10)

        # Block height is now 110
        self.assertEqual(self.blockchain.block_height, 110)
```

## Mock Contract Calls

Mock responses from other contracts.

```python
from stxscript.testing import ContractTestCase, ClarityValue

class TestWithMocks(ContractTestCase):
    def setUp(self):
        self.load_contract_file('contract.stx')

        # Set up mock response
        self.mock_calls.when("Token", "transfer").returns(
            ClarityValue.ok(ClarityValue.bool(True))
        )

    def test_calls_token(self):
        # ... run test ...

        # Verify the call was made
        self.assertTrue(
            self.mock_calls.verify_called("Token", "transfer")
        )

        # Verify call count
        self.assertTrue(
            self.mock_calls.verify_called("Token", "transfer", times=1)
        )
```

## Test Runner

Run tests programmatically.

```python
from stxscript.testing import TestRunner

runner = TestRunner()

# Run a single test suite
result = runner.run_suite(TestMyContract)

# Run multiple suites
results = runner.run_all([TestMyContract, TestOtherContract])

# Print results
runner.print_results()

# Export as JSON
json_output = runner.to_json()
```

## Coverage Tracking

Track code coverage.

```python
from stxscript.testing import CoverageTracker

tracker = CoverageTracker()

# Register files
tracker.register_file('contract.stx', total_lines=100)

# Mark lines as covered
tracker.mark_covered('contract.stx', 10)
tracker.mark_covered('contract.stx', 15)

# Get coverage
percentage = tracker.get_coverage('contract.stx')
total = tracker.get_total_coverage()

# Print report
tracker.print_report()
```

## CLI Usage

```bash
# Run all tests in tests/
stxscript test

# Specify directory
stxscript test tests/

# With coverage
stxscript test --coverage

# JSON output
stxscript test --json

# Specific pattern
stxscript test --pattern "test_token_*.py"
```

## Example: Token Contract Tests

```python
from stxscript.testing import (
    ContractTestCase,
    ClarityValue,
    Assertions
)

class TestToken(ContractTestCase):
    def setUp(self):
        self.load_contract_file('src/token.stx')

        # Set up initial state
        self.blockchain.set_tx_sender(
            "'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7"
        )
        self.blockchain.set_map_entry(
            "balances",
            "'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7",
            ClarityValue.uint(1000)
        )

    def test_transfer_success(self):
        # Expected: transfer succeeds
        result = ClarityValue.ok(ClarityValue.bool(True))
        Assertions.is_ok(result)

    def test_transfer_insufficient_balance(self):
        # Expected: transfer fails with error code
        result = ClarityValue.err(ClarityValue.uint(101))
        Assertions.is_err(result)
        Assertions.err_equals(result, ClarityValue.uint(101))

    def test_get_balance(self):
        expected = ClarityValue.uint(1000)
        actual = ClarityValue.uint(1000)
        Assertions.equals(actual, expected)

    def test_mint_within_limit(self):
        result = ClarityValue.ok(ClarityValue.bool(True))
        Assertions.is_ok(result)

    def test_mint_exceeds_limit(self):
        result = ClarityValue.err(ClarityValue.uint(1))
        Assertions.is_err(result)
```

## Best Practices

1. **One test file per contract** - Keep tests organized
2. **Use setUp for common state** - Avoid repetition
3. **Test both success and failure** - Cover error paths
4. **Use descriptive names** - `test_transfer_insufficient_balance`
5. **Mock external contracts** - Isolate your tests
6. **Check edge cases** - Zero values, max values, boundaries
