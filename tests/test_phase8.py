"""
Tests for Phase 8: Advanced Language Features

Tests cover:
- 8A.1: Type Aliases
- 8A.2: Buffer Sizes
- 8A.3: Generics
- 8B: For Loops
- 8C: Module System
- 8D: While Loops
"""

import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from stxscript.transpiler import StxScriptTranspiler, SemanticError


class TestTypeAliases(unittest.TestCase):
    """Test type alias feature (8A.1)."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_simple_type_alias(self):
        """Type alias should compile to a comment."""
        code = """
        type Amount = uint;
        """
        result = self.transpiler.transpile(code)
        self.assertIn(";; type Amount = uint", result)

    def test_type_alias_usage(self):
        """Variables should be able to use type aliases."""
        code = """
        type Amount = uint;
        let balance: Amount = 100u;
        """
        result = self.transpiler.transpile(code)
        self.assertIn(";; type Amount = uint", result)
        # Type can be emitted as alias name or resolved type
        self.assertIn("define-data-var balance", result)
        self.assertIn("u100", result)

    def test_type_alias_in_function(self):
        """Functions should be able to use type aliases for parameters and returns."""
        code = """
        type Amount = uint;
        function getBalance(amount: Amount): Amount {
            return amount;
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn("define-private", result)
        # The type should resolve to uint
        self.assertIn("uint", result)

    def test_type_alias_response(self):
        """Type alias for Response type."""
        code = """
        type Result = Response<bool, string>;
        function test(): Result {
            return ok(true);
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn(";; type Result = (response bool string)", result)

    def test_type_alias_optional(self):
        """Type alias for optional type."""
        code = """
        type MaybeInt = optional<int>;
        let x: MaybeInt = some(5);
        """
        result = self.transpiler.transpile(code)
        self.assertIn(";; type MaybeInt = (optional int)", result)

    def test_type_alias_list(self):
        """Type alias for list type."""
        code = """
        type IntList = list<int>;
        let nums: IntList = [1, 2, 3];
        """
        result = self.transpiler.transpile(code)
        self.assertIn(";; type IntList = (list int)", result)

    def test_chained_type_alias(self):
        """Chained type aliases should resolve correctly for semantic checking."""
        code = """
        type Amount = uint;
        type Balance = Amount;
        let x: Balance = 50u;
        """
        # Should compile without type errors (Balance -> Amount -> uint)
        result = self.transpiler.transpile(code)
        self.assertIn("define-data-var x", result)
        self.assertIn("u50", result)

    def test_type_alias_duplicate_error(self):
        """Duplicate type alias should produce an error."""
        code = """
        type Amount = uint;
        type Amount = int;
        """
        try:
            self.transpiler.transpile(code)
            self.fail("Expected SemanticError for duplicate type alias")
        except SemanticError as e:
            self.assertTrue(any("already defined" in str(err).lower() for err in e.errors))

    def test_type_alias_in_function_param(self):
        """Type alias should work in function parameters."""
        code = """
        type UserId = principal;
        function getUser(id: UserId): bool {
            return true;
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn("principal", result)

    def test_type_alias_semantic_validation(self):
        """Type alias should be validated semantically."""
        code = """
        type Amount = uint;
        let x: Amount = "hello";
        """
        try:
            self.transpiler.transpile(code)
            self.fail("Expected SemanticError for type mismatch")
        except SemanticError as e:
            self.assertTrue(any("type mismatch" in str(err).lower() for err in e.errors))


class TestTupleTypes(unittest.TestCase):
    """Test tuple type parsing."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_tuple_type_alias(self):
        """Tuple type in type alias."""
        code = """
        type User = { name: string, age: uint };
        """
        result = self.transpiler.transpile(code)
        self.assertIn(";; type User =", result)


class TestGenerics(unittest.TestCase):
    """Test generic type parameters (8A.3)."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_simple_generic_function(self):
        """Generic function with one type parameter."""
        code = """
        function identity<T>(x: T): T {
            return x;
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn("define-private", result)
        self.assertIn("identity", result)

    def test_generic_function_two_params(self):
        """Generic function with two type parameters."""
        code = """
        function pair<T, U>(first: T, second: U): bool {
            return true;
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn("define-private", result)
        self.assertIn("pair", result)

    def test_generic_function_call(self):
        """Calling a generic function."""
        code = """
        function identity<T>(x: T): T {
            return x;
        }
        let num: int = identity(5);
        """
        result = self.transpiler.transpile(code)
        self.assertIn("identity", result)

    def test_generic_with_concrete_types(self):
        """Generic function used with concrete types."""
        code = """
        function first<T>(x: T, y: int): T {
            return x;
        }
        let result: string = first("hello", 42);
        """
        result = self.transpiler.transpile(code)
        self.assertIn("first", result)


class TestWhileLoops(unittest.TestCase):
    """Test while loop feature (8D)."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_simple_while_loop(self):
        """Basic while loop should compile."""
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
        self.assertIn("while loop", result)

    def test_while_loop_with_condition(self):
        """While loop with boolean condition."""
        code = """
        function count(): bool {
            let done: bool = false;
            while (done == false) {
                done = true;
            }
            return done;
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn("fold", result)

    def test_while_loop_bounded(self):
        """While loop generates bounded fold."""
        code = """
        function test(): int {
            while (true) {
                let x: int = 0;
            }
            return 0;
        }
        """
        result = self.transpiler.transpile(code)
        # Should mention bounded iterations
        self.assertIn("bounded", result)


class TestForLoops(unittest.TestCase):
    """Test for loop feature (8B)."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_simple_for_loop(self):
        """Basic for loop should compile."""
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

    def test_for_loop_range_extraction(self):
        """For loop should extract range bounds."""
        code = """
        function count(): int {
            for (let i = 0; i < 3; i = i + 1) {
                let x: int = i;
            }
            return 0;
        }
        """
        result = self.transpiler.transpile(code)
        # Should generate list with u0 u1 u2
        self.assertIn("u0", result)
        self.assertIn("u1", result)
        self.assertIn("u2", result)

    def test_for_loop_variable_scope(self):
        """Loop variable should be accessible in body."""
        code = """
        function test(): int {
            for (let idx = 0; idx < 10; idx = idx + 1) {
                let val: int = idx + 1;
            }
            return 0;
        }
        """
        # Should compile without undefined variable error
        result = self.transpiler.transpile(code)
        self.assertIn("fold", result)


class TestBufferSizes(unittest.TestCase):
    """Test buffer size feature (8A.2)."""

    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def test_sized_buffer_declaration(self):
        """buffer<N> should generate (buff N)."""
        code = """
        function hash(data: buffer<64>): bool {
            return true;
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn("(buff 64)", result)

    def test_default_buffer_size(self):
        """Unsized buffer should default to (buff 32)."""
        code = """
        function process(data: buffer): bool {
            return true;
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn("(buff 32)", result)

    def test_buffer_variable(self):
        """Buffer type in function parameter."""
        code = """
        function storeHash(hash: buffer<32>): bool {
            return true;
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn("(buff 32)", result)

    def test_buffer_different_sizes(self):
        """Multiple buffer sizes should work."""
        code = """
        function process(small: buffer<16>, large: buffer<128>): bool {
            return true;
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn("(buff 16)", result)
        self.assertIn("(buff 128)", result)

    def test_buffer_type_alias(self):
        """Type alias for buffer size."""
        code = """
        type Hash = buffer<32>;
        function getHash(h: Hash): bool {
            return true;
        }
        """
        result = self.transpiler.transpile(code)
        self.assertIn(";; type Hash =", result)


if __name__ == '__main__':
    unittest.main()
