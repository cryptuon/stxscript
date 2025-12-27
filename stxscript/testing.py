"""
StxScript Testing Framework

Provides utilities for testing StxScript contracts:
- Contract test runner
- Mock system for contract calls
- Assertions for Clarity types
- Coverage tracking
"""

import os
import sys
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable, Union
from pathlib import Path

from .transpiler import StxScriptTranspiler, SemanticError


# =============================================================================
# DATA TYPES
# =============================================================================

@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    duration_ms: float
    error: Optional[str] = None
    output: Optional[str] = None


@dataclass
class TestSuiteResult:
    """Result of a test suite."""
    name: str
    tests: List[TestResult] = field(default_factory=list)
    setup_error: Optional[str] = None

    @property
    def passed(self) -> int:
        return sum(1 for t in self.tests if t.passed)

    @property
    def failed(self) -> int:
        return sum(1 for t in self.tests if not t.passed)

    @property
    def total(self) -> int:
        return len(self.tests)

    @property
    def duration_ms(self) -> float:
        return sum(t.duration_ms for t in self.tests)


@dataclass
class ClarityValue:
    """Represents a Clarity value for testing."""
    type: str  # "int", "uint", "bool", "string", "principal", "optional", "response", "list", "tuple"
    value: Any

    @staticmethod
    def int(val: int) -> 'ClarityValue':
        return ClarityValue(type="int", value=val)

    @staticmethod
    def uint(val: int) -> 'ClarityValue':
        return ClarityValue(type="uint", value=val)

    @staticmethod
    def bool(val: bool) -> 'ClarityValue':
        return ClarityValue(type="bool", value=val)

    @staticmethod
    def string(val: str) -> 'ClarityValue':
        return ClarityValue(type="string", value=val)

    @staticmethod
    def principal(val: str) -> 'ClarityValue':
        return ClarityValue(type="principal", value=val)

    @staticmethod
    def some(val: 'ClarityValue') -> 'ClarityValue':
        return ClarityValue(type="optional", value=("some", val))

    @staticmethod
    def none() -> 'ClarityValue':
        return ClarityValue(type="optional", value=("none", None))

    @staticmethod
    def ok(val: 'ClarityValue') -> 'ClarityValue':
        return ClarityValue(type="response", value=("ok", val))

    @staticmethod
    def err(val: 'ClarityValue') -> 'ClarityValue':
        return ClarityValue(type="response", value=("err", val))

    @staticmethod
    def list(vals: List['ClarityValue']) -> 'ClarityValue':
        return ClarityValue(type="list", value=vals)

    @staticmethod
    def tuple(fields: Dict[str, 'ClarityValue']) -> 'ClarityValue':
        return ClarityValue(type="tuple", value=fields)

    def __eq__(self, other):
        if not isinstance(other, ClarityValue):
            return False
        return self.type == other.type and self.value == other.value


# =============================================================================
# MOCK SYSTEM
# =============================================================================

class MockContractCall:
    """Mock for contract calls."""

    def __init__(self):
        self.calls: List[Dict[str, Any]] = []
        self.responses: Dict[str, ClarityValue] = {}

    def when(self, contract: str, method: str) -> 'MockContractCall':
        """Set up a mock for a contract call."""
        self._current_mock = f"{contract}.{method}"
        return self

    def returns(self, value: ClarityValue) -> 'MockContractCall':
        """Set the return value for the mock."""
        if hasattr(self, '_current_mock'):
            self.responses[self._current_mock] = value
        return self

    def get_response(self, contract: str, method: str) -> Optional[ClarityValue]:
        """Get the mocked response for a contract call."""
        key = f"{contract}.{method}"
        return self.responses.get(key)

    def record_call(self, contract: str, method: str, args: List[Any]):
        """Record a contract call for verification."""
        self.calls.append({
            "contract": contract,
            "method": method,
            "args": args
        })

    def verify_called(self, contract: str, method: str, times: int = None) -> bool:
        """Verify a contract method was called."""
        matching = [c for c in self.calls
                   if c["contract"] == contract and c["method"] == method]
        if times is not None:
            return len(matching) == times
        return len(matching) > 0

    def reset(self):
        """Reset all mocks and call records."""
        self.calls = []
        self.responses = {}


class MockBlockchain:
    """Mock blockchain state for testing."""

    def __init__(self):
        self.block_height: int = 1
        self.stx_balances: Dict[str, int] = {}
        self.data_vars: Dict[str, ClarityValue] = {}
        self.maps: Dict[str, Dict[str, ClarityValue]] = {}
        self.tx_sender: str = "'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM"
        self.contract_caller: str = "'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM"

    def set_block_height(self, height: int):
        """Set the current block height."""
        self.block_height = height

    def set_tx_sender(self, sender: str):
        """Set the transaction sender."""
        self.tx_sender = sender

    def set_stx_balance(self, principal: str, amount: int):
        """Set STX balance for a principal."""
        self.stx_balances[principal] = amount

    def get_stx_balance(self, principal: str) -> int:
        """Get STX balance for a principal."""
        return self.stx_balances.get(principal, 0)

    def set_var(self, name: str, value: ClarityValue):
        """Set a data variable."""
        self.data_vars[name] = value

    def get_var(self, name: str) -> Optional[ClarityValue]:
        """Get a data variable."""
        return self.data_vars.get(name)

    def set_map_entry(self, map_name: str, key: str, value: ClarityValue):
        """Set a map entry."""
        if map_name not in self.maps:
            self.maps[map_name] = {}
        self.maps[map_name][key] = value

    def get_map_entry(self, map_name: str, key: str) -> Optional[ClarityValue]:
        """Get a map entry."""
        if map_name not in self.maps:
            return None
        return self.maps[map_name].get(key)

    def mine_block(self, count: int = 1):
        """Advance the block height."""
        self.block_height += count

    def reset(self):
        """Reset the blockchain state."""
        self.block_height = 1
        self.stx_balances = {}
        self.data_vars = {}
        self.maps = {}


# =============================================================================
# ASSERTIONS
# =============================================================================

class Assertions:
    """Assertion helpers for StxScript testing."""

    @staticmethod
    def is_ok(result: ClarityValue, message: str = None) -> bool:
        """Assert that a response is ok."""
        if result.type != "response":
            raise AssertionError(message or f"Expected response, got {result.type}")
        if result.value[0] != "ok":
            raise AssertionError(message or f"Expected ok, got err: {result.value[1]}")
        return True

    @staticmethod
    def is_err(result: ClarityValue, message: str = None) -> bool:
        """Assert that a response is err."""
        if result.type != "response":
            raise AssertionError(message or f"Expected response, got {result.type}")
        if result.value[0] != "err":
            raise AssertionError(message or f"Expected err, got ok: {result.value[1]}")
        return True

    @staticmethod
    def is_some(result: ClarityValue, message: str = None) -> bool:
        """Assert that an optional is some."""
        if result.type != "optional":
            raise AssertionError(message or f"Expected optional, got {result.type}")
        if result.value[0] != "some":
            raise AssertionError(message or "Expected some, got none")
        return True

    @staticmethod
    def is_none(result: ClarityValue, message: str = None) -> bool:
        """Assert that an optional is none."""
        if result.type != "optional":
            raise AssertionError(message or f"Expected optional, got {result.type}")
        if result.value[0] != "none":
            raise AssertionError(message or f"Expected none, got some: {result.value[1]}")
        return True

    @staticmethod
    def equals(actual: ClarityValue, expected: ClarityValue, message: str = None) -> bool:
        """Assert that two values are equal."""
        if actual != expected:
            raise AssertionError(
                message or f"Expected {expected.value}, got {actual.value}"
            )
        return True

    @staticmethod
    def ok_equals(result: ClarityValue, expected: ClarityValue, message: str = None) -> bool:
        """Assert that a response is ok with a specific value."""
        Assertions.is_ok(result)
        return Assertions.equals(result.value[1], expected, message)

    @staticmethod
    def err_equals(result: ClarityValue, expected: ClarityValue, message: str = None) -> bool:
        """Assert that a response is err with a specific value."""
        Assertions.is_err(result)
        return Assertions.equals(result.value[1], expected, message)


# =============================================================================
# TEST RUNNER
# =============================================================================

class ContractTestCase:
    """Base class for contract test cases."""

    def __init__(self):
        self.mock_calls = MockContractCall()
        self.blockchain = MockBlockchain()
        self.transpiler = StxScriptTranspiler()
        self._contract_source: Optional[str] = None
        self._compiled_clarity: Optional[str] = None

    def load_contract(self, source: str):
        """Load and compile a contract for testing."""
        self._contract_source = source
        self._compiled_clarity = self.transpiler.transpile(source)

    def load_contract_file(self, path: str):
        """Load a contract from a file."""
        with open(path, 'r') as f:
            self.load_contract(f.read())

    def setUp(self):
        """Called before each test. Override to set up test fixtures."""
        pass

    def tearDown(self):
        """Called after each test. Override to clean up."""
        self.mock_calls.reset()
        self.blockchain.reset()

    def get_compiled(self) -> Optional[str]:
        """Get the compiled Clarity code."""
        return self._compiled_clarity


