"""
StxScript Clarity Code Generator
Transforms AST nodes into Clarity smart contract code
"""

from typing import Union
from .ast_nodes import (
    # Base
    Node, SourceLocation,
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
    # Higher-order
    MapFunctionExpression, FilterExpression, FoldExpression,
    # Patterns
    WildcardPattern,
)


def to_kebab_case(name: str) -> str:
    """Convert camelCase to kebab-case"""
    import re
    # Don't convert if all uppercase (constant)
    if name.isupper():
        return name
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


class ClarityGenerator:
    """Generates Clarity code from StxScript AST nodes"""

    def __init__(self):
        self.indent_level = 0

    def indent(self) -> str:
        return "  " * self.indent_level

    def generate(self, node) -> str:
        """Main entry point - dispatches to specific generator methods"""
        if node is None:
            return ""

        # Handle primitive types
        if isinstance(node, str):
            return node
        if isinstance(node, int):
            return str(node)
        if isinstance(node, bool):
            return 'true' if node else 'false'

        # Get the specific generator method
        method_name = f'generate_{type(node).__name__}'
        method = getattr(self, method_name, None)

        if method is None:
            raise NotImplementedError(f"No generator for {type(node).__name__}")

        return method(node)

    # =========================================================================
    # PROGRAM
    # =========================================================================

    def generate_Program(self, node: Program) -> str:
        """Generate complete program"""
        parts = []
        for stmt in node.statements:
            result = self.generate(stmt)
            if result:
                parts.append(result)
        return '\n\n'.join(parts)

    # =========================================================================
    # TYPES
    # =========================================================================

    def generate_Type(self, node: Type) -> str:
        return node.name

    def generate_SimpleType(self, node: SimpleType) -> str:
        return node.name

    def generate_BufferType(self, node: BufferType) -> str:
        """Generate buffer type with size: (buff N)"""
        size = node.size if node.size else 32  # Default to 32 if not specified
        return f"(buff {size})"

    def generate_TypeParameter(self, node: TypeParameter) -> str:
        """Generate type parameter - use int as default (type erasure)"""
        # Clarity doesn't have generics, so we use a default type
        # The semantic analyzer has already validated type compatibility
        return "int"

    def generate_ListType(self, node: ListType) -> str:
        elem = self.generate(node.element_type) if node.element_type else "int"
        return f"(list {elem})"

    def generate_OptionalType(self, node: OptionalType) -> str:
        inner = self.generate(node.value_type) if node.value_type else "int"
        return f"(optional {inner})"

    def generate_ResponseType(self, node: ResponseType) -> str:
        ok = self.generate(node.ok_type) if node.ok_type else "bool"
        err = self.generate(node.err_type) if node.err_type else "uint"
        return f"(response {ok} {err})"

    def generate_MapType(self, node: MapType) -> str:
        key = self.generate(node.key_type) if node.key_type else "principal"
        val = self.generate(node.value_type) if node.value_type else "uint"
        return f"{{ {key}: {val} }}"

    # =========================================================================
    # DECLARATIONS
    # =========================================================================

    def generate_FunctionDeclaration(self, node: FunctionDeclaration) -> str:
        """Generate function declaration"""
        # Determine visibility
        is_public = 'public' in node.decorators
        is_readonly = 'readable' in node.decorators

        if is_readonly:
            func_type = 'read-only'
        elif is_public:
            func_type = 'public'
        else:
            func_type = 'private'

        # Generate parameters
        params = ' '.join(
            f"({to_kebab_case(p.name)} {self.generate(p.param_type)})"
            for p in node.parameters
        )

        # Generate body
        body = self.generate(node.body) if node.body else ""

        name = to_kebab_case(node.name)

        if params:
            return f"(define-{func_type} ({name} {params})\n{body})"
        else:
            return f"(define-{func_type} ({name})\n{body})"

    def generate_VariableDeclaration(self, node: VariableDeclaration) -> str:
        """Generate variable declaration"""
        name = to_kebab_case(node.name)
        var_type = self.generate(node.var_type) if node.var_type else "int"
        value = self.generate(node.value) if node.value else "0"
        return f"(define-data-var {name} {var_type} {value})"

    def generate_ConstantDeclaration(self, node: ConstantDeclaration) -> str:
        """Generate constant declaration"""
        value = self.generate(node.value) if node.value else "0"

        # Check if value is a lambda - convert to private function
        if isinstance(node.value, LambdaExpression):
            params = ' '.join(
                f"({to_kebab_case(p.name)} {self.generate(p.param_type)})"
                for p in node.value.parameters
            )
            body = self.generate(node.value.body) if node.value.body else ""
            name = to_kebab_case(node.name)
            # Single line for simple functions
            return f"(define-private ({name} {params}) {body})"

        return f"(define-constant {node.name} {value})"

    def generate_MapDeclaration(self, node: MapDeclaration) -> str:
        """Generate map declaration"""
        name = to_kebab_case(node.name)
        key_type = self.generate(node.key_type) if node.key_type else "principal"
        value_type = self.generate(node.value_type) if node.value_type else "uint"
        return f"(define-map {name} {key_type} {value_type})"

    def generate_ClassDeclaration(self, node: ClassDeclaration) -> str:
        """Generate class declaration"""
        parts = []
        impl_trait = None

        # Handle @asset decorator - NFT
        if 'asset' in node.decorators:
            parts.append(f"(define-non-fungible-token {node.name} uint)")

            # Generate owner map
            parts.append(f"(define-map {node.name.lower()}-owners uint principal)")

            # Generate field declarations
            for member in node.members:
                if isinstance(member, FieldDeclaration):
                    # Additional maps for fields
                    pass

        # Handle @contract decorator
        elif 'contract' in node.decorators:
            # Save impl-trait for end
            if node.implements:
                impl_trait = f"(impl-trait .{node.implements})"

            # Generate members
            for member in node.members:
                result = self.generate(member)
                if result:
                    parts.append(result)

            # Add impl-trait at the end
            if impl_trait:
                parts.append(impl_trait)

        return '\n\n'.join(parts)

    def generate_FieldDeclaration(self, node: FieldDeclaration) -> str:
        """Generate field declaration"""
        if 'data' in node.decorators:
            # This is a map declaration
            name = to_kebab_case(node.name)
            if isinstance(node.field_type, MapType):
                key_type = self.generate(node.field_type.key_type)
                value_type = self.generate(node.field_type.value_type)
                return f"(define-map {name} {key_type} {value_type})"
        return ""

    def generate_TraitDeclaration(self, node: TraitDeclaration) -> str:
        """Generate trait declaration"""
        methods = []
        for method in node.methods:
            params = ' '.join(
                self.generate(p.param_type)
                for p in method.parameters
            )
            ret = self.generate(method.return_type) if method.return_type else "bool"
            name = to_kebab_case(method.name)
            methods.append(f"  ({name} ({params}) {ret})")

        methods_str = '\n'.join(methods)
        return f"(define-trait {node.name}\n  (\n{methods_str}\n  ))"

    def generate_TraitMethod(self, node: TraitMethod) -> str:
        """Generate trait method (used within trait declaration)"""
        params = ' '.join(self.generate(p.param_type) for p in node.parameters)
        ret = self.generate(node.return_type) if node.return_type else "bool"
        name = to_kebab_case(node.name)
        return f"({name} ({params}) {ret})"

    def generate_ImportDeclaration(self, node: ImportDeclaration) -> str:
        """Generate import declaration"""
        imports = ', '.join(node.imports)
        return f";; import {{ {imports} }} from \"{node.module}\""

    def generate_ExportDeclaration(self, node: ExportDeclaration) -> str:
        """Generate export declaration"""
        return self.generate(node.declaration)

    def generate_TypeAliasDeclaration(self, node: TypeAliasDeclaration) -> str:
        """Generate type alias declaration as a comment"""
        target = self.generate(node.target_type) if node.target_type else "unknown"
        return f";; type {node.name} = {target}"

    def generate_TupleType(self, node: TupleType) -> str:
        """Generate tuple type"""
        fields = ' '.join(f"({k} {self.generate(v)})" for k, v in node.fields.items())
        return f"{{ {fields} }}"

    # =========================================================================
    # STATEMENTS
    # =========================================================================

    def generate_Block(self, node: Block) -> str:
        """Generate block of statements"""
        if not node.statements:
            return "  (ok true)"

        self.indent_level += 1

        if len(node.statements) == 1:
            result = f"{self.indent()}{self.generate(node.statements[0])}"
        else:
            stmts = [f"{self.indent()}{self.generate(s)}" for s in node.statements]
            result = f"{self.indent()}(begin\n" + '\n'.join(stmts) + f"\n{self.indent()})"

        self.indent_level -= 1
        return result

    def generate_ReturnStatement(self, node: ReturnStatement) -> str:
        """Generate return statement"""
        if node.expression:
            return self.generate(node.expression)
        return "()"

    def generate_IfStatement(self, node: IfStatement) -> str:
        """Generate if statement"""
        cond = self.generate(node.condition)
        then_block = self.generate(node.then_block) if node.then_block else "(ok true)"

        if node.else_block:
            else_block = self.generate(node.else_block)
            return f"(if {cond}\n{then_block}\n{else_block})"
        else:
            return f"(if {cond}\n{then_block}\n  (ok true))"

    def generate_ForStatement(self, node: ForStatement) -> str:
        """Generate for statement as a fold over a range list.

        Transforms: for (let i = 0; i < 10; i = i + 1) { body }
        Into: (fold loop-fn (list u0 u1 ... u9) initial-state)
        """
        var_name = to_kebab_case(node.init_var) if node.init_var else "i"

        # Try to extract loop bounds from condition
        start_val = 0
        end_val = 10  # Default

        # Parse init value
        if node.init_value:
            if isinstance(node.init_value, IntegerLiteral):
                start_val = node.init_value.value
            elif isinstance(node.init_value, UIntegerLiteral):
                start_val = node.init_value.value

        # Try to extract end value from condition (e.g., i < 10)
        if node.condition and isinstance(node.condition, BinaryExpression):
            if node.condition.operator in ('<', '<='):
                right = node.condition.right
                if isinstance(right, IntegerLiteral):
                    end_val = right.value
                    if node.condition.operator == '<=':
                        end_val += 1
                elif isinstance(right, UIntegerLiteral):
                    end_val = right.value
                    if node.condition.operator == '<=':
                        end_val += 1

        # Generate the range list
        range_list = ' '.join(f"u{i}" for i in range(start_val, end_val))

        # Generate body
        body = self.generate(node.body) if node.body else "(ok true)"

        # Generate as fold with inline lambda-style comment
        return f""";; for loop: {var_name} from {start_val} to {end_val}
(fold
  (lambda (acc {var_name})
{body}
    acc)
  (list {range_list})
  0)"""

    def generate_WhileStatement(self, node: WhileStatement) -> str:
        """Generate while statement as a bounded fold.

        Transforms: while (condition) { body }
        Into: A fold over a range with conditional execution
        """
        cond = self.generate(node.condition) if node.condition else "true"
        body = self.generate(node.body) if node.body else "(ok true)"
        max_iter = node.max_iterations

        # Generate a range list for bounded iterations
        range_list = ' '.join(f"u{i}" for i in range(max_iter))

        return f""";; while loop (bounded to {max_iter} iterations)
(fold
  (lambda (acc iter)
    (if {cond}
{body}
      acc))
  (list {range_list})
  0)"""

    def generate_ExpressionStatement(self, node: ExpressionStatement) -> str:
        """Generate expression statement"""
        return self.generate(node.expression)

    def generate_AssignmentStatement(self, node: AssignmentStatement) -> str:
        """Generate assignment statement"""
        target = self.generate(node.target)
        value = self.generate(node.value)
        return f"(var-set {target} {value})"

    def generate_MapInsert(self, node: MapInsert) -> str:
        name = to_kebab_case(node.map_name)
        key = self.generate(node.key)
        value = self.generate(node.value)
        return f"(map-set {name} {key} {value})"

    def generate_MapUpdate(self, node: MapUpdate) -> str:
        name = to_kebab_case(node.map_name)
        key = self.generate(node.key)
        value = self.generate(node.value)
        return f"(map-set {name} {key} {value})"

    def generate_MapDelete(self, node: MapDelete) -> str:
        name = to_kebab_case(node.map_name)
        key = self.generate(node.key)
        return f"(map-delete {name} {key})"

    # =========================================================================
    # EXPRESSIONS - Literals
    # =========================================================================

    def generate_Identifier(self, node: Identifier) -> str:
        return to_kebab_case(node.name)

    def generate_IntegerLiteral(self, node: IntegerLiteral) -> str:
        return str(node.value)

    def generate_UIntegerLiteral(self, node: UIntegerLiteral) -> str:
        return f"u{node.value}"

    def generate_StringLiteral(self, node: StringLiteral) -> str:
        return f'"{node.value}"'

    def generate_BooleanLiteral(self, node: BooleanLiteral) -> str:
        return 'true' if node.value else 'false'

    def generate_PrincipalLiteral(self, node: PrincipalLiteral) -> str:
        return node.value

    def generate_ListLiteral(self, node: ListLiteral) -> str:
        elements = ' '.join(self.generate(e) for e in node.elements)
        return f"(list {elements})"

    def generate_TupleLiteral(self, node: TupleLiteral) -> str:
        fields = ' '.join(f"({k} {self.generate(v)})" for k, v in node.fields.items())
        return f"(tuple {fields})"

    def generate_Literal(self, node: Literal) -> str:
        if isinstance(node.value, str):
            return f'"{node.value}"'
        elif isinstance(node.value, bool):
            return 'true' if node.value else 'false'
        return str(node.value)

    # =========================================================================
    # EXPRESSIONS - Operations
    # =========================================================================

    # Operator mappings
    BINARY_OPS = {
        '+': '+', '-': '-', '*': '*', '/': '/', '%': 'mod',
        '==': 'is-eq', '!=': 'not', '<': '<', '>': '>', '<=': '<=', '>=': '>=',
        '&&': 'and', '||': 'or',
        '&': 'bit-and', '|': 'bit-or', '^': 'bit-xor',
        '<<': 'bit-shift-left', '>>': 'bit-shift-right',
    }

    UNARY_OPS = {
        '!': 'not',
        '-': '-',
        '~': 'bit-not',
    }

    def generate_BinaryExpression(self, node: BinaryExpression) -> str:
        left = self.generate(node.left)
        right = self.generate(node.right)
        op = self.BINARY_OPS.get(node.operator, node.operator)

        # Special handling for !=
        if node.operator == '!=':
            return f"(not (is-eq {left} {right}))"

        # Special handling for shift operators - right operand must be unsigned
        if node.operator in ('<<', '>>'):
            # Convert integer to unsigned if it's a plain integer
            if isinstance(node.right, IntegerLiteral):
                right = f"u{node.right.value}"

        return f"({op} {left} {right})"

    def generate_UnaryExpression(self, node: UnaryExpression) -> str:
        operand = self.generate(node.operand)
        op = self.UNARY_OPS.get(node.operator, node.operator)
        return f"({op} {operand})"

    def generate_NullishCoalescing(self, node: NullishCoalescing) -> str:
        expr = self.generate(node.expression)
        default = self.generate(node.default)
        return f"(default-to {default} {expr})"

    def generate_ForceUnwrap(self, node: ForceUnwrap) -> str:
        expr = self.generate(node.expression)
        return f'(unwrap! {expr} (err "Unwrap failed"))'

    def generate_IndexExpression(self, node: IndexExpression) -> str:
        obj = self.generate(node.object)
        idx = self.generate(node.index)
        return f"(element-at {obj} {idx})"

    def generate_MemberExpression(self, node: MemberExpression) -> str:
        obj = self.generate(node.object)
        prop = to_kebab_case(node.property)
        return f"(get {prop} {obj})"

    def generate_MethodCallExpression(self, node: MethodCallExpression) -> str:
        obj = self.generate(node.object)
        method = to_kebab_case(node.method)
        args = ' '.join(self.generate(a) for a in node.arguments)

        # Handle special methods
        if method == 'get':
            return f"(map-get? {obj} {args})"

        return f"({method} {obj} {args})"

    # =========================================================================
    # EXPRESSIONS - Calls
    # =========================================================================

    def generate_CallExpression(self, node: CallExpression) -> str:
        callee = node.callee if isinstance(node.callee, str) else self.generate(node.callee)
        callee = to_kebab_case(callee)
        args = ' '.join(self.generate(a) for a in node.arguments)

        if args:
            return f"({callee} {args})"
        return f"({callee})"

    def generate_ContractCallExpression(self, node: ContractCallExpression) -> str:
        method = to_kebab_case(node.method)
        args = ' '.join(self.generate(a) for a in node.arguments)

        if args:
            return f"(contract-call? .{node.contract} {method} {args})"
        return f"(contract-call? .{node.contract} {method})"

    def generate_NewExpression(self, node: NewExpression) -> str:
        # new Map<K, V>() -> just return empty comment
        return f";; new {node.type_name}"

    # =========================================================================
    # EXPRESSIONS - Special
    # =========================================================================

    def generate_ThisExpression(self, node: ThisExpression) -> str:
        return "tx-sender"

    def generate_SomeExpression(self, node: SomeExpression) -> str:
        value = self.generate(node.value)
        return f"(some {value})"

    def generate_NoneExpression(self, node: NoneExpression) -> str:
        return "none"

    def generate_OkExpression(self, node: OkExpression) -> str:
        value = self.generate(node.value)
        return f"(ok {value})"

    def generate_ErrExpression(self, node: ErrExpression) -> str:
        value = self.generate(node.value)
        return f"(err {value})"

    def generate_UnwrapExpression(self, node: UnwrapExpression) -> str:
        expr = self.generate(node.expression)
        return f"(unwrap! {expr} (err u0))"

    def generate_TryExpression(self, node: TryExpression) -> str:
        expr = self.generate(node.expression)
        return f"(try! {expr})"

    def generate_GroupedExpression(self, node: GroupedExpression) -> str:
        return self.generate(node.expression)

    # =========================================================================
    # EXPRESSIONS - Lambda
    # =========================================================================

    def generate_LambdaExpression(self, node: LambdaExpression) -> str:
        # In Clarity, lambdas are typically inlined or converted to private functions
        # For simple cases, we can use the expression directly
        body = self.generate(node.body) if node.body else ""

        if len(node.parameters) == 1:
            # Single param lambda can often be simplified
            param = node.parameters[0].name
            return body.replace(param, "")

        params = ' '.join(to_kebab_case(p.name) for p in node.parameters)
        return f"(lambda ({params}) {body})"

    # =========================================================================
    # EXPRESSIONS - Match and Let
    # =========================================================================

    def generate_MatchExpression(self, node: MatchExpression) -> str:
        expr = self.generate(node.expression)
        # Convert match to nested if expressions
        # This is a simplification - real implementation would be more complex
        return f"(match {expr})"

    def generate_MatchArm(self, node: MatchArm) -> str:
        pattern = self.generate(node.pattern)
        expr = self.generate(node.expression)
        return f"({pattern} {expr})"

    def generate_LetExpression(self, node: LetExpression) -> str:
        bindings = ' '.join(
            f"({b.name} {self.generate(b.value)})"
            for b in node.bindings
        )
        body = self.generate(node.body) if node.body else ""
        return f"(let ({bindings}) {body})"

    def generate_LetBinding(self, node: LetBinding) -> str:
        value = self.generate(node.value)
        return f"({node.name} {value})"

    # =========================================================================
    # HIGHER-ORDER OPERATIONS
    # =========================================================================

    def generate_MapFunctionExpression(self, node: MapFunctionExpression) -> str:
        list_expr = self.generate(node.list_expr)
        func = self.generate(node.function)
        return f"(map {func} {list_expr})"

    def generate_FilterExpression(self, node: FilterExpression) -> str:
        list_expr = self.generate(node.list_expr)
        func = self.generate(node.function)
        return f"(filter {func} {list_expr})"

    def generate_FoldExpression(self, node: FoldExpression) -> str:
        list_expr = self.generate(node.list_expr)
        initial = self.generate(node.initial)
        func = self.generate(node.function)
        return f"(fold {func} {list_expr} {initial})"

    # =========================================================================
    # PATTERNS
    # =========================================================================

    def generate_WildcardPattern(self, node: WildcardPattern) -> str:
        return "_"

    def generate_Parameter(self, node: Parameter) -> str:
        name = to_kebab_case(node.name)
        type_str = self.generate(node.param_type) if node.param_type else "int"
        return f"({name} {type_str})"
