from lark import Lark, Transformer, v_args, Token
from .ast_nodes import *
from .clarity_generator import ClarityGenerator

@v_args(inline=True)
class StxScriptTransformer(Transformer):
    def program(self, *statements):
        return Program(list(statements))

    def statement(self, stmt):
        # Transformation logic for 'statement' rule (adjust based on actual grammar and structure)
        if isinstance(stmt, FunctionDeclaration):
            return stmt
        elif isinstance(stmt, ReturnStatement):
            return stmt
        elif isinstance(stmt, VariableDeclaration):
            return stmt
        elif isinstance(stmt, ConstantDeclaration):
            return stmt
        elif isinstance(stmt, IfStatement):
            return stmt
        elif isinstance(stmt, TryCatchStatement):
            return stmt
        elif isinstance(stmt, ThrowStatement):
            return stmt
        elif isinstance(stmt, ExpressionStatement):
            return stmt
        elif isinstance(stmt, MapDeclaration):
            return stmt
        elif isinstance(stmt, AssetDeclaration):
            return stmt
        elif isinstance(stmt, TraitDeclaration):
            return stmt
        elif isinstance(stmt, ImportDeclaration):
            return stmt
        elif isinstance(stmt, ExportDeclaration):
            return stmt
        else:
            # Log the unhandled statement for debugging
            print(f"Unhandled statement type: {type(stmt)}")
            return stmt  # Return as-is for now, adjust as needed

    @v_args(inline=True)
    def function_declaration(self, *items):
        print(f"Debug: function_declaration called with items={items}")
        decorators = [d for d in items if isinstance(d, Identifier) and d.name.startswith('@')]
        name = next((i for i in items if isinstance(i, Identifier) and not i.name.startswith('@')), None)
        
        if name is None:
            raise ValueError("Function name not found in declaration")
        
        params = next((i for i in items if isinstance(i, list)), [])
        return_type = next((i for i in items if isinstance(i, Type)), None)
        body = next((i for i in items if isinstance(i, Block)), None)
        
        is_export = 'export' in [item.value for item in items if isinstance(item, Token)]
        
        func = FunctionDeclaration(decorators, name, params, return_type, body)
        return ExportDeclaration(func) if is_export else func

    def variable_declaration(self, name, type_=None, value=None):
        return VariableDeclaration(name, type_, value)

    def constant_declaration(self, name, type_=None, value=None):
        return ConstantDeclaration(name, type_, value)

    def map_declaration(self, *args):
        # Assuming the order is: key_type, value_type, name, _, _, _
        key_type, value_type, name = args[:3]
        return MapDeclaration(name, key_type, value_type)

    def asset_declaration(self, name, *fields):
        field_nodes = []
        for i in range(0, len(fields), 2):
            if i + 1 < len(fields):
                field_name = fields[i]
                field_type = fields[i + 1]
                if isinstance(field_name, Identifier) and isinstance(field_type, Type):
                    field_nodes.append(Parameter(name=field_name.name, type=field_type))
                else:
                    raise SyntaxError(f"Unexpected field format: {field_name} {field_type}")
            else:
                raise SyntaxError(f"Incomplete field definition for {fields[i]}")
        return AssetDeclaration(name=name, fields=field_nodes)

    def asset_call_expression(self, asset, function, *args):
        return AssetCallExpression(asset, function, list(args))

    def field(self, name, field_type):
        return [name, field_type]  # Return as a list of name and type for asset_declaration to unpack

    def trait_declaration(self, name, *functions):
        return TraitDeclaration(name, list(functions))

    def function_signature(self, name, params, return_type):
        return FunctionDeclaration([], name, params, return_type, None)

    def expression_statement(self, expr):
        return ExpressionStatement(expr)
    @v_args(inline=True)
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
        print(f"Debug: import_declaration called with items={items}")
        imports = [item.name if isinstance(item, Identifier) else item for item in items if item != 'from']
        module = items[-1].value if isinstance(items[-1], Token) else items[-1]
        return ImportDeclaration(module, imports)

    def export_declaration(self, func):
        print(f"Debug: export_declaration called with func={func}")
        return ExportDeclaration(func)

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

    @v_args(tree=True)
    def call_expression(self, tree):
        print(f"Debug: call_expression called with tree={tree}")
        print(f"Debug: tree.children = {tree.children}")
        
        if not tree.children:
            print(f"call_expression requires at least a callee. Tree: {tree}")
            return CallExpression(callee=None, arguments=[])
        
        callee = tree.children[0]
        args = tree.children[1] if len(tree.children) > 1 else []
        
        print(f"Debug: callee = {callee}, args = {args}")
        
        if isinstance(callee, AssetCallExpression):
            callee.arguments = args
            return callee
        return CallExpression(callee=callee, arguments=args)
            
    @v_args(inline=True)
    def member_expression(self, obj, prop=None):
        print(f"Debug: member_expression called with obj={obj}, prop={prop}")
        if prop is None:
            return obj
        if isinstance(obj, Identifier) and obj.name == 'NFT':
            return AssetCallExpression(asset='NFT', function=prop.name, arguments=[])
        return MemberExpression(object=obj, property=prop)

    def is_expression(self, type_):
        return TypeCheck(None, type_)

    def as_expression(self, type_):
        return TypeAssertion(None, type_)

    def is_ok_expression(self, expr):
        print(f"Debug: is_ok_expression called with expr={expr}")
        return CallExpression(callee=MemberExpression(expr, Identifier('isOk')), arguments=[])
    
    def ok_expression(self, value):
        print(f"Debug: ok_expression called with value={value}")
        return CallExpression(callee=Identifier('ok'), arguments=[value])

    def err_expression(self, value):
        print(f"Debug: err_expression called with value={value}")
        return CallExpression(callee=Identifier('err'), arguments=[value])

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
    
    def type_identifier(self, token):
        # Assuming `token` is a Lark token with a `value` attribute representing the type name
        return Type(token.value)

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

    def IDENTIFIER(self, token):
        # Assuming `token` is a Lark token with a `value` attribute representing the identifier's name
        return Identifier(token.value)

    def NUMBER(self, value):
        return int(value) if value.isdigit() else float(value)

    def STRING(self, value):
        return value[1:-1]  # Remove quotes

    def BOOLEAN(self, value):
        return value == "true"

    def PRINCIPAL(self, value):
        return value
    
    def lambda_expression(self, parameters, body):
        return LambdaExpression(parameters, body)
    
    def primary_expression(self, value):
        # Example transformation logic for primary expression (adjust based on actual grammar)
        if isinstance(value, list):
            return value[0]  # If value is a list, return the first element (e.g., Identifier, Literal, etc.)
        return value
    
    def generate_MemberExpression(self, node: MemberExpression):
        obj = self.generate(node.object)
        return f'(get {node.property} {obj})'
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
            print("AST:", ast)  # Add this line
            clarity_code = self.generator.generate(ast)
            print("Clarity Code:", clarity_code)
            return clarity_code
        except Exception as e:
            raise SyntaxError(f"Transpilation failed: {str(e)}")