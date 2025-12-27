import unittest
import sys
import re
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from stxscript.transpiler import StxScriptTranspiler


def normalize_clarity(code: str) -> str:
    """Normalize Clarity code for comparison by removing extra whitespace"""
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in code.strip().split('\n')]
    # Remove empty lines
    lines = [line for line in lines if line]
    # Join with single newline
    return '\n'.join(lines)


class TestStxScriptTranspiler(unittest.TestCase):
    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def assert_transpile(self, stxscript, expected_clarity):
        result = self.transpiler.transpile(stxscript)
        # Normalize both for comparison
        normalized_result = normalize_clarity(result)
        normalized_expected = normalize_clarity(expected_clarity)
        self.assertEqual(normalized_result, normalized_expected)

    def test_variable_declaration(self):
        stxscript = "let x: int = 5;"
        expected_clarity = "(define-data-var x int 5)"
        self.assert_transpile(stxscript, expected_clarity)

    def test_constant_declaration(self):
        stxscript = "const MAX_VALUE: uint = 100u;"
        expected_clarity = "(define-constant MAX_VALUE u100)"
        self.assert_transpile(stxscript, expected_clarity)

    def test_public_function_declaration(self):
        stxscript = """
        @public
        function greet(name: string): Response<bool, string> {
            return ok(true);
        }
        """
        expected_clarity = """
        (define-public (greet (name string))
          (ok true))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_lambda_function(self):
        stxscript = "const double = (x: int): int => x * 2;"
        expected_clarity = "(define-private (double (x int)) (* x 2))"
        self.assert_transpile(stxscript, expected_clarity)

    def test_trait_declaration(self):
        stxscript = """
        trait TokenTrait {
            transfer(from: principal, to: principal, amount: uint): Response<bool, string>;
        }
        """
        # Generate and check structure
        result = self.transpiler.transpile(stxscript)
        # Just check that it contains the essential parts
        self.assertIn("define-trait", result)
        self.assertIn("TokenTrait", result)
        self.assertIn("transfer", result)

    def test_contract_declaration(self):
        stxscript = """
        trait TokenTrait {
            transfer(from: principal, to: principal, amount: uint): Response<bool, string>;
        }

        @contract
        class MyToken implements TokenTrait {
            @data
            balances: Map<principal, uint> = new Map<principal, uint>();

            @public
            function transfer(from: principal, to: principal, amount: uint): Response<bool, string> {
                return ok(true);
            }
        }
        """
        # Generate and check structure
        result = self.transpiler.transpile(stxscript)
        # Just check that it contains the essential parts
        self.assertIn("define-map", result)
        self.assertIn("balances", result)
        self.assertIn("define-public", result)
        self.assertIn("transfer", result)
        self.assertIn("impl-trait", result)
        self.assertIn("TokenTrait", result)

    def test_list_operations(self):
        stxscript = """
        let myList: list<int> = [1, 2, 3];
        """
        expected_clarity = """
        (define-data-var my-list (list int) (list 1 2 3))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_optional_and_unwrapping(self):
        stxscript = """
        let optValue: optional<int> = some(5);
        let unwrapped: int = optValue!;
        let safeUnwrapped: int = optValue ?? 0;
        """
        expected_clarity = """
        (define-data-var opt-value (optional int) (some 5))
        (define-data-var unwrapped int (unwrap! opt-value (err "Unwrap failed")))
        (define-data-var safe-unwrapped int (default-to 0 opt-value))
        """
        # Run and print for debugging
        result = self.transpiler.transpile(stxscript)
        normalized_result = normalize_clarity(result)
        normalized_expected = normalize_clarity(expected_clarity)
        self.assertEqual(normalized_result, normalized_expected)

    def test_asset_declaration(self):
        stxscript = """
        @asset
        class NFT {
            id: uint;
            owner: principal;
        }
        """
        expected_clarity = """
        (define-non-fungible-token NFT uint)
        (define-map nft-owners uint principal)
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_contract_call(self):
        stxscript = """
        let sender: principal = 'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM;
        let recipient: principal = 'ST2CY5V39NHDPWSXMW9QDT3HC3GD6Q6XX4CFRK9AG;
        let amount: uint = 100u;
        let result: boolean = TokenContract.transfer(sender, recipient, amount);
        """
        expected_clarity = """
        (define-data-var sender principal 'ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM)
        (define-data-var recipient principal 'ST2CY5V39NHDPWSXMW9QDT3HC3GD6Q6XX4CFRK9AG)
        (define-data-var amount uint u100)
        (define-data-var result bool (contract-call? .TokenContract transfer sender recipient amount))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_bitwise_operations(self):
        stxscript = """
        let a: int = 5;
        let b: int = 3;
        let bitwiseAnd: int = a & b;
        let bitwiseOr: int = a | b;
        let bitwiseXor: int = a ^ b;
        let bitwiseNot: int = ~a;
        let leftShift: int = a << 1;
        let rightShift: int = a >> 1;
        """
        expected_clarity = """
        (define-data-var a int 5)
        (define-data-var b int 3)
        (define-data-var bitwise-and int (bit-and a b))
        (define-data-var bitwise-or int (bit-or a b))
        (define-data-var bitwise-xor int (bit-xor a b))
        (define-data-var bitwise-not int (bit-not a))
        (define-data-var left-shift int (bit-shift-left a u1))
        (define-data-var right-shift int (bit-shift-right a u1))
        """
        self.assert_transpile(stxscript, expected_clarity)

if __name__ == '__main__':
    unittest.main()