"""
StxScript AST Builder
Transforms Lark parse tree into StxScript AST nodes
"""

from lark import Transformer, Token, Tree
from typing import List, Optional, Any

from .ast_nodes import (
    # Base and location
    SourceLocation, Node,
    # Types
    Type, SimpleType, BufferType, ListType, OptionalType, ResponseType, MapType, TupleType, TypeParameter,
    # Program and declarations
    Program, Decorator, Parameter, Block,
    FunctionDeclaration, VariableDeclaration, ConstantDeclaration,
    MapDeclaration, FieldDeclaration, ClassDeclaration,
    TraitMethod, TraitDeclaration, ImportDeclaration, ExportDeclaration,
    TypeAliasDeclaration,
    # Statements
    AssignmentStatement, ReturnStatement, IfStatement, ForStatement, WhileStatement, ExpressionStatement,
    MapInsert, MapUpdate, MapDelete,
    # Expressions - Identifiers and Literals
    Identifier, Literal, IntegerLiteral, UIntegerLiteral, StringLiteral,
    BooleanLiteral, PrincipalLiteral, ListLiteral, TupleLiteral,
    # Expressions - Operations
    BinaryExpression, UnaryExpression, NullishCoalescing, ForceUnwrap,
    IndexExpression, MemberExpression, MethodCallExpression,
    # Expressions - Calls
    CallExpression, ContractCallExpression, NewExpression,
    # Expressions - Special
    ThisExpression, SomeExpression, NoneExpression, OkExpression, ErrExpression,
    UnwrapExpression, TryExpression, GroupedExpression,
    # Expressions - Lambda
    LambdaExpression,
    # Expressions - Match and Let
    MatchArm, MatchExpression, LetBinding, LetExpression,
    # Patterns
    WildcardPattern,
)


class ASTBuilder(Transformer):
    """
    Transforms Lark parse tree into StxScript AST nodes.
    Each method corresponds to a grammar rule and returns the appropriate AST node.
    """

    def _get_location(self, meta) -> Optional[SourceLocation]:
        """Extract source location from Lark meta"""
        if hasattr(meta, 'line'):
            return SourceLocation(
                line=meta.line,
                column=meta.column,
                end_line=getattr(meta, 'end_line', None),
                end_column=getattr(meta, 'end_column', None)
            )
        return None

    def _get_token_location(self, token) -> Optional[SourceLocation]:
        """Extract source location from a Token"""
        if isinstance(token, Token) and hasattr(token, 'line'):
            return SourceLocation(
                line=token.line,
                column=token.column,
                end_line=token.end_line if hasattr(token, 'end_line') else None,
                end_column=token.end_column if hasattr(token, 'end_column') else None
            )
        return None

    def _find_first_token(self, items) -> Optional[Token]:
        """Find the first Token in a list of items for location tracking"""
        for item in items:
            if isinstance(item, Token):
                return item
            if isinstance(item, Node) and item.location:
                return None  # Already has location from child
        return None

    def _token_value(self, token) -> str:
        """Extract value from a Token or return string as-is"""
        if isinstance(token, Token):
            return str(token)
        return str(token)

    # =========================================================================
    # ROOT
    # =========================================================================

    def start(self, items) -> Program:
        """Root rule - returns Program node"""
        statements = [item for item in items if item is not None]
        return Program(statements=statements)

    def top_level_item(self, items):
        """Top level item - pass through the single child"""
        return items[0] if items else None

    # =========================================================================
    # CLASS DECLARATIONS
    # =========================================================================

    def class_declaration(self, items) -> ClassDeclaration:
        """Parse class declaration"""
        decorators = []
        name = None
        implements = None
        members = []

        for item in items:
            if isinstance(item, str) and item.startswith('@'):
                decorators.append(item[1:])  # Remove @
            elif isinstance(item, Token):
                if item.type == 'IDENTIFIER':
                    if name is None:
                        name = str(item)
                    else:
                        implements = str(item)
            elif isinstance(item, list):
                members = item
            elif isinstance(item, (FunctionDeclaration, FieldDeclaration, MapDeclaration)):
                members.append(item)

        return ClassDeclaration(
            name=name or "Unknown",
            members=members,
            implements=implements,
            decorators=decorators
        )

    def class_member(self, items):
        """Class member - pass through"""
        return items[0] if items else None

    def field_declaration(self, items) -> FieldDeclaration:
        """Parse field declaration"""
        decorators = []
        name = None
        field_type = None
        value = None

        for item in items:
            if isinstance(item, str) and item.startswith('@'):
                decorators.append(item[1:])
            elif isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
            elif isinstance(item, Type):
                field_type = item
            elif isinstance(item, Node):
                value = item

        return FieldDeclaration(
            name=name or "unknown",
            field_type=field_type or SimpleType(name="unknown"),
            value=value,
            decorators=decorators
        )

    # =========================================================================
    # FUNCTION DECLARATIONS
    # =========================================================================

    def function_declaration(self, items) -> FunctionDeclaration:
        """Parse function declaration"""
        decorators = []
        name = None
        parameters = []
        return_type = None
        body = None
        type_params = []
        location = None

        for item in items:
            if isinstance(item, str) and item.startswith('@'):
                decorators.append(item[1:])
            elif isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
                if location is None:
                    location = self._get_token_location(item)
            elif isinstance(item, list):
                # Could be parameter list or type params
                if item and isinstance(item[0], Parameter):
                    parameters = item
                elif item and isinstance(item[0], str) and len(item[0]) == 1 and item[0].isupper():
                    # Type parameters like ["T", "U"]
                    type_params = item
            elif isinstance(item, Type):
                return_type = item
            elif isinstance(item, Block):
                body = item

        return FunctionDeclaration(
            name=name or "unknown",
            parameters=parameters,
            return_type=return_type,
            body=body,
            decorators=decorators,
            type_params=type_params,
            location=location
        )

    def generic_params(self, items) -> List[str]:
        """Parse generic type parameters: <T>, <T, U>"""
        type_params = []
        for item in items:
            if isinstance(item, Token) and item.type == 'TYPE_PARAM':
                type_params.append(str(item))
        return type_params

    def parameter_list(self, items) -> List[Parameter]:
        """Parse parameter list"""
        return [item for item in items if isinstance(item, Parameter)]

    def parameter(self, items) -> Parameter:
        """Parse single parameter"""
        name = None
        param_type = None

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
            elif isinstance(item, Type):
                param_type = item

        return Parameter(
            name=name or "unknown",
            param_type=param_type or SimpleType(name="unknown")
        )

    # =========================================================================
    # TRAIT DECLARATIONS
    # =========================================================================

    def trait_declaration(self, items) -> TraitDeclaration:
        """Parse trait declaration"""
        name = None
        methods = []

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
            elif isinstance(item, TraitMethod):
                methods.append(item)

        return TraitDeclaration(name=name or "Unknown", methods=methods)

    def trait_method(self, items) -> TraitMethod:
        """Parse trait method signature"""
        name = None
        parameters = []
        return_type = None

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
            elif isinstance(item, list) and item and isinstance(item[0], Parameter):
                parameters = item
            elif isinstance(item, Type):
                return_type = item

        return TraitMethod(
            name=name or "unknown",
            parameters=parameters,
            return_type=return_type
        )

    # =========================================================================
    # STATEMENTS
    # =========================================================================

    def statement(self, items):
        """Statement - pass through"""
        return items[0] if items else None

    def variable_declaration(self, items) -> VariableDeclaration:
        """Parse variable declaration"""
        name = None
        var_type = None
        value = None
        location = None

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
                if location is None:
                    location = self._get_token_location(item)
            elif isinstance(item, Type):
                var_type = item
            elif isinstance(item, Node):
                value = item

        return VariableDeclaration(
            name=name or "unknown",
            value=value,
            var_type=var_type,
            location=location
        )

    def constant_declaration(self, items) -> ConstantDeclaration:
        """Parse constant declaration"""
        name = None
        const_type = None
        value = None
        location = None

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
                if location is None:
                    location = self._get_token_location(item)
            elif isinstance(item, Type):
                const_type = item
            elif isinstance(item, Node):
                value = item

        return ConstantDeclaration(
            name=name or "unknown",
            value=value,
            const_type=const_type,
            location=location
        )

    def assignment_statement(self, items) -> AssignmentStatement:
        """Parse assignment statement"""
        target = items[0] if len(items) > 0 else Identifier(name="unknown")
        value = items[1] if len(items) > 1 else Identifier(name="unknown")

        # Convert Token to Identifier if needed
        if isinstance(target, Token):
            target = Identifier(name=str(target))

        return AssignmentStatement(target=target, value=value)

    def return_statement(self, items) -> ReturnStatement:
        """Parse return statement"""
        # Skip tokens (like RETURN keyword), find the expression
        expr = None
        for item in items:
            if isinstance(item, Node):
                expr = item
                break
        return ReturnStatement(expression=expr)

    def if_statement(self, items) -> IfStatement:
        """Parse if statement"""
        condition = None
        then_block = None
        else_block = None

        for item in items:
            if isinstance(item, Node) and not isinstance(item, Block) and not isinstance(item, IfStatement):
                if condition is None:
                    condition = item
            elif isinstance(item, Block):
                if then_block is None:
                    then_block = item
                else:
                    else_block = item
            elif isinstance(item, IfStatement):
                else_block = item

        return IfStatement(
            condition=condition or Identifier(name="true"),
            then_block=then_block or Block(),
            else_block=else_block
        )

    def for_statement(self, items) -> ForStatement:
        """Parse for statement: for (let i = 0; i < 10; i = i + 1) { body }"""
        init_info = None
        condition = None
        update_info = None
        body = None

        for item in items:
            if isinstance(item, dict) and 'for_init' in item:
                init_info = item
            elif isinstance(item, dict) and 'for_update' in item:
                update_info = item
            elif isinstance(item, Block):
                body = item
            elif isinstance(item, Node) and condition is None:
                condition = item

        return ForStatement(
            init_var=init_info.get('var', '') if init_info else '',
            init_type=init_info.get('type') if init_info else None,
            init_value=init_info.get('value') if init_info else None,
            condition=condition,
            update_var=update_info.get('var', '') if update_info else '',
            update_expr=update_info.get('expr') if update_info else None,
            body=body
        )

    def for_init(self, items) -> dict:
        """Parse for loop initialization: let i = 0 or let i: int = 0"""
        var_name = None
        var_type = None
        init_value = None

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                var_name = str(item)
            elif isinstance(item, Type):
                var_type = item
            elif isinstance(item, Node):
                init_value = item

        return {'for_init': True, 'var': var_name, 'type': var_type, 'value': init_value}

    def for_update(self, items) -> dict:
        """Parse for loop update: i = i + 1"""
        var_name = None
        expr = None

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                var_name = str(item)
            elif isinstance(item, Node):
                expr = item

        return {'for_update': True, 'var': var_name, 'expr': expr}

    def while_statement(self, items) -> WhileStatement:
        """Parse while statement: while (condition) { body }"""
        condition = None
        body = None

        for item in items:
            if isinstance(item, Block):
                body = item
            elif isinstance(item, Node):
                condition = item

        return WhileStatement(
            condition=condition,
            body=body,
            max_iterations=100  # Default bounded iteration limit
        )

    def expression_statement(self, items) -> ExpressionStatement:
        """Parse expression statement"""
        expr = items[0] if items else Identifier(name="unknown")
        return ExpressionStatement(expression=expr)

    def block(self, items) -> Block:
        """Parse block"""
        statements = [item for item in items if isinstance(item, Node)]
        return Block(statements=statements)

    # =========================================================================
    # MAP OPERATIONS
    # =========================================================================

    def map_declaration(self, items) -> MapDeclaration:
        """Parse map declaration"""
        name = None
        types = []

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
            elif isinstance(item, Type):
                types.append(item)

        return MapDeclaration(
            name=name or "unknown",
            key_type=types[0] if len(types) > 0 else SimpleType(name="unknown"),
            value_type=types[1] if len(types) > 1 else SimpleType(name="unknown")
        )

    def map_operation(self, items):
        """Map operation - pass through"""
        return items[0] if items else None

    def map_insert(self, items) -> MapInsert:
        """Parse map insert"""
        name = str(items[0]) if items and isinstance(items[0], Token) else "unknown"
        key = items[1] if len(items) > 1 else Identifier(name="key")
        value = items[2] if len(items) > 2 else Identifier(name="value")
        return MapInsert(map_name=name, key=key, value=value)

    def map_update(self, items) -> MapUpdate:
        """Parse map update"""
        name = str(items[0]) if items and isinstance(items[0], Token) else "unknown"
        key = items[1] if len(items) > 1 else Identifier(name="key")
        value = items[2] if len(items) > 2 else Identifier(name="value")
        return MapUpdate(map_name=name, key=key, value=value)

    def map_delete(self, items) -> MapDelete:
        """Parse map delete"""
        name = str(items[0]) if items and isinstance(items[0], Token) else "unknown"
        key = items[1] if len(items) > 1 else Identifier(name="key")
        return MapDelete(map_name=name, key=key)

    # =========================================================================
    # IMPORT/EXPORT
    # =========================================================================

    def import_statement(self, items) -> ImportDeclaration:
        """Parse import statement"""
        imports = []
        module = ""

        for item in items:
            if isinstance(item, list):
                imports = item
            elif isinstance(item, Token) and item.type == 'STRING':
                module = str(item)[1:-1]  # Remove quotes

        return ImportDeclaration(module=module, imports=imports)

    def import_list(self, items) -> List[str]:
        """Parse import list"""
        return [str(item) for item in items if isinstance(item, Token)]

    def export_statement(self, items) -> ExportDeclaration:
        """Parse export statement"""
        decl = items[0] if items else None
        return ExportDeclaration(declaration=decl)

    def type_alias_declaration(self, items) -> TypeAliasDeclaration:
        """Parse type alias: type Name = Type;"""
        name = None
        target_type = None

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
            elif isinstance(item, Type):
                target_type = item

        return TypeAliasDeclaration(
            name=name or "unknown",
            target_type=target_type,
            location=self._get_location(items)
        )

    # =========================================================================
    # TYPES
    # =========================================================================

    def type(self, items):
        """Type - pass through"""
        return items[0] if items else SimpleType(name="unknown")

    def simple_type(self, items):
        """Simple type - pass through to specific type"""
        return items[0] if items else SimpleType(name="unknown")

    def int_type(self, items) -> SimpleType:
        return SimpleType(name="int")

    def uint_type(self, items) -> SimpleType:
        return SimpleType(name="uint")

    def bool_type(self, items) -> SimpleType:
        return SimpleType(name="bool")

    def string_type(self, items) -> SimpleType:
        return SimpleType(name="string")

    def buffer_type(self, items) -> BufferType:
        return BufferType(name="buffer", size=None)

    def sized_buffer_type(self, items) -> BufferType:
        """Parse buffer<N> with size"""
        size = None
        for item in items:
            if isinstance(item, Token) and item.type == 'INTEGER':
                size = int(str(item))
                break
        return BufferType(size=size)

    def principal_type(self, items) -> SimpleType:
        return SimpleType(name="principal")

    def response_type(self, items) -> ResponseType:
        """Parse Response<Ok, Err>"""
        # Filter to only Type instances (skip tokens like RESPONSE)
        types = [item for item in items if isinstance(item, Type)]
        ok_type = types[0] if len(types) > 0 else SimpleType(name="unknown")
        err_type = types[1] if len(types) > 1 else SimpleType(name="unknown")
        return ResponseType(name="", ok_type=ok_type, err_type=err_type)

    def optional_type(self, items) -> OptionalType:
        """Parse optional<T>"""
        # Skip tokens, find the Type
        value_type = None
        for item in items:
            if isinstance(item, Type):
                value_type = item
                break
        return OptionalType(name="", value_type=value_type or SimpleType(name="unknown"))

    def list_type(self, items) -> ListType:
        """Parse list<T>"""
        # Skip tokens (like LIST keyword), find the Type
        element_type = None
        for item in items:
            if isinstance(item, Type):
                element_type = item
                break
        return ListType(name="", element_type=element_type or SimpleType(name="unknown"))

    def map_type(self, items) -> MapType:
        """Parse Map<K, V>"""
        # Filter to only Type instances (skip tokens like MAP_TYPE)
        types = [item for item in items if isinstance(item, Type)]
        key_type = types[0] if len(types) > 0 else SimpleType(name="unknown")
        value_type = types[1] if len(types) > 1 else SimpleType(name="unknown")
        return MapType(name="", key_type=key_type, value_type=value_type)

    def custom_type(self, items) -> Type:
        """Parse custom type reference (type alias or type parameter)"""
        name = None
        for item in items:
            if isinstance(item, Token):
                name = str(item)
                break
        if name and len(name) == 1 and name.isupper():
            # Single uppercase letter is a type parameter (T, K, V, etc.)
            return TypeParameter(name=name)
        return SimpleType(name=name or "unknown")

    def tuple_type(self, items) -> TupleType:
        """Parse tuple type: { field: Type, ... }"""
        fields = {}
        for item in items:
            if isinstance(item, tuple) and len(item) == 2:
                field_name, field_type = item
                fields[field_name] = field_type
        return TupleType(fields=fields)

    def tuple_type_field(self, items):
        """Parse tuple type field: name: Type"""
        name = None
        field_type = None
        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
            elif isinstance(item, Type):
                field_type = item
        return (name, field_type)

    # =========================================================================
    # EXPRESSIONS - Binary and Unary
    # =========================================================================

    def expression(self, items):
        """Expression - pass through the single child"""
        return items[0] if items else None

    def nullish_coalescing(self, items) -> Node:
        """Parse nullish coalescing: a ?? b"""
        if len(items) == 1:
            return items[0]

        # Build left-associative chain
        result = items[0]
        for i in range(1, len(items)):
            if isinstance(items[i], Token) and str(items[i]) == '??':
                continue
            result = NullishCoalescing(expression=result, default=items[i])
        return result

    def _build_binary_chain(self, items, op_type: str = None) -> Node:
        """Build left-associative binary expression chain"""
        if len(items) == 1:
            return items[0]

        result = items[0]
        i = 1
        while i < len(items):
            if isinstance(items[i], Token):
                op = str(items[i])
                i += 1
                if i < len(items):
                    result = BinaryExpression(left=result, operator=op, right=items[i])
            else:
                # Implicit operator from caller
                if op_type:
                    result = BinaryExpression(left=result, operator=op_type, right=items[i])
            i += 1
        return result

    # Binary expression handlers - each calls _build_binary_chain
    def logical_or(self, items):
        return self._build_binary_chain(items)

    def logical_and(self, items):
        return self._build_binary_chain(items)

    def bitwise_or(self, items):
        return self._build_binary_chain(items)

    def bitwise_xor(self, items):
        return self._build_binary_chain(items)

    def bitwise_and(self, items):
        return self._build_binary_chain(items)

    def equality(self, items):
        return self._build_binary_chain(items)

    def comparison(self, items):
        return self._build_binary_chain(items)

    def shift(self, items):
        return self._build_binary_chain(items)

    def addition(self, items):
        return self._build_binary_chain(items)

    def multiplication(self, items):
        return self._build_binary_chain(items)

    def power(self, items):
        if len(items) == 1:
            return items[0]
        return BinaryExpression(left=items[0], operator="**", right=items[1])

    # Unary expressions - items[0] is the operator token, items[-1] is the operand
    def unary_not(self, items) -> UnaryExpression:
        return UnaryExpression(operator="!", operand=items[-1])

    def unary_neg(self, items) -> UnaryExpression:
        return UnaryExpression(operator="-", operand=items[-1])

    def unary_pos(self, items) -> UnaryExpression:
        return UnaryExpression(operator="+", operand=items[-1])

    def unary_bitnot(self, items) -> UnaryExpression:
        return UnaryExpression(operator="~", operand=items[-1])

    # =========================================================================
    # EXPRESSIONS - Postfix
    # =========================================================================

    def postfix(self, items) -> Node:
        """Handle postfix operations"""
        if len(items) == 1:
            return items[0]

        result = items[0]
        for op in items[1:]:
            if isinstance(op, dict):
                op_type = op.get('type')
                if op_type == 'force_unwrap':
                    result = ForceUnwrap(expression=result)
                elif op_type == 'method_call':
                    result = MethodCallExpression(
                        object=result,
                        method=op.get('method', 'unknown'),
                        arguments=op.get('arguments', [])
                    )
                elif op_type == 'member_access':
                    result = MemberExpression(
                        object=result,
                        property=op.get('property', 'unknown')
                    )
                elif op_type == 'index':
                    result = IndexExpression(object=result, index=op.get('index'))
        return result

    def postfix_op(self, items):
        """Pass through postfix op"""
        return items[0] if items else None

    def force_unwrap(self, items) -> dict:
        """Force unwrap marker"""
        return {'type': 'force_unwrap'}

    def method_call(self, items) -> dict:
        """Method call marker"""
        method = None
        args = []

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                method = str(item)
            elif isinstance(item, list):
                args = item

        return {'type': 'method_call', 'method': method or 'unknown', 'arguments': args}

    def member_access(self, items) -> dict:
        """Member access marker"""
        prop = None
        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                prop = str(item)
        return {'type': 'member_access', 'property': prop or 'unknown'}

    def index_op(self, items) -> dict:
        """Index operation marker"""
        index = items[0] if items else Identifier(name="0")
        return {'type': 'index', 'index': index}

    # =========================================================================
    # EXPRESSIONS - Primary
    # =========================================================================

    def identifier(self, items) -> Identifier:
        """Parse identifier"""
        token = items[0] if items else None
        name = str(token) if token else "unknown"
        location = self._get_token_location(token) if token else None
        return Identifier(name=name, location=location)

    def this_expr(self, items) -> ThisExpression:
        """Parse this expression"""
        return ThisExpression()

    def grouped_expr(self, items) -> Node:
        """Parse grouped expression - just return inner"""
        return items[0] if items else Identifier(name="unknown")

    def principal_literal(self, items) -> PrincipalLiteral:
        """Parse principal literal"""
        value = str(items[0]) if items else "'SP"
        return PrincipalLiteral(value=value)

    # =========================================================================
    # EXPRESSIONS - Calls
    # =========================================================================

    def call_expr(self, items):
        """Pass through call expression"""
        return items[0] if items else None

    def function_call(self, items) -> CallExpression:
        """Parse function call"""
        name = None
        args = []

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
            elif isinstance(item, list):
                args = item

        return CallExpression(callee=name or "unknown", arguments=args)

    def contract_call(self, items) -> ContractCallExpression:
        """Parse contract call"""
        contract = None
        method = None
        args = []

        identifiers = []
        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                identifiers.append(str(item))
            elif isinstance(item, list):
                args = item

        if len(identifiers) >= 2:
            contract = identifiers[0]
            method = identifiers[1]
        elif len(identifiers) == 1:
            contract = identifiers[0]
            method = "call"

        return ContractCallExpression(
            contract=contract or "Unknown",
            method=method or "unknown",
            arguments=args
        )

    def argument_list(self, items) -> List[Node]:
        """Parse argument list"""
        return [item for item in items if isinstance(item, Node)]

    def new_expression(self, items) -> NewExpression:
        """Parse new expression"""
        type_name = None
        type_params = []

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                type_name = str(item)
            elif isinstance(item, Type):
                type_params.append(item)

        return NewExpression(type_name=type_name or "Unknown", type_params=type_params)

    # =========================================================================
    # EXPRESSIONS - Special
    # =========================================================================

    def some_expression(self, items) -> SomeExpression:
        """Parse some(value)"""
        # Skip tokens, find the expression
        value = None
        for item in items:
            if isinstance(item, Node):
                value = item
                break
        return SomeExpression(value=value or Identifier(name="unknown"))

    def none_expression(self, items) -> NoneExpression:
        """Parse none()"""
        return NoneExpression()

    def ok_expression(self, items) -> OkExpression:
        """Parse ok(value)"""
        # Skip tokens (like OK keyword), find the expression
        value = None
        for item in items:
            if isinstance(item, Node):
                value = item
                break
        return OkExpression(value=value or Identifier(name="unknown"))

    def err_expression(self, items) -> ErrExpression:
        """Parse err(value)"""
        # Skip tokens (like ERR keyword), find the expression
        value = None
        for item in items:
            if isinstance(item, Node):
                value = item
                break
        return ErrExpression(value=value or Identifier(name="unknown"))

    def unwrap_expression(self, items) -> UnwrapExpression:
        """Parse unwrap!(expr)"""
        # Skip tokens (like UNWRAP keyword), find the expression
        expr = None
        for item in items:
            if isinstance(item, Node):
                expr = item
                break
        return UnwrapExpression(expression=expr or Identifier(name="unknown"))

    def try_expression(self, items) -> TryExpression:
        """Parse try!(expr)"""
        # Skip tokens (like TRY keyword), find the expression
        expr = None
        for item in items:
            if isinstance(item, Node):
                expr = item
                break
        return TryExpression(expression=expr or Identifier(name="unknown"))

    # =========================================================================
    # EXPRESSIONS - Lambda
    # =========================================================================

    def lambda_expression(self, items):
        """Pass through lambda"""
        return items[0] if items else None

    def typed_lambda(self, items) -> LambdaExpression:
        """Parse typed lambda: (x: int): int => expr"""
        params = []
        return_type = None
        body = None

        for item in items:
            if isinstance(item, list) and item and isinstance(item[0], Parameter):
                params = item
            elif isinstance(item, Type):
                return_type = item
            elif isinstance(item, Node):
                body = item

        return LambdaExpression(parameters=params, body=body, return_type=return_type)

    def empty_lambda(self, items) -> LambdaExpression:
        """Parse empty lambda: () => expr"""
        body = items[0] if items else Identifier(name="unknown")
        return LambdaExpression(parameters=[], body=body, return_type=None)

    def untyped_lambda(self, items) -> LambdaExpression:
        """Parse untyped lambda: (x, y) => expr"""
        param_names = []
        body = None

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                param_names.append(str(item))
            elif isinstance(item, Node):
                body = item

        # Create parameters without types
        params = [Parameter(name=name, param_type=SimpleType(name="unknown")) for name in param_names]

        return LambdaExpression(parameters=params, body=body, return_type=None)

    def typed_params(self, items) -> List[Parameter]:
        """Parse typed parameter list"""
        return [item for item in items if isinstance(item, Parameter)]

    def typed_param(self, items) -> Parameter:
        """Parse typed parameter"""
        name = None
        param_type = None

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
            elif isinstance(item, Type):
                param_type = item

        return Parameter(
            name=name or "unknown",
            param_type=param_type or SimpleType(name="unknown")
        )

    def lambda_body(self, items):
        """Lambda body - pass through"""
        return items[0] if items else Identifier(name="unknown")

    # =========================================================================
    # EXPRESSIONS - Match and Let
    # =========================================================================

    def match_expression(self, items) -> MatchExpression:
        """Parse match expression"""
        expr = None
        arms = []

        for item in items:
            if isinstance(item, MatchArm):
                arms.append(item)
            elif isinstance(item, Node) and expr is None:
                expr = item

        return MatchExpression(expression=expr or Identifier(name="unknown"), arms=arms)

    def match_arm(self, items) -> MatchArm:
        """Parse match arm"""
        pattern = items[0] if items else Identifier(name="_")
        expr = items[1] if len(items) > 1 else Identifier(name="unknown")
        return MatchArm(pattern=pattern, expression=expr)

    def pattern(self, items) -> Node:
        """Parse pattern"""
        if not items:
            return WildcardPattern()

        item = items[0]
        if isinstance(item, Token):
            if str(item) == '_':
                return WildcardPattern()
            return Identifier(name=str(item))
        return item

    def let_expression(self, items) -> LetExpression:
        """Parse let expression"""
        bindings = []
        body = None

        for item in items:
            if isinstance(item, LetBinding):
                bindings.append(item)
            elif isinstance(item, Node):
                body = item

        return LetExpression(bindings=bindings, body=body)

    def let_binding(self, items) -> LetBinding:
        """Parse let binding"""
        name = None
        value = None

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
            elif isinstance(item, Node):
                value = item

        return LetBinding(name=name or "unknown", value=value or Identifier(name="unknown"))

    # =========================================================================
    # EXPRESSIONS - Literals
    # =========================================================================

    def list_literal(self, items) -> ListLiteral:
        """Parse list literal"""
        elements = [item for item in items if isinstance(item, Node)]
        return ListLiteral(elements=elements)

    def tuple_literal(self, items) -> TupleLiteral:
        """Parse tuple literal"""
        fields = {}
        for item in items:
            if isinstance(item, tuple) and len(item) == 2:
                name, value = item
                fields[name] = value
        return TupleLiteral(fields=fields)

    def tuple_field(self, items) -> tuple:
        """Parse tuple field"""
        name = None
        value = None

        for item in items:
            if isinstance(item, Token) and item.type == 'IDENTIFIER':
                name = str(item)
            elif isinstance(item, Node):
                value = item

        return (name or "unknown", value or Identifier(name="unknown"))

    def literal(self, items):
        """Pass through literal"""
        return items[0] if items else None

    def integer_literal(self, items) -> IntegerLiteral:
        """Parse integer literal"""
        value = int(str(items[0])) if items else 0
        return IntegerLiteral(value=value)

    def uinteger_literal(self, items) -> UIntegerLiteral:
        """Parse unsigned integer literal"""
        value_str = str(items[0]) if items else "0u"
        value = int(value_str.rstrip('u'))
        return UIntegerLiteral(value=value)

    def string_literal(self, items) -> StringLiteral:
        """Parse string literal"""
        value = str(items[0])[1:-1] if items else ""  # Remove quotes
        return StringLiteral(value=value)

    def boolean_literal(self, items) -> BooleanLiteral:
        """Parse boolean literal"""
        value = str(items[0]).lower() == 'true' if items else False
        return BooleanLiteral(value=value)

    # =========================================================================
    # DECORATORS
    # =========================================================================

    def decorator(self, items) -> str:
        """Parse decorator - return as string with @"""
        name = str(items[0]) if items else "unknown"
        return f"@{name}"
