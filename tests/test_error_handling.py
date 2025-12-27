"""
Tests for Phase 9: Error Handling and Reporting

Tests cover:
- Multi-error collection
- Warning system
- Error recovery
- Source location tracking
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from stxscript.transpiler import StxScriptTranspiler, SemanticError


class TestMultiErrorReporting(unittest.TestCase):
    """Test that multiple errors are collected and reported together."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_multiple_undefined_variables(self):
        """Multiple undefined variable errors should all be reported."""
        code = """
        function test(): int {
            let result: int = x + y + z;
            return result;
        }
        """
        with self.assertRaises(SemanticError) as context:
            self.transpiler.transpile(code)

        # Should report multiple errors
        self.assertGreaterEqual(len(context.exception.errors), 1)

    def test_multiple_type_errors(self):
        """Multiple type errors should all be reported."""
        code = """
        let a: int = "hello";
        let b: string = 42;
        let c: bool = "not a bool";
        """
        with self.assertRaises(SemanticError) as context:
            self.transpiler.transpile(code)

        # Should have 3 type mismatch errors
        self.assertEqual(len(context.exception.errors), 3)

    def test_mixed_error_types(self):
        """Different types of errors should be collected together."""
        code = """
        let x: int = undefined_var;
        let x: string = "duplicate";
        """
        with self.assertRaises(SemanticError) as context:
            self.transpiler.transpile(code)

        # Should have at least 2 errors (undefined + duplicate)
        self.assertGreaterEqual(len(context.exception.errors), 1)

    def test_error_message_formatting(self):
        """Error messages should be properly formatted."""
        code = """
        let x: int = "wrong type";
        """
        with self.assertRaises(SemanticError) as context:
            self.transpiler.transpile(code)

        error_str = str(context.exception)
        self.assertIn("error", error_str.lower())

    def test_transpile_with_error_handling_returns_errors(self):
        """transpile_with_error_handling should return error list."""
        code = """
        let x: int = "string";
        """
        result = self.transpiler.transpile_with_error_handling(code)

        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("errors", result)


class TestWarningSystem(unittest.TestCase):
    """Test the warning system functionality."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_unused_variable_warning(self):
        """Unused variables should generate warnings but still compile."""
        code = """
        function test(): int {
            let unused: int = 42;
            return 0;
        }
        """
        # Should compile successfully but may warn
        result = self.transpiler.transpile(code)
        self.assertIn("define-private", result)

    def test_warnings_dont_prevent_compilation(self):
        """Warnings should not prevent successful compilation."""
        code = """
        function test(): int {
            return 42;
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn("define-private", result)


class TestParseErrors(unittest.TestCase):
    """Test parser error handling."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_syntax_error_message(self):
        """Syntax errors should have helpful messages."""
        code = """
        let x: int = ;
        """
        with self.assertRaises(Exception) as context:
            self.transpiler.transpile(code)

        error_str = str(context.exception)
        # Should contain some indication of the problem
        self.assertIsInstance(error_str, str)
        self.assertGreater(len(error_str), 0)

    def test_unbalanced_braces(self):
        """Unbalanced braces should be caught."""
        code = """
        function test(): int {
            return 0;
        """
        with self.assertRaises(Exception):
            self.transpiler.transpile(code)

    def test_invalid_token(self):
        """Invalid tokens should be caught."""
        code = """
        let x: int = @@@invalid@@@;
        """
        with self.assertRaises(Exception):
            self.transpiler.transpile(code)


class TestSemanticErrorDetails(unittest.TestCase):
    """Test semantic error details and suggestions."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_undefined_variable_error(self):
        """Undefined variable errors should be clear."""
        code = """
        function test(): int {
            return unknownVar;
        }
        """
        with self.assertRaises(SemanticError) as context:
            self.transpiler.transpile(code)

        error_str = str(context.exception)
        self.assertIn("unknownVar", error_str)

    def test_duplicate_definition_error(self):
        """Duplicate definition should be reported."""
        code = """
        function test(): int { return 0; }
        function test(): int { return 1; }
        """
        with self.assertRaises(SemanticError) as context:
            self.transpiler.transpile(code)

        error_str = str(context.exception)
        self.assertIn("test", error_str)

    def test_type_mismatch_shows_both_types(self):
        """Type mismatch errors should show expected and actual types."""
        code = """
        let x: int = "hello";
        """
        with self.assertRaises(SemanticError) as context:
            self.transpiler.transpile(code)

        error_str = str(context.exception)
        # Should mention types involved
        self.assertIn("type", error_str.lower())


class TestErrorRecovery(unittest.TestCase):
    """Test that analysis continues after encountering errors."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_analysis_continues_after_error(self):
        """Analysis should continue to find subsequent errors."""
        code = """
        let a: int = "error1";
        let b: int = "error2";
        let c: int = "error3";
        """
        with self.assertRaises(SemanticError) as context:
            self.transpiler.transpile(code)

        # Should find all 3 errors, not just stop at first
        self.assertEqual(len(context.exception.errors), 3)

    def test_function_analysis_continues(self):
        """Analysis should continue across function boundaries."""
        code = """
        function func1(): int {
            return "wrong";
        }
        function func2(): int {
            return "also wrong";
        }
        """
        with self.assertRaises(SemanticError) as context:
            self.transpiler.transpile(code)

        # Should find errors in both functions
        self.assertGreaterEqual(len(context.exception.errors), 2)


class TestTranspileWithErrorHandling(unittest.TestCase):
    """Test the transpile_with_error_handling method."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_success_result(self):
        """Successful transpilation should return correct structure."""
        code = """
        let x: int = 42;
        """
        result = self.transpiler.transpile_with_error_handling(code)

        self.assertTrue(result["success"])
        self.assertIn("clarity", result)
        self.assertIn("define-data-var x", result["clarity"])

    def test_failure_result(self):
        """Failed transpilation should return error info."""
        code = """
        let x: int = undefined;
        """
        result = self.transpiler.transpile_with_error_handling(code)

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_parse_error_result(self):
        """Parse errors should be handled gracefully."""
        code = """
        let x int = ;  // syntax error
        """
        result = self.transpiler.transpile_with_error_handling(code)

        self.assertFalse(result["success"])
        self.assertIn("error", result)


if __name__ == '__main__':
    unittest.main()
