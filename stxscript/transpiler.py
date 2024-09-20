from lark import Lark, Transformer, v_args
from .ast_nodes import *
from .clarity_generator import ClarityGenerator

@v_args(inline=True)
class StxScriptTransformer(Transformer):
    def program(self, *statements):
        return Program(list(statements))

    def function_declaration(self, *items):
        print("Function Declaration Items:", items)
        print("Types of items:", [type(item) for item in items])
        
        decorators = [d for d in items if isinstance(d, Identifier) and d.name.startswith('@')]
        name = next((i for i in items if isinstance(i, Identifier) and not i.name.startswith('@')), None)
        
        print("Decorators:", decorators)
        print("Name:", name)
        
        if name is None:
            raise ValueError("Function name not found in declaration")
        
        params = next((i for i in items if isinstance(i, list)), [])
        return_type = next((i for i in items if isinstance(i, Type)), None)
        body = next((i for i in items if isinstance(i, Block)), None)
        
        print("Params:", params)
        print("Return Type:", return_type)
        print("Body:", body)
        
        return FunctionDeclaration(decorators, name, params, return_type, body)

    def variable_declaration(self, name, type_=None, value=None):
        return VariableDeclaration(name, type_, value)

    def constant_declaration(self, name, type_=None, value=None):
        return ConstantDeclaration(name, type_, value)

    def map_declaration(self, *args):
        # Assuming the order is: key_type, value_type, name, _, _, _
        key_type, value_type, name = args[:3]
        return MapDeclaration(name, key_type, value_type)

    def asset_declaration(self, name, *fields):
        return AssetDeclaration(name, list(fields))

    def trait_declaration(self, name, *functions):
        return TraitDeclaration(name, list(functions))

    def function_signature(self, name, params, return_type):
        return FunctionDeclaration([], name, params, return_type, None)

    def expression_statement(self, expr):
        return ExpressionStatement(expr)

    def if_statement(self, condition, true_block, *else_ifs_and_else):
        else_ifs = []
        else_block = None
        for i in range(0, len(else_ifs_and_else), 2):
            if i + 1 < len(else_ifs_and_else):
                else_ifs.append(ElseIf(else_ifs_and_else[i], else_ifs_and_else[i+1]))
            else:
                else_block = else_ifs_and_else[i]
        return IfStatement(condition, true_block, else_ifs, else_block)

    def try_catch_statement(self, try_block, error_var, catch_block):
        return TryCatchStatement(try_block, error_var, catch_block)

    def throw_statement(self, expr):
        return ThrowStatement(expr)

    def return_statement(self, expr=None):
        return ReturnStatement(expr)

    def import_declaration(self, *items):
        imports = [item for item in items if isinstance(item, str) and item != 'from']
        module = items[-1]
        return ImportDeclaration(module, imports)

    def export_declaration(self, declaration):
        return ExportDeclaration(declaration)

    def expression(self, expr):
        return expr

    def assignment_expression(self, left, right=None):
        return BinaryExpression(left, "=", right) if right else left

    def conditional_expression(self, condition, true_expr=None, false_expr=None):
        return TernaryExpression(condition, true_expr, false_expr) if true_expr and false_expr else condition

    @v_args(tree=True)
    def binary_expression(self, tree):
        if len(tree.children) == 1:
            return tree.children[0]
        left = tree.children[0]
        for i in range(1, len(tree.children) - 1, 2):
            op = tree.children[i]
            right = tree.children[i + 1]
            left = BinaryExpression(left, op, right)
        return left

    logical_or_expression = binary_expression
    logical_and_expression = binary_expression
    bitwise_or_expression = binary_expression
    bitwise_xor_expression = binary_expression
    bitwise_and_expression = binary_expression
    equality_expression = binary_expression
    relational_expression = binary_expression
    shift_expression = binary_expression
    additive_expression = binary_expression
    multiplicative_expression = binary_expression

    def unary_expression(self, *args):
        if len(args) == 1:
            return args[0]
        return UnaryExpression(args[0], args[1])

    def postfix_expression(self, expr, *postfix):
        for p in postfix:
            if isinstance(p, CallExpression):
                expr = CallExpression(expr, p.arguments)
            elif isinstance(p, MemberExpression):
                expr = MemberExpression(expr, p.property)
            elif isinstance(p, TypeCheck):
                expr = TypeCheck(expr, p.checked_type)
            elif isinstance(p, TypeAssertion):
                expr = TypeAssertion(expr, p.asserted_type)
        return expr

    def call_expression(self, *args):
        return CallExpression(None, list(args))

    def member_expression(self, property):
        return MemberExpression(None, property)

    def is_expression(self, type_):
        return TypeCheck(None, type_)

    def as_expression(self, type_):
        return TypeAssertion(None, type_)

    def array_or_list_literal(self, *items):
        return ListLiteral(list(items))

    def object_or_tuple_literal(self, *items):
        return TupleLiteral(dict(zip(items[::2], items[1::2])))

    def object_or_tuple_item(self, key, value):
        return key, value

    def arguments(self, *args):
        return list(args)

    def parameters(self, *params):
        return list(params)

    def parameter(self, name, type_):
        return Parameter(name, type_)

    def block(self, *statements):
        return Block(list(statements))

    def type(self, name):
        return Type(name)

    def list_type(self, elem_type):
        return ListType(elem_type)

    def tuple_type(self, *items):
        return TupleType({str(k): v for k, v in items})

    def tuple_type_item(self, name, type_):
        return (name, type_)

    def optional_type(self, type_):
        return OptionalType(type_)

    def response_type(self, ok_type, err_type):
        return ResponseType(ok_type, err_type)

    def list_comprehension(self, expr, iterator, iterable, condition=None):
        return ListComprehension(expr, iterable, iterator, condition)

    def literal(self, value):
        return Literal(value)

    def IDENTIFIER(self, value):
        return Identifier(value)

    def NUMBER(self, value):
        return int(value) if value.isdigit() else float(value)

    def STRING(self, value):
        return value[1:-1]  # Remove quotes

    def BOOLEAN(self, value):
        return value == "true"

    def PRINCIPAL(self, value):
        return value

class StxScriptTranspiler:
    def __init__(self):
        with open('stxscript/grammar.lark', 'r') as grammar_file:
            self.parser = Lark(grammar_file.read(), start='program', parser='lalr')
        self.transformer = StxScriptTransformer()
        self.generator = ClarityGenerator()

    def transpile(self, input_code):
        try:
            parse_tree = self.parser.parse(input_code)
            ast = self.transformer.transform(parse_tree)
            clarity_code = self.generator.generate(ast)
            return clarity_code
        except Exception as e:
            raise SyntaxError(f"Transpilation failed: {str(e)}")