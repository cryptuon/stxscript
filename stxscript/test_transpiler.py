import unittest
from .transpiler import StxScriptTranspiler

class TestStxScriptTranspiler(unittest.TestCase):
    def setUp(self):
        self.transpiler = StxScriptTranspiler()

    def assert_transpile(self, stxscript, expected_clarity):
        result = self.transpiler.transpile(stxscript)
        self.assertEqual(result.strip(), expected_clarity.strip())

    def test_function_declaration(self):
        stxscript = """
        @public
        function add(a: int, b: int): int {
            return a + b;
        }
        """
        expected_clarity = """
        (define-public (add (a int) (b int))
          (+ a b))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_variable_declaration(self):
        stxscript = "let x: int = 5;"
        expected_clarity = "(define-data-var x int 5)"
        self.assert_transpile(stxscript, expected_clarity)

    def test_constant_declaration(self):
        stxscript = "const PI: int = 314;"
        expected_clarity = "(define-constant PI 314)"
        self.assert_transpile(stxscript, expected_clarity)

    def test_map_declaration(self):
        stxscript = """
        @map({ key: principal, value: uint })
        const balances = new Map<principal, uint>();
        """
        expected_clarity = "(define-map balances principal uint)"
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
        (define-non-fungible-token NFT (id uint) (owner principal))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_trait_declaration(self):
        stxscript = """
        trait Token {
            transfer(from: principal, to: principal, amount: uint): Response<bool, uint>;
            getBalance(account: principal): Response<uint, uint>;
        }
        """
        expected_clarity = """
        (define-trait Token
          ((transfer (principal principal uint) (response bool uint))
           (getBalance (principal) (response uint uint))))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_if_statement(self):
        stxscript = """
        function max(a: int, b: int): int {
            if (a > b) {
                return a;
            } else {
                return b;
            }
        }
        """
        expected_clarity = """
        (define-private (max (a int) (b int))
          (if (> a b)
            a
            b))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_try_catch_statement(self):
        stxscript = """
        function divide(a: int, b: int): Response<int, string> {
            try {
                return ok(a / b);
            } catch (error) {
                return err("Division by zero");
            }
        }
        """
        expected_clarity = """
        (define-private (divide (a int) (b int))
          (try
            (ok (/ a b))
            (catch error (err "Division by zero"))))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_list_operations(self):
        stxscript = """
        function sumList(numbers: list<int>): int {
            return fold(numbers, 0, (acc: int, x: int) => acc + x);
        }
        """
        expected_clarity = """
        (define-private (sumList (numbers (list int)))
          (fold numbers 0 (lambda (acc x) (+ acc x))))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_contract_call(self):
        stxscript = """
        function transferToken(to: principal, amount: uint): Response<bool, uint> {
            return TokenContract.transfer(tx.sender, to, amount);
        }
        """
        expected_clarity = """
        (define-private (transferToken (to principal) (amount uint))
          (contract-call? .TokenContract transfer tx-sender to amount))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_asset_call(self):
        stxscript = """
        function mintNFT(recipient: principal, id: uint): Response<bool, string> {
            return NFT.mint(recipient, id);
        }
        """
        expected_clarity = """
        (define-private (mintNFT (recipient principal) (id uint))
          (nft-mint? NFT id recipient))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_list_comprehension(self):
        stxscript = """
        function doubleEvens(numbers: list<int>): list<int> {
            return [x * 2 for x in numbers if x % 2 == 0];
        }
        """
        expected_clarity = """
        (define-private (doubleEvens (numbers (list int)))
          (map (* 2) (filter (lambda (x) (is-eq (mod x 2) 0)) numbers)))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_type_assertion_and_check(self):
        stxscript = """
        function processValue(value: any): int {
            if (value is int) {
                return value as int;
            }
            return 0;
        }
        """
        expected_clarity = """
        (define-private (processValue (value (optional any)))
          (if (is-int value)
            (as int value)
            0))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_import_and_export(self):
        stxscript = """
        import { TokenTrait } from './token-trait';

        export function getBalance(account: principal): Response<uint, uint> {
            return TokenContract.getBalance(account);
        }
        """
        expected_clarity = """
        (use-trait TokenTrait .token-trait)

        (define-read-only (getBalance (account principal))
          (contract-call? .TokenContract getBalance account))
        """
        self.assert_transpile(stxscript, expected_clarity)

    def test_complex_function(self):
        stxscript = """
        @public
        function complexOperation(
            a: int,
            b: uint,
            c: principal
        ): Response<{value: int, owner: principal}, string> {
            let x = a + (b as int);
            if (x > 100) {
                return err("Value too high");
            }
            
            try {
                let result = TokenContract.mint(c, (x as uint));
                if (result.isOk()) {
                    return ok({value: x, owner: c});
                } else {
                    return err("Minting failed");
                }
            } catch (error) {
                return err("Unexpected error");
            }
        }
        """
        expected_clarity = """
        (define-public (complexOperation (a int) (b uint) (c principal))
          (let ((x (+ a (to-int b))))
            (if (> x 100)
              (err "Value too high")
              (try
                (let ((result (contract-call? .TokenContract mint c (to-uint x))))
                  (if (is-ok result)
                    (ok (tuple (value x) (owner c)))
                    (err "Minting failed")))
                (catch error (err "Unexpected error"))))))
        """
        self.assert_transpile(stxscript, expected_clarity)

if __name__ == '__main__':
    unittest.main()