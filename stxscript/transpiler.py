import lark
from .semantic_analyzer import StxScriptSemanticAnalyzer

class StxScriptTranspiler:
    def __init__(self):
        with open('stxscript/grammar.lark', 'r') as grammar_file:
            self.parser = lark.Lark(grammar_file.read(), start='start', parser='lalr')
        self.semantic_analyzer = StxScriptSemanticAnalyzer()

    def transpile(self, stxscript):
        tree = self.parser.parse(stxscript)
        
        # Perform semantic analysis
        errors, warnings = self.semantic_analyzer.analyze(tree)
        
        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"  {warning}")
        
        if errors:
            raise ValueError("Semantic errors found:\n" + "\n".join(errors))
        
        transformer = StxScriptTransformer()
        clarity_code = transformer.transform(tree)
        return clarity_code

class StxScriptTransformer(lark.Transformer):
    def start(self, statements):
        return "\n".join(statement for statement in statements if statement)

    def variable_declaration(self, items):
        name, type_annotation, value = items
        if type_annotation:
            return f"(define-data-var {name} {self.transform_type(type_annotation)} {value})"
        else:
            return f"(define-data-var {name} {self.infer_type(value)} {value})"

    def constant_declaration(self, items):
        name, type_annotation, value = items
        return f"(define-constant {name} {value})"

    def function_declaration(self, items):
        decorators, name, params, return_type, body = items
        is_public = "@public" in decorators
        is_readable = "@readable" in decorators
        
        if is_public:
            define_keyword = "define-public"
        elif is_readable:
            define_keyword = "define-read-only"
        else:
            define_keyword = "define-private"
        
        params_str = " ".join(f"({param_name} {self.transform_type(param_type)})" for param_name, param_type in params)
        return f"({define_keyword} ({name} {params_str})\n  {body})"

    def lambda_function(self, items):
        params, return_type, body = items
        params_str = " ".join(f"({param_name} {self.transform_type(param_type)})" for param_name, param_type in params)
        return f"(lambda ({params_str}) {body})"

    def class_declaration(self, items):
        name, implements, members = items
        clarity_code = []
        
        for member in members:
            if isinstance(member, tuple) and member[0] == "@data":
                _, var_name, var_type, initial_value = member
                clarity_code.append(f"(define-data-var {var_name} {self.transform_type(var_type)} {initial_value})")
            elif isinstance(member, tuple) and member[0] == "@map":
                _, map_name, key_type, value_type = member
                clarity_code.append(f"(define-map {map_name} {self.transform_type(key_type)} {self.transform_type(value_type)})")
            else:
                clarity_code.append(member)
        
        if implements:
            clarity_code.append(f"(impl-trait .{implements})")
        
        return "\n".join(clarity_code)

    def trait_declaration(self, items):
        name, functions = items
        functions_str = "\n  ".join(functions)
        return f"(define-trait {name}\n  ({functions_str}))"

    def trait_function_signature(self, items):
        name, params, return_type = items
        params_str = " ".join(self.transform_type(param_type) for _, param_type in params)
        return f"({name} ({params_str}) {self.transform_type(return_type)})"

    def if_statement(self, items):
        condition, true_branch, false_branch = items
        if false_branch:
            return f"(if {condition}\n  {true_branch}\n  {false_branch})"
        else:
            return f"(if {condition}\n  {true_branch}\n  false)"

    def try_catch_statement(self, items):
        try_block, catch_var, catch_block = items
        return f"(try! {try_block}\n  (unwrap-panic {catch_var}\n    {catch_block}))"

    def throw_statement(self, items):
        return f"(err {items[0]})"

    def return_statement(self, items):
        return f"(ok {items[0]})" if items else "(ok true)"

    def expression_statement(self, items):
        return items[0]

    def assignment(self, items):
        target, op, value = items
        if op == '=':
            return f"(var-set {target} {value})"
        else:
            op_func = {
                '+=': '+', '-=': '-', '*=': '*', '/=': '/', '%=': 'mod',
                '&=': 'bit-and', '|=': 'bit-or', '^=': 'bit-xor',
                '<<=': 'bit-shift-left', '>>=': 'bit-shift-right'
            }[op]
            return f"(var-set {target} ({op_func} (var-get {target}) {value}))"

    def logical_or(self, items):
        return f"(or {items[0]} {items[1]})"

    def logical_and(self, items):
        return f"(and {items[0]} {items[1]})"

    def bitwise_or(self, items):
        return f"(bit-or {items[0]} {items[1]})"

    def bitwise_xor(self, items):
        return f"(bit-xor {items[0]} {items[1]})"

    def bitwise_and(self, items):
        return f"(bit-and {items[0]} {items[1]})"

    def equality(self, items):
        left, op, right = items
        if op == '==':
            return f"(is-eq {left} {right})"
        else:  # !=
            return f"(not (is-eq {left} {right}))"

    def comparison(self, items):
        left, op, right = items
        return f"({op} {left} {right})"

    def bitwise_shift(self, items):
        left, op, right = items
        if op == '<<':
            return f"(bit-shift-left {left} {right})"
        else:  # >>
            return f"(bit-shift-right {left} {right})"

    def arithmetic(self, items):
        left, op, right = items
        return f"({op} {left} {right})"

    def term(self, items):
        left, op, right = items
        if op == '%':
            return f"(mod {left} {right})"
        else:
            return f"({op} {left} {right})"

    def factor(self, items):
        op, expr = items
        if op == '!':
            return f"(not {expr})"
        elif op == '~':
            return f"(bit-not {expr})"
        else:
            return f"({op} {expr})"

    def power(self, items):
        base, exponent = items
        return f"(pow {base} {exponent})"

    def parenthesized(self, items):
        return items[0]

    def type_assertion(self, items):
        expr, type_name = items
        return f"(as-contract {expr})"  # Note: This might need more sophisticated handling

    def type_check(self, items):
        expr, type_name = items
        return f"(is-{type_name} {expr})"

    def function_call(self, items):
        func, *args = items
        return f"({func} {' '.join(args)})"

    def list_operation(self, items):
        op, *args = items
        if op == 'listAppend':
            return f"(append {args[0]} {args[1]})"
        elif op == 'listLen':
            return f"(len {args[0]})"
        elif op == 'listElementAt':
            return f"(element-at {args[0]} {args[1]})"

    def contract_call(self, items):
        contract, func, args, modifier = items
        call = f"(contract-call? .{contract} {func} {' '.join(args)})"
        if modifier:
            mod_func, mod_arg = modifier
            return f"({mod_func} {call} {mod_arg})"
        return call

    def tuple_literal(self, items):
        return f"(tuple {' '.join(f'({key} {value})' for key, value in items)})"

    def list_literal(self, items):
        return f"(list {' '.join(items)})"

    def optional_some(self, items):
        return f"(some {items[0]})"

    def optional_none(self, items):
        return "none"

    def response_ok(self, items):
        return f"(ok {items[0]})"

    def response_err(self, items):
        return f"(err {items[0]})"

    def transform_type(self, type_annotation):
        if isinstance(type_annotation, tuple):
            base_type, param_type = type_annotation
            if base_type == "list":
                return f"(list {self.transform_type(param_type)})"
            elif base_type == "optional":
                return f"(optional {self.transform_type(param_type)})"
            elif base_type == "Response":
                ok_type, err_type = param_type
                return f"(response {self.transform_type(ok_type)} {self.transform_type(err_type)})"
        return type_annotation

    def infer_type(self, value):
        if value.isdigit():
            return "uint"
        elif value[0] == "-" and value[1:].isdigit():
            return "int"
        elif value in ["true", "false"]:
            return "bool"
        elif value.startswith('"') and value.endswith('"'):
            return "string"
        elif value.startswith("'"):
            return "principal"
        else:
            return "unknown"

    # Additional methods for handling literals
    def INT(self, token):
        return token.value

    def UINT(self, token):
        return f"u{token.value[:-1]}"  # Remove the 'u' suffix and add it as a prefix

    def STRING(self, token):
        return token.value

    def BOOLEAN(self, token):
        return token.value

    def PRINCIPAL(self, token):
        return token.value

    def HEX(self, token):
        return f"0x{token.value[2:]}"  # Keep the '0x' prefix

    def BINARY(self, token):
        return f"0b{token.value[2:]}"  # Keep the '0b' prefix

    def IDENTIFIER(self, token):
        return token.value

    def block(self, items):
        return "\n".join(items)
    
    def assign(self, items):
        target, value = items
        return f"(var-set {target} {value})"

    def logical_or(self, items):
        left, right = items
        return f"(or {left} {right})"

    def logical_and(self, items):
        left, right = items
        return f"(and {left} {right})"

    def bitwise_or(self, items):
        left, right = items
        return f"(bit-or {left} {right})"
    
if __name__ == '__main__':
    transpiler = StxScriptTranspiler()
    stxscript_code = """
    @public
    function add(a: int, b: int): Response<int, string> {
        return ok(a + b);
    }
    """
    try:
        clarity_code = transpiler.transpile(stxscript_code)
        print(clarity_code)
    except ValueError as e:
        print(f"Error: {e}")