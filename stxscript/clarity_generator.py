from .ast_nodes import *

class ClarityGenerator:
    def __init__(self):
        self.indent_level = 0

    def indent(self):
        return "  " * self.indent_level

    def generate(self, node):
        if node is None:
            return ""
        elif isinstance(node, str):
            return self.generate_str(node)
        elif isinstance(node, int):
            return str(node)
        elif isinstance(node, float):
            return str(node)
        elif isinstance(node, bool):
            return 'true' if node else 'false'
        elif isinstance(node, list):
            return self.generate_list(node)
        elif isinstance(node, tuple):
            return self.generate_tuple(node)
        elif isinstance(node, dict):
            return self.generate_dict(node)
        elif isinstance(node, Identifier):
            return self.generate_Identifier(node)
        elif isinstance(node, Type):
            return self.generate_Type(node)
        
        method = getattr(self, f'generate_{node.__class__.__name__}', None)
        if method is None:
            raise NotImplementedError(f"Generation not implemented for {node.__class__.__name__}")
        return method(node)

    def generate_str(self, node: str):
        return f'"{node}"'

    def generate_list(self, node: list):
        return f'(list {" ".join(self.generate(item) for item in node)})'

    def generate_tuple(self, node: tuple):
        return f'(tuple {" ".join(self.generate(item) for item in node)})'

    def generate_dict(self, node: dict):
        return f'(tuple {" ".join(f"({self.generate(k)} {self.generate(v)})" for k, v in node.items())})'

    def generate_Identifier(self, node: Identifier):
        return node.name

    def generate_Type(self, node: Type):
        return node.name

    def generate_Program(self, node: Program):
        return '\n'.join(self.generate(stmt) for stmt in node.statements)

    def generate_FunctionDeclaration(self, node: FunctionDeclaration):
        is_public = any(d.name == '@public' for d in node.decorators)
        func_type = 'public' if is_public else 'private'
        params = ' '.join(self.generate(param) for param in node.parameters)
        body = self.generate(node.body)
        return f'(define-{func_type} ({node.name} {params})\n{self.indent()}{body})'

    def generate_VariableDeclaration(self, node: VariableDeclaration):
        type_str = self.generate(node.type) if node.type else ''
        value = self.generate(node.value)
        return f'(define-data-var {node.name} {type_str} {value})'

    def generate_ConstantDeclaration(self, node: ConstantDeclaration):
        value = self.generate(node.value)
        return f'(define-constant {node.name} {value})'

    def generate_MapDeclaration(self, node: MapDeclaration):
        key_type = self.generate(node.key_type)
        value_type = self.generate(node.value_type)
        return f'(define-map {node.name} {key_type} {value_type})'

    def generate_AssetDeclaration(self, node: AssetDeclaration):
        fields = ' '.join(f'({field.name} {self.generate(field.type)})' for field in node.fields)
        return f'(define-non-fungible-token {node.name} {fields})'

    def generate_TraitDeclaration(self, node: TraitDeclaration):
        functions = '\n'.join(f'({self.generate(func)})' for func in node.functions)
        return f'(define-trait {node.name}\n{self.indent()}({functions}))'

    def generate_Parameter(self, node: Parameter):
        return f'({node.name} {self.generate(node.type)})'

    def generate_Block(self, node: Block):
        self.indent_level += 1
        body = '\n'.join(f'{self.indent()}{self.generate(stmt)}' for stmt in node.statements)
        self.indent_level -= 1
        return body

    def generate_IfStatement(self, node: IfStatement):
        condition = self.generate(node.condition)
        true_block = self.generate(node.true_block)
        else_block = self.generate(node.else_block) if node.else_block else ''
        return f'(if {condition}\n{self.indent()}{true_block}\n{self.indent()}{else_block})'

    def generate_TryCatchStatement(self, node: TryCatchStatement):
        try_block = self.generate(node.try_block)
        catch_block = self.generate(node.catch_block)
        return f'(try\n{self.indent()}{try_block}\n{self.indent()}(catch {node.error_var} {catch_block}))'

    def generate_ThrowStatement(self, node: ThrowStatement):
        expr = self.generate(node.expression)
        return f'(error {expr})'

    def generate_ReturnStatement(self, node: ReturnStatement):
        if node.expression:
            expr = self.generate(node.expression)
            return expr
        return '()'

    def generate_ExpressionStatement(self, node: ExpressionStatement):
        return self.generate(node.expression)

    def generate_BinaryExpression(self, node: BinaryExpression):
        left = self.generate(node.left)
        right = self.generate(node.right)
        return f'({node.operator} {left} {right})'

    def generate_UnaryExpression(self, node: UnaryExpression):
        expr = self.generate(node.expression)
        return f'({node.operator} {expr})'

    def generate_TernaryExpression(self, node: TernaryExpression):
        condition = self.generate(node.condition)
        true_expr = self.generate(node.true_expr)
        false_expr = self.generate(node.false_expr)
        return f'(if {condition} {true_expr} {false_expr})'

    def generate_CallExpression(self, node: CallExpression):
        callee = self.generate(node.callee)
        args = ' '.join(self.generate(arg) for arg in node.arguments)
        return f'({callee} {args})'

    def generate_MemberExpression(self, node: MemberExpression):
        obj = self.generate(node.object)
        return f'(get {node.property} {obj})'

    def generate_Literal(self, node: Literal):
        if isinstance(node.value, str):
            return f'"{node.value}"'
        return str(node.value)

    def generate_ListLiteral(self, node: ListLiteral):
        elements = ' '.join(self.generate(elem) for elem in node.elements)
        return f'(list {elements})'

    def generate_TupleLiteral(self, node: TupleLiteral):
        elements = ' '.join(f'({k} {self.generate(v)})' for k, v in node.elements.items())
        return f'(tuple {elements})'

    def generate_OptionalLiteral(self, node: OptionalLiteral):
        if node.value:
            return f'(some {self.generate(node.value)})'
        return 'none'

    def generate_PrincipalLiteral(self, node: PrincipalLiteral):
        return f"'{node.value}'"

    def generate_ListType(self, node: ListType):
        return f'(list {self.generate(node.element_type)})'

    def generate_TupleType(self, node: TupleType):
        fields = ' '.join(f'({k} {self.generate(v)})' for k, v in node.fields.items())
        return f'(tuple {fields})'

    def generate_OptionalType(self, node: OptionalType):
        return f'(optional {self.generate(node.value_type)})'

    def generate_ResponseType(self, node: ResponseType):
        ok_type = self.generate(node.ok_type)
        err_type = self.generate(node.err_type)
        return f'(response {ok_type} {err_type})'

    def generate_ContractCallExpression(self, node: ContractCallExpression):
        contract = self.generate(node.contract)
        args = ' '.join(self.generate(arg) for arg in node.arguments)
        return f'(contract-call? .{contract} {node.function} {args})'

    def generate_AssetCallExpression(self, node: AssetCallExpression):
        args = ' '.join(self.generate(arg) for arg in node.arguments)
        return f'(nft-{node.function}? {node.asset} {args})'

    def generate_MapExpression(self, node: MapExpression):
        list_expr = self.generate(node.list)
        function = self.generate(node.function)
        return f'(map {function} {list_expr})'

    def generate_FilterExpression(self, node: FilterExpression):
        list_expr = self.generate(node.list)
        function = self.generate(node.function)
        return f'(filter {function} {list_expr})'

    def generate_FoldExpression(self, node: FoldExpression):
        list_expr = self.generate(node.list)
        initial = self.generate(node.initial)
        function = self.generate(node.function)
        return f'(fold {list_expr} {initial} {function})'

    def generate_ListComprehension(self, node: ListComprehension):
        expression = self.generate(node.expression)
        iterable = self.generate(node.iterable)
        iterator = self.generate(node.iterator)
        condition = self.generate(node.condition) if node.condition else None
        if condition:
            return f'(map {expression} (filter (lambda ({iterator}) {condition}) {iterable}))'
        return f'(map (lambda ({iterator}) {expression}) {iterable})'

    def generate_ImportDeclaration(self, node: ImportDeclaration):
        return f'(use-trait {" ".join(node.imports)} .{node.module})'

    def generate_ExportDeclaration(self, node: ExportDeclaration):
        return self.generate(node.declaration)

    def generate_TypeAssertion(self, node: TypeAssertion):
        expr = self.generate(node.expression)
        asserted_type = self.generate(node.asserted_type)
        return f'(as {asserted_type} {expr})'

    def generate_TypeCheck(self, node: TypeCheck):
        expr = self.generate(node.expression)
        checked_type = self.generate(node.checked_type)
        return f'(is-{checked_type} {expr})'

    def generate_LambdaExpression(self, node: LambdaExpression):
        params = ' '.join(self.generate(param) for param in node.parameters)
        body = self.generate(node.body)
        return f'(lambda ({params}) {body})'