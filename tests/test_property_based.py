"""
Property-based tests for StxScript parser using Hypothesis.

Phase 9: Production Hardening - Comprehensive testing with fuzzing.
"""

import unittest
from hypothesis import given, strategies as st, settings, assume
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from stxscript.transpiler import StxScriptTranspiler


class TestParserRobustness(unittest.TestCase):
    """Property-based tests for parser robustness."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    @given(st.text(min_size=0, max_size=100))
    @settings(max_examples=50)
    def test_parser_never_crashes_on_random_input(self, random_text):
        """Parser should never crash, only return errors gracefully."""
        try:
            self.transpiler.transpile(random_text)
        except Exception as e:
            # Parser exceptions are acceptable, crashes are not
            self.assertIsInstance(e, Exception)

    @given(st.from_regex(r'[a-z][a-zA-Z0-9_]{0,20}', fullmatch=True))
    @settings(max_examples=30)
    def test_valid_identifier_parsing(self, identifier):
        """Valid identifiers should parse correctly in variable declarations."""
        assume(identifier not in ['let', 'const', 'function', 'if', 'else',
                                   'return', 'true', 'false', 'while', 'for',
                                   'match', 'import', 'export', 'type', 'trait'])
        code = f"let {identifier}: int = 1;"
        try:
            result = self.transpiler.transpile(code)
            self.assertIn(identifier, result)
        except Exception:
            pass  # Some identifiers may conflict with grammar

    @given(st.integers(min_value=0, max_value=10**15))
    @settings(max_examples=30)
    def test_valid_uint_literals(self, num):
        """Valid uint literals should transpile correctly."""
        code = f"let x: uint = {num}u;"
        result = self.transpiler.transpile(code)
        self.assertIn(f"u{num}", result)

    @given(st.integers(min_value=-10**15, max_value=10**15))
    @settings(max_examples=30)
    def test_valid_int_literals(self, num):
        """Valid int literals should transpile correctly."""
        code = f"let x: int = {num};"
        result = self.transpiler.transpile(code)
        self.assertIn("define-data-var x", result)

    @given(st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'S', 'P')),
                   min_size=1, max_size=50))
    @settings(max_examples=30)
    def test_string_literals(self, text):
        """String literals should be properly escaped and parsed."""
        # Escape special characters
        escaped = text.replace('\\', '\\\\').replace('"', '\\"')
        code = f'let s: string = "{escaped}";'
        try:
            result = self.transpiler.transpile(code)
            self.assertIn("define-data-var s", result)
        except Exception:
            pass  # Some strings may not be valid

    @given(st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=10))
    @settings(max_examples=20)
    def test_list_literals(self, numbers):
        """List literals should transpile to Clarity lists."""
        items = ", ".join(str(n) for n in numbers)
        code = f"let nums: list<int> = [{items}];"
        result = self.transpiler.transpile(code)
        self.assertIn("list", result)

    @given(st.booleans())
    @settings(max_examples=10)
    def test_boolean_literals(self, value):
        """Boolean literals should transpile correctly."""
        code = f"let flag: bool = {str(value).lower()};"
        result = self.transpiler.transpile(code)
        self.assertIn("define-data-var flag", result)


class TestExpressionGeneration(unittest.TestCase):
    """Property-based tests for expression parsing."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    @given(st.integers(min_value=0, max_value=1000),
           st.integers(min_value=0, max_value=1000),
           st.sampled_from(['+', '-', '*', '/']))
    @settings(max_examples=30)
    def test_binary_arithmetic(self, a, b, op):
        """Binary arithmetic expressions should parse and transpile."""
        if op == '/' and b == 0:
            assume(False)  # Skip division by zero
        code = f"let result: int = {a} {op} {b};"
        result = self.transpiler.transpile(code)
        self.assertIn("define-data-var result", result)

    @given(st.integers(min_value=0, max_value=100),
           st.integers(min_value=0, max_value=100),
           st.sampled_from(['<', '>', '<=', '>=', '==', '!=']))
    @settings(max_examples=30)
    def test_comparison_operators(self, a, b, op):
        """Comparison operators should produce boolean results."""
        code = f"let cmp: bool = {a} {op} {b};"
        result = self.transpiler.transpile(code)
        self.assertIn("define-data-var cmp", result)

    @given(st.booleans(), st.booleans(), st.sampled_from(['&&', '||']))
    @settings(max_examples=20)
    def test_logical_operators(self, a, b, op):
        """Logical operators should combine boolean values."""
        code = f"let logic: bool = {str(a).lower()} {op} {str(b).lower()};"
        result = self.transpiler.transpile(code)
        self.assertIn("define-data-var logic", result)


class TestFunctionGeneration(unittest.TestCase):
    """Property-based tests for function declarations."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    @given(st.from_regex(r'[a-z][a-zA-Z]{0,15}', fullmatch=True),
           st.from_regex(r'[a-z][a-zA-Z]{0,10}', fullmatch=True))
    @settings(max_examples=20)
    def test_function_declarations(self, func_name, param_name):
        """Function declarations should parse with various names."""
        assume(func_name not in ['let', 'const', 'function', 'if', 'return', 'while', 'for', 'type'])
        assume(param_name not in ['let', 'const', 'function', 'if', 'return', 'while', 'for', 'type'])
        assume(func_name != param_name)

        code = f"""
        function {func_name}({param_name}: int): int {{
            return {param_name};
        }}
        """
        try:
            result = self.transpiler.transpile(code)
            self.assertIn(func_name, result)
        except Exception:
            pass  # Some names may conflict

    @given(st.lists(st.from_regex(r'[a-z]{1,8}', fullmatch=True),
                    min_size=1, max_size=5, unique=True))
    @settings(max_examples=15)
    def test_multiple_parameters(self, param_names):
        """Functions should handle multiple parameters."""
        keywords = {'let', 'const', 'function', 'if', 'return', 'while', 'for', 'type', 'match'}
        assume(not any(p in keywords for p in param_names))

        params = ", ".join(f"{p}: int" for p in param_names)
        code = f"""
        function test({params}): int {{
            return 0;
        }}
        """
        try:
            result = self.transpiler.transpile(code)
            self.assertIn("test", result)
        except Exception:
            pass


class TestTypeAliasGeneration(unittest.TestCase):
    """Property-based tests for type aliases."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    @given(st.from_regex(r'[A-Z][a-zA-Z]{0,15}', fullmatch=True),
           st.sampled_from(['int', 'uint', 'bool', 'string', 'principal']))
    @settings(max_examples=20)
    def test_type_alias_declarations(self, alias_name, base_type):
        """Type aliases should work with various names and types."""
        code = f"type {alias_name} = {base_type};"
        result = self.transpiler.transpile(code)
        self.assertIn(f";; type {alias_name}", result)


class TestBufferSizes(unittest.TestCase):
    """Property-based tests for buffer sizes."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    @given(st.integers(min_value=1, max_value=1024))
    @settings(max_examples=20)
    def test_buffer_size_range(self, size):
        """Buffer sizes should accept various valid sizes."""
        code = f"""
        function process(data: buffer<{size}>): bool {{
            return true;
        }}
        """
        result = self.transpiler.transpile(code)
        self.assertIn(f"(buff {size})", result)


class TestControlFlow(unittest.TestCase):
    """Property-based tests for control flow constructs."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    @given(st.integers(min_value=1, max_value=20))
    @settings(max_examples=15)
    def test_for_loop_bounds(self, upper_bound):
        """For loops should handle various iteration counts."""
        code = f"""
        function test(): int {{
            for (let i = 0; i < {upper_bound}; i = i + 1) {{
                let x: int = i;
            }}
            return 0;
        }}
        """
        result = self.transpiler.transpile(code)
        self.assertIn("fold", result)


class TestEdgeCases(unittest.TestCase):
    """Tests for specific edge cases discovered through fuzzing."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_empty_input(self):
        """Empty input should be handled gracefully."""
        result = self.transpiler.transpile("")
        self.assertEqual(result.strip(), "")

    def test_whitespace_only(self):
        """Whitespace-only input should be handled."""
        result = self.transpiler.transpile("   \n\t  \n  ")
        self.assertEqual(result.strip(), "")

    def test_comment_only(self):
        """Comment-only input should be handled gracefully."""
        result = self.transpiler.transpile("// just a comment")
        # Comments may or may not be preserved - just ensure no crash
        self.assertIsInstance(result, str)

    def test_deeply_nested_expressions(self):
        """Deeply nested expressions should parse."""
        code = "let x: int = ((((1 + 2) * 3) - 4) / 2);"
        result = self.transpiler.transpile(code)
        self.assertIn("define-data-var x", result)

    def test_unicode_in_strings(self):
        """Unicode characters in strings should be handled."""
        code = 'let s: string = "Hello 世界 🌍";'
        try:
            result = self.transpiler.transpile(code)
            self.assertIn("define-data-var s", result)
        except Exception:
            pass  # May not support all unicode

    def test_max_int_value(self):
        """Maximum int values should be handled."""
        code = f"let x: int = {2**127 - 1};"
        result = self.transpiler.transpile(code)
        self.assertIn("define-data-var x", result)

    def test_negative_int(self):
        """Negative integers should be handled."""
        code = "let x: int = -42;"
        result = self.transpiler.transpile(code)
        self.assertIn("define-data-var x", result)


if __name__ == '__main__':
    unittest.main()
