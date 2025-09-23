import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from stxscript.transpiler import StxScriptTranspiler

class TestStxScriptTranspiler(unittest.TestCase):
    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def assert_transpile(self, stxscript, expected_clarity):
        result = self.transpiler.transpile(stxscript)
        self.assertEqual(result.strip(), expected_clarity.strip())

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
        function transfer(from: principal, to: principal, amount: uint): Response<bool, string> {
            if (amount > getBalance(from)) {
                return err("Insufficient balance");
            }
            setBalance(from, getBalance(from) - amount);
            setBalance(to, getBalance(to) + amount);
            return ok(true);
        }
        """
        expected_clarity = """
        (define-public (transfer (from principal) (to principal) (amount uint))
          (if (> amount (get-balance from))
              (err "Insufficient balance")
              (begin
                (set-balance from (- (get-balance from) amount))
                (set-balance to (+ (get-balance to) amount))
                (ok true))))
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
            getBalance(account: principal): Response<uint, string>;
        }
        """
        expected_clarity = """
        (define-trait TokenTrait
          ((transfer (principal principal uint) (response bool string))
           (get-balance (principal) (response uint string))))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_contract_declaration(self):
        stxscript = """
        @contract
        class MyToken implements TokenTrait {
            @data
            balances: Map<principal, uint> = new Map<principal, uint>();

            @public
            function transfer(from: principal, to: principal, amount: uint): Response<bool, string> {
                // Implementation
            }

            @readable
            function getBalance(account: principal): Response<uint, string> {
                return ok(this.balances.get(account) ?? 0u);
            }
        }
        """
        expected_clarity = """
        (define-map balances principal uint)

        (define-public (transfer (from principal) (to principal) (amount uint))
          (begin
            ;; Implementation
          ))

        (define-read-only (get-balance (account principal))
          (ok (default-to u0 (map-get? balances account))))

        (impl-trait .TokenTrait)
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_list_operations(self):
        stxscript = """
        let myList: list<int> = [1, 2, 3];
        let doubled = map(myList, (x: int): int => x * 2);
        let sum = fold(doubled, 0, (acc: int, x: int): int => acc + x);
        """
        expected_clarity = """
        (define-data-var my-list (list 3 int) (list 1 2 3))
        (define-data-var doubled (list 3 int) (map (* 2) my-list))
        (define-data-var sum int (fold + doubled 0))
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
        self.assert_transpile(stxscript, expected_clarity)

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
        let result: boolean = TokenContract.transfer(sender, recipient, amount).limitHeight(10);
        """
        expected_clarity = """
        (define-data-var result bool 
          (contract-call? .TokenContract transfer sender recipient amount block-height))
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