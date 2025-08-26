from lark import Lark

with open('stxscript/simple_grammar.lark', 'r') as grammar_file:
    stxscript_parser = Lark(grammar_file.read(), start='start')

code = """
function add(a: int, b: int): int {
    return a + b;
}
@public
function transfer(from: principal, to: principal, amount: uint): Response<boolean, string> {
    if (amount > getBalance(from)) {
        return err("Insufficient balance");
    }
    setBalance(from, getBalance(from) - amount);
    setBalance(to, getBalance(to) + amount);
    return ok(true);
}

@contract
class MyToken implements TokenTrait {
    @data
    balances: Map<principal, uint> = new Map<principal, uint>();

    @public
    function transfer(from: principal, to: principal, amount: uint): Response<boolean, string> {
        // Implementation
    }

    @readable
    function getBalance(account: principal): Response<uint, string> {
        return ok(this.balances.get(account) ?? 0u);
    }
}

let myList: list<int> = [1, 2, 3];
let doubled = map(myList, (x: int): int => x * 2);
let sum = fold(doubled, 0, (acc: int, x: int): int => acc + x);

@asset
class NFT {
    id: uint;
    owner: principal;
}

let a: int = 5;
let b: int = 3;
let bitwiseAnd: int = a & b;
let bitwiseOr: int = a | b;
let bitwiseXor: int = a ^ b;
let bitwiseNot: int = ~a;
let leftShift: int = a << 1;
let rightShift: int = a >> 1;

let result: boolean = TokenContract.transfer(sender, recipient, amount).limitHeight(10);
let optValue: optional<int> = some(5);
let unwrapped: int = optValue!;
let safeUnwrapped: int = optValue ?? 0;

trait TokenTrait {
    transfer(from: principal, to: principal, amount: uint): Response<bool, string>;
    getBalance(account: principal): Response<uint, string>;
}

// Basic Types and Variables
let intValue: int = -100;
let uintValue: uint = 100u;
let boolValue: boolean = true;
let stringValue: string = "Hello, StxScript!";
let bufferValue: buffer = buffer(10);
let principalValue: principal = 'SP2J6ZY48GV1EZ5V2V5RB9MP66SW86PYKKNRV9EJ7';

// Complex Types
let listValue: list<int> = [1, 2, 3, 4, 5];
let tupleValue: { x: int, y: string } = { x: 10, y: "tuple" };
let optionalValue: optional<int> = some(5);

// Constants
const MAX_VALUE: uint = 1000u;

// Functions
function add(a: int, b: int): int {
    return a + b;
}

const multiply = (a: int, b: int): int => a * b;

// Decorators and Public Functions
@public
function transfer(sender: principal, recipient: principal, amount: uint): boolean {
    // Implementation
    return true;
}

@readable
function getBalance(account: principal): uint {
    // Implementation
    return 100u;
}

// Control Structures and Error Handling
function divideIfEven(a: int, b: int): Response<int, string> {
    if (a % 2 !== 0) {
        return err("First argument must be even");
    }
    if (b === 0) {
        return err("Cannot divide by zero");
    }
    return ok(a / b);
}

// Try-Catch
try {
    // code that might throw an error
} catch (error: string) {
    // handle error
}

// Clarity-specific Features
let hash: buffer = clarity.keccak256(stringValue);
let txSender: principal = clarity.txSender();

// Traits and Classes
trait TokenTrait {
    transfer(sender: principal, recipient: principal, amount: uint): boolean;
    getBalance(account: principal): uint;
}

@contract
class MyToken implements TokenTrait {
    @data
    balances: Map<principal, uint> = new Map<principal, uint>();

    transfer(sender: principal, recipient: principal, amount: uint): boolean {
        // Implementation
        return true;
    }

    getBalance(account: principal): uint {
        return this.balances.get(account) ?? 0u;
    }
}

// Assets
@asset
class NFT {
    id: uint;
    owner: principal;
}

// Type Assertions and Checks
let value: unknown = someFunction();
let numValue: int = value as int;

if (value is int) {
    let result: int = value + 1;
}

// Literals and Operations
let hexValue: int = 0xff;
let binaryValue: int = 0b1010;
let bigNumber: int = 1_000_000;

// Bitwise Operations
let a: int = 5;
let b: int = 3;
let bitwiseAnd: int = a & b;
let bitwiseOr: int = a | b;
let bitwiseXor: int = a ^ b;
let bitwiseNot: int = ~a;
let leftShift: int = a << 1;
let rightShift: int = a >> 1;

// Block Information
let currentHeight: uint = clarity.block.height;
let currentTime: uint = clarity.block.time;

// Optional and Response Handling
let optValue: optional<int> = some(5);
let value: int = optValue!;

let response: Response<int, string> = ok(10);
let result: int = response.unwrap();

let deepOptional: optional<{x: optional<int>}> = some({x: some(5)});
let deepValue: int = deepOptional?.x ?? 0;

// List Operations
let myList: list<int> = [1, 2, 3];
let longerList: list<int> = clarity.listAppend(myList, 4);
let listLength: uint = clarity.listLen(longerList);
let thirdElement: optional<int> = clarity.listElementAt(longerList, 2);

// Functional Operations
let doubled: list<int> = map(myList, (x: int): int => x * 2);
let evens: list<int> = filter(doubled, (x: int): boolean => x % 2 == 0);
let sum: int = fold(evens, 0, (acc: int, x: int): int => acc + x);

// Contract Calls with Block Limits
let result: boolean = TokenContract.transfer(sender, recipient, amount).limitHeight(10);
let otherResult: int = OtherContract.someFunction().limitTime(1000);

// Read-only Calls
let balance: uint = TokenContract.getBalance(account).readonly();

// Named Arguments
let transferResult: boolean = transfer({from: sender, to: recipient, amount: 100});

// Parsing
let parsedInt: int = clarity.toInt("123");
let parsedUint: uint = clarity.toUint("456");

// Function Composition
const double = (x: int): int => x * 2;
const addOne = (x: int): int => x + 1;
const doublePlusOne = compose(addOne, double);

// Memoization
@memo
function fibonacci(n: uint): uint {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Constant Time Comparison
let buffer1: buffer = buffer(10);
let buffer2: buffer = buffer(10);
let areEqual: boolean = clarity.constantTimeBufferEq(buffer1, buffer2);

// Asynchronous Mint
@async
function mint(recipient: principal, amount: uint): void {
    // Implementation
}

// Testing the grammar with various expressions and statements
let complexExpression: int = (a + b) * (c - d) / (e % f);
let ternaryResult: string = condition ? "true case" : "false case";
let nullCoalescing: int = someOptionalValue ?? defaultValue;

if (condition1 && condition2 || condition3) {
    // Complex condition
}

for (let i = 0; i < 10; i++) {
    // For loop (if supported in StxScript)
}

switch (value) {
    case 1:
        // Switch case (if supported in StxScript)
        break;
    default:
        // Default case
}

// End of test code

"""

parse_tree = stxscript_parser.parse(code)
print(parse_tree.pretty())