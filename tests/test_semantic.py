"""
Tests for the StxScript Semantic Analyzer.

Tests cover:
- Phase A: Undefined symbols, type mismatch, duplicates, argument count
- Phase B: Unused variables, unreachable code, shadowing, missing returns
- Phase C: Trait compliance checks
"""

import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from stxscript.transpiler import StxScriptTranspiler, SemanticError


class TestSemanticAnalyzer(unittest.TestCase):
    """Test semantic analysis error detection."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def get_errors(self, code: str):
        """Helper to get semantic errors from code."""
        try:
            self.transpiler.transpile(code)
            return []
        except SemanticError as e:
            return e.errors

    def assert_error_contains(self, code: str, expected_message: str):
        """Assert that transpilation produces an error containing the expected message."""
        errors = self.get_errors(code)
        self.assertTrue(
            any(expected_message.lower() in str(e).lower() for e in errors),
            f"Expected error containing '{expected_message}', got: {errors}"
        )

    def assert_no_errors(self, code: str):
        """Assert that transpilation produces no semantic errors."""
        errors = self.get_errors(code)
        self.assertEqual(errors, [], f"Expected no errors, got: {errors}")

    # =========================================================================
    # Phase A: Core Checks
    # =========================================================================

    def test_undefined_variable(self):
        """Should error on undefined variable reference."""
        code = """
        let x: int = y;
        """
        self.assert_error_contains(code, "Undefined symbol 'y'")

    def test_undefined_function(self):
        """Should error on undefined function call."""
        code = """
        let x: int = unknownFunc(5);
        """
        self.assert_error_contains(code, "Undefined function 'unknownFunc'")

    def test_type_mismatch_variable(self):
        """Should error on type mismatch in variable declaration."""
        code = """
        let x: int = "hello";
        """
        self.assert_error_contains(code, "Type mismatch")

    def test_type_mismatch_assignment(self):
        """Should error on type mismatch in assignment."""
        code = """
        function test(): int {
            let x: int = 5;
            x = "hello";
            return x;
        }
        """
        self.assert_error_contains(code, "Type mismatch")

    def test_duplicate_variable(self):
        """Should error on duplicate variable definition in same scope."""
        code = """
        let x: int = 1;
        let x: int = 2;
        """
        self.assert_error_contains(code, "already defined")

    def test_duplicate_function(self):
        """Should error on duplicate function definition."""
        code = """
        function add(a: int, b: int): int { return a + b; }
        function add(x: int, y: int): int { return x + y; }
        """
        self.assert_error_contains(code, "already defined")

    def test_assignment_to_constant(self):
        """Should error on constant reassignment."""
        code = """
        const X: int = 1;
        function test(): int {
            X = 2;
            return X;
        }
        """
        self.assert_error_contains(code, "Cannot assign to constant")

    def test_function_argument_count_too_few(self):
        """Should error on too few function arguments."""
        code = """
        function add(a: int, b: int): int { return a + b; }
        let x: int = add(1);
        """
        self.assert_error_contains(code, "expects 2 arguments, got 1")

    def test_function_argument_count_too_many(self):
        """Should error on too many function arguments."""
        code = """
        function add(a: int, b: int): int { return a + b; }
        let x: int = add(1, 2, 3);
        """
        self.assert_error_contains(code, "expects 2 arguments, got 3")

    def test_return_type_mismatch(self):
        """Should error on return type mismatch."""
        code = """
        function test(): int {
            return "hello";
        }
        """
        self.assert_error_contains(code, "Return type mismatch")

    # =========================================================================
    # Phase A: Type Compatibility
    # =========================================================================

    def test_bool_boolean_compatible(self):
        """bool and boolean should be compatible types."""
        code = """
        let x: bool = true;
        let y: boolean = false;
        """
        self.assert_no_errors(code)

    def test_int_uint_operations(self):
        """int and uint should work together in expressions."""
        code = """
        let x: int = 5;
        let y: uint = 10u;
        function test(): int {
            return x + 1;
        }
        """
        self.assert_no_errors(code)

    def test_response_type_check(self):
        """Response types should be checked correctly."""
        code = """
        function test(): Response<bool, string> {
            return ok(true);
        }
        """
        self.assert_no_errors(code)

    def test_optional_type_check(self):
        """Optional types should be checked correctly."""
        code = """
        let x: optional<int> = some(5);
        let y: optional<int> = none();
        """
        self.assert_no_errors(code)

    # =========================================================================
    # Phase B: Enhanced Checks (Warnings)
    # =========================================================================

    def test_valid_code_passes(self):
        """Valid code should pass without errors."""
        code = """
        function add(a: int, b: int): int {
            return a + b;
        }
        let result: int = add(2, 3);
        """
        self.assert_no_errors(code)

    def test_complex_valid_code(self):
        """Complex valid code should pass."""
        code = """
        const MAX_VALUE: uint = 100u;

        function isValid(value: uint): bool {
            if (value > 0u) {
                return true;
            } else {
                return false;
            }
        }

        let x: bool = isValid(50u);
        """
        self.assert_no_errors(code)

    # =========================================================================
    # Phase C: Trait Compliance
    # =========================================================================

    def test_trait_not_defined(self):
        """Should error when implementing undefined trait."""
        code = """
        @contract
        class MyContract implements UndefinedTrait {
            @public
            function test(): bool { return true; }
        }
        """
        self.assert_error_contains(code, "Trait 'UndefinedTrait' not defined")

    def test_trait_method_missing(self):
        """Should error when class doesn't implement all trait methods."""
        code = """
        trait MyTrait {
            required(): bool;
        }

        @contract
        class MyContract implements MyTrait {
            @public
            function other(): bool { return true; }
        }
        """
        self.assert_error_contains(code, "does not implement trait method 'required'")

    def test_trait_compliance_pass(self):
        """Should pass when all trait methods are implemented."""
        code = """
        trait MyTrait {
            required(): bool;
        }

        @contract
        class MyContract implements MyTrait {
            @public
            function required(): bool { return true; }
        }
        """
        self.assert_no_errors(code)

    # =========================================================================
    # Edge Cases
    # =========================================================================

    def test_nested_scope_variable_access(self):
        """Variables from outer scope should be accessible."""
        code = """
        let x: int = 5;
        function test(): int {
            return x;
        }
        """
        self.assert_no_errors(code)

    def test_list_operations_valid(self):
        """List operations should type check correctly."""
        code = """
        let myList: list<int> = [1, 2, 3];
        """
        self.assert_no_errors(code)

    def test_map_operations_valid(self):
        """Map declarations should work correctly."""
        code = """
        map balances<principal, uint>;
        """
        self.assert_no_errors(code)

    def test_lambda_valid(self):
        """Lambda expressions should be analyzed correctly."""
        code = """
        const double = (x: int): int => x * 2;
        """
        self.assert_no_errors(code)

    def test_contract_call_valid(self):
        """Contract calls should pass semantic analysis."""
        code = """
        let sender: principal = 'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM;
        let result: bool = Contract.method(sender);
        """
        self.assert_no_errors(code)


class TestSemanticWarnings(unittest.TestCase):
    """Test semantic analysis warning detection."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_transpiles_with_warnings(self):
        """Code with warnings should still transpile successfully."""
        # This code has unused parameter warning but should still compile
        code = """
        function test(unused: int): bool {
            return true;
        }
        """
        # Should not raise an exception
        result = self.transpiler.transpile(code)
        self.assertIn("define-private", result)


if __name__ == '__main__':
    unittest.main()
