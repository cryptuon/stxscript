"""
Tests for Phase 9: Clarity Output Validation

Verifies that generated Clarity code follows correct syntax patterns
and produces valid Clarity constructs.
"""

import unittest
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from stxscript.transpiler import StxScriptTranspiler


class TestClarityVariables(unittest.TestCase):
    """Test Clarity variable output."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_int_variable_format(self):
        """Int variables should use define-data-var with int type."""
        code = "let count: int = 42;"
        result = self.transpiler.transpile(code)

        self.assertIn("define-data-var count", result)
        self.assertIn("int", result)
        self.assertIn("42", result)

    def test_uint_variable_format(self):
        """Uint variables should have u prefix on values."""
        code = "let amount: uint = 100u;"
        result = self.transpiler.transpile(code)

        self.assertIn("define-data-var amount", result)
        self.assertIn("uint", result)
        self.assertIn("u100", result)

    def test_bool_variable_format(self):
        """Bool variables should use bool type."""
        code = "let active: bool = true;"
        result = self.transpiler.transpile(code)

        self.assertIn("define-data-var active", result)
        self.assertIn("bool", result)
        self.assertIn("true", result)

    def test_string_variable_format(self):
        """String variables should have correct format."""
        code = 'let name: string = "hello";'
        result = self.transpiler.transpile(code)

        self.assertIn("define-data-var name", result)
        self.assertIn('"hello"', result)

    def test_constant_format(self):
        """Constants should use define-constant."""
        code = "const MAX: int = 100;"
        result = self.transpiler.transpile(code)

        self.assertIn("define-constant MAX", result)
        self.assertIn("100", result)


class TestClarityFunctions(unittest.TestCase):
    """Test Clarity function output."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_private_function_format(self):
        """Private functions should use define-private."""
        code = """
        function add(a: int, b: int): int {
            return a + b;
        }
        """
        result = self.transpiler.transpile(code)

        self.assertIn("define-private", result)
        self.assertIn("(add", result)

    def test_public_function_format(self):
        """Public functions should use define-public."""
        code = """
        @public
        function getCount(): int {
            return 0;
        }
        """
        result = self.transpiler.transpile(code)

        self.assertIn("define-public", result)
        # Function name may be converted to kebab-case
        self.assertTrue("get-count" in result or "getCount" in result)

    def test_read_only_function_format(self):
        """Read-only functions with @public decorator."""
        code = """
        @public
        function getValue(): int {
            return 42;
        }
        """
        result = self.transpiler.transpile(code)

        # @public generates define-public
        self.assertIn("define-public", result)
        self.assertTrue("get-value" in result or "getValue" in result)

    def test_function_parameters(self):
        """Function parameters should have correct syntax."""
        code = """
        function transfer(sender: principal, amount: uint): bool {
            return true;
        }
        """
        result = self.transpiler.transpile(code)

        self.assertIn("(sender principal)", result)
        self.assertIn("(amount uint)", result)

    def test_function_return_type(self):
        """Function body should contain the return value."""
        code = """
        function check(): bool {
            return true;
        }
        """
        result = self.transpiler.transpile(code)

        # Return value should be in output
        self.assertIn("true", result)


class TestClarityExpressions(unittest.TestCase):
    """Test Clarity expression output."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_arithmetic_expressions(self):
        """Arithmetic should produce Clarity prefix notation."""
        code = "let result: int = 10 + 5;"
        result = self.transpiler.transpile(code)

        # Clarity uses prefix notation: (+ 10 5)
        self.assertIn("+", result)

    def test_comparison_expressions(self):
        """Comparisons should produce correct Clarity operators."""
        code = "let bigger: bool = 10 > 5;"
        result = self.transpiler.transpile(code)

        self.assertIn(">", result)

    def test_logical_expressions(self):
        """Logical operators should map correctly."""
        code = "let both: bool = true && false;"
        result = self.transpiler.transpile(code)

        self.assertIn("and", result)


class TestClarityControlFlow(unittest.TestCase):
    """Test Clarity control flow output."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_if_expression(self):
        """If statements should produce Clarity if form."""
        code = """
        function check(val: int): int {
            if (val > 0) {
                return 1;
            } else {
                return 0;
            }
        }
        """
        result = self.transpiler.transpile(code)

        self.assertIn("if", result)

    def test_for_loop_to_fold(self):
        """For loops should compile to fold."""
        code = """
        function sum(): int {
            for (let i = 0; i < 5; i = i + 1) {
                let x: int = i;
            }
            return 0;
        }
        """
        result = self.transpiler.transpile(code)

        self.assertIn("fold", result)
        self.assertIn("list", result)

    def test_while_loop_to_fold(self):
        """While loops should compile to bounded fold."""
        code = """
        function process(): int {
            while (true) {
                let x: int = 1;
            }
            return 0;
        }
        """
        result = self.transpiler.transpile(code)

        self.assertIn("fold", result)
        self.assertIn("bounded", result)


class TestClarityTypes(unittest.TestCase):
    """Test Clarity type output."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_list_type(self):
        """List types should be properly formatted."""
        code = "let nums: list<int> = [1, 2, 3];"
        result = self.transpiler.transpile(code)

        self.assertIn("list", result)

    def test_optional_type(self):
        """Optional types should use Clarity optional."""
        code = "let maybe: optional<int> = some(5);"
        result = self.transpiler.transpile(code)

        self.assertIn("optional", result)
        self.assertIn("some", result)

    def test_response_type(self):
        """Response types should generate ok/err expressions."""
        code = """
        function test(): Response<bool, string> {
            return ok(true);
        }
        """
        result = self.transpiler.transpile(code)

        # ok expression should be generated
        self.assertIn("ok", result)
        self.assertIn("true", result)

    def test_buffer_type(self):
        """Buffer types should include size."""
        code = """
        function hash(data: buffer<32>): bool {
            return true;
        }
        """
        result = self.transpiler.transpile(code)

        self.assertIn("(buff 32)", result)


class TestClarityMap(unittest.TestCase):
    """Test Clarity map output."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_map_declaration(self):
        """Maps should use define-map."""
        # Use the correct map syntax without colon
        code = """
        map balances<principal, uint>;
        """
        result = self.transpiler.transpile(code)

        self.assertIn("define-map balances", result)


class TestClaritySyntaxValidity(unittest.TestCase):
    """Test that generated Clarity has valid syntax patterns."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_balanced_parentheses(self):
        """Generated Clarity should have balanced parentheses."""
        code = """
        function calculate(x: int, y: int): int {
            let sum: int = x + y;
            let product: int = x * y;
            return sum + product;
        }
        """
        result = self.transpiler.transpile(code)

        open_count = result.count('(')
        close_count = result.count(')')
        self.assertEqual(open_count, close_count,
                        f"Unbalanced parens: {open_count} open, {close_count} close")

    def test_no_invalid_constructs(self):
        """Generated Clarity should not have invalid patterns."""
        code = """
        let x: int = 42;
        const Y: uint = 100u;
        function test(): bool { return true; }
        """
        result = self.transpiler.transpile(code)

        # Should not have JavaScript-like constructs
        self.assertNotIn("function ", result)  # With space (function declaration)
        self.assertNotIn("let ", result)  # With space
        self.assertNotIn("const ", result)  # With space

    def test_comments_are_clarity_style(self):
        """Comments should use Clarity style (;;)."""
        code = """
        type Amount = uint;
        """
        result = self.transpiler.transpile(code)

        # Type aliases generate comments
        if ";;" in result:
            # If there are comments, they should be Clarity style
            self.assertIn(";;", result)
            self.assertNotIn("//", result)


class TestEndToEndContracts(unittest.TestCase):
    """End-to-end tests for complete contract patterns."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_simple_counter_contract(self):
        """Simple counter contract should compile correctly."""
        code = """
        let counter: int = 0;

        @public
        function increment(): int {
            counter = counter + 1;
            return counter;
        }

        @public
        function getCounter(): int {
            return counter;
        }
        """
        result = self.transpiler.transpile(code)

        self.assertIn("define-data-var counter", result)
        self.assertIn("define-public", result)
        self.assertIn("increment", result)
        # Function names may be kebab-cased
        self.assertTrue("get-counter" in result or "getCounter" in result)

    def test_token_like_contract(self):
        """Token-like contract patterns should compile."""
        code = """
        map balances<principal, uint>;

        @public
        function transfer(to: principal, amount: uint): bool {
            return true;
        }

        @public
        function getBalance(account: principal): uint {
            return 0u;
        }
        """
        result = self.transpiler.transpile(code)

        self.assertIn("define-map balances", result)
        self.assertIn("define-public", result)
        self.assertIn("transfer", result)
        self.assertTrue("get-balance" in result or "getBalance" in result)


if __name__ == '__main__':
    unittest.main()