class TestRunner:
    """Runs StxScript contract tests."""

    def __init__(self):
        self.suites: List[TestSuiteResult] = []

    def run_suite(self, test_class: type) -> TestSuiteResult:
        """Run all tests in a test class."""
        suite_name = test_class.__name__
        result = TestSuiteResult(name=suite_name)

        # Get all test methods
        test_methods = [m for m in dir(test_class) if m.startswith('test_')]

        for method_name in test_methods:
            # Create fresh instance for each test
            instance = test_class()

            try:
                # Run setUp
                instance.setUp()

                # Run test
                start_time = time.time()
                method = getattr(instance, method_name)
                method()
                duration = (time.time() - start_time) * 1000

                result.tests.append(TestResult(
                    name=method_name,
                    passed=True,
                    duration_ms=duration
                ))

            except AssertionError as e:
                duration = (time.time() - start_time) * 1000
                result.tests.append(TestResult(
                    name=method_name,
                    passed=False,
                    duration_ms=duration,
                    error=str(e)
                ))

            except Exception as e:
                duration = (time.time() - start_time) * 1000
                result.tests.append(TestResult(
                    name=method_name,
                    passed=False,
                    duration_ms=duration,
                    error=f"{type(e).__name__}: {str(e)}"
                ))

            finally:
                try:
                    instance.tearDown()
                except Exception:
                    pass

        self.suites.append(result)
        return result

    def run_all(self, test_classes: List[type]) -> List[TestSuiteResult]:
        """Run all test suites."""
        for test_class in test_classes:
            self.run_suite(test_class)
        return self.suites

    def print_results(self):
        """Print test results to stdout."""
        total_passed = 0
        total_failed = 0
        total_time = 0.0

        print("\n" + "=" * 60)
        print("StxScript Test Results")
        print("=" * 60)

        for suite in self.suites:
            print(f"\n{suite.name}")
            print("-" * 40)

            for test in suite.tests:
                status = "[PASS]" if test.passed else "[FAIL]"
                print(f"  {status} {test.name} ({test.duration_ms:.1f}ms)")
                if test.error:
                    print(f"         Error: {test.error}")

            total_passed += suite.passed
            total_failed += suite.failed
            total_time += suite.duration_ms

        print("\n" + "=" * 60)
        print(f"Total: {total_passed} passed, {total_failed} failed")
        print(f"Time: {total_time:.1f}ms")
        print("=" * 60 + "\n")

        return total_failed == 0

    def to_json(self) -> str:
        """Export results as JSON."""
        data = {
            "suites": [
                {
                    "name": suite.name,
                    "passed": suite.passed,
                    "failed": suite.failed,
                    "total": suite.total,
                    "duration_ms": suite.duration_ms,
                    "tests": [
                        {
                            "name": t.name,
                            "passed": t.passed,
                            "duration_ms": t.duration_ms,
                            "error": t.error
                        }
                        for t in suite.tests
                    ]
                }
                for suite in self.suites
            ]
        }
        return json.dumps(data, indent=2)


# =============================================================================
# COVERAGE TRACKING
# =============================================================================

class CoverageTracker:
    """Tracks code coverage for StxScript contracts."""

    def __init__(self):
        self.covered_lines: Dict[str, set] = {}
        self.total_lines: Dict[str, int] = {}

    def register_file(self, file_path: str, total_lines: int):
        """Register a file for coverage tracking."""
        self.covered_lines[file_path] = set()
        self.total_lines[file_path] = total_lines

    def mark_covered(self, file_path: str, line: int):
        """Mark a line as covered."""
        if file_path in self.covered_lines:
            self.covered_lines[file_path].add(line)

    def get_coverage(self, file_path: str) -> float:
        """Get coverage percentage for a file."""
        if file_path not in self.total_lines:
            return 0.0
        total = self.total_lines[file_path]
        covered = len(self.covered_lines.get(file_path, set()))
        if total == 0:
            return 100.0
        return (covered / total) * 100

    def get_total_coverage(self) -> float:
        """Get total coverage across all files."""
        total = sum(self.total_lines.values())
        covered = sum(len(lines) for lines in self.covered_lines.values())
        if total == 0:
            return 100.0
        return (covered / total) * 100

    def print_report(self):
        """Print coverage report."""
        print("\n" + "=" * 60)
        print("Coverage Report")
        print("=" * 60)

        for file_path in self.total_lines:
            coverage = self.get_coverage(file_path)
            covered = len(self.covered_lines.get(file_path, set()))
            total = self.total_lines[file_path]
            print(f"  {file_path}: {coverage:.1f}% ({covered}/{total} lines)")

        print("-" * 60)
        print(f"Total Coverage: {self.get_total_coverage():.1f}%")
        print("=" * 60 + "\n")


# =============================================================================
# CLI INTEGRATION
# =============================================================================

def run_tests(test_dir: str, pattern: str = "test_*.py") -> bool:
    """
    Run all tests in a directory.

    Args:
        test_dir: Directory containing test files
        pattern: File pattern for test files

    Returns:
        True if all tests passed
    """
    import importlib.util
    import glob

    test_files = glob.glob(os.path.join(test_dir, pattern))
    runner = TestRunner()
    test_classes = []

    for file_path in test_files:
        # Load the module
        spec = importlib.util.spec_from_file_location("test_module", file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find test classes
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and
                    issubclass(obj, ContractTestCase) and
                    obj != ContractTestCase):
                    test_classes.append(obj)

    runner.run_all(test_classes)
    return runner.print_results()


# Convenience exports
assert_ok = Assertions.is_ok
assert_err = Assertions.is_err
assert_some = Assertions.is_some
assert_none = Assertions.is_none
assert_equals = Assertions.equals
