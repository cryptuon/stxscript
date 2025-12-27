"""
AST Visitor Pattern for StxScript

Provides a base visitor class for walking AST nodes with automatic dispatch
to visit_* methods based on node type.
"""

from typing import Any, Optional
from .ast_nodes import (
    Node, Program, Block,
    # Declarations
    FunctionDeclaration, VariableDeclaration, ConstantDeclaration,
    MapDeclaration, FieldDeclaration, ClassDeclaration, TraitDeclaration,
    ImportDeclaration, ExportDeclaration, Parameter, TraitMethod,
    # Statements
    AssignmentStatement, ReturnStatement, IfStatement, ExpressionStatement,
    MapInsert, MapUpdate, MapDelete,
    # Expressions
    Identifier, Literal, IntegerLiteral, UIntegerLiteral, StringLiteral,
    BooleanLiteral, PrincipalLiteral, ListLiteral, TupleLiteral,
    BinaryExpression, UnaryExpression, NullishCoalescing, ForceUnwrap,
    IndexExpression, MemberExpression, MethodCallExpression,
    CallExpression, ContractCallExpression, NewExpression,
    ThisExpression, SomeExpression, NoneExpression, OkExpression, ErrExpression,
    UnwrapExpression, TryExpression, GroupedExpression,
    LambdaExpression, MatchExpression, MatchArm, LetExpression, LetBinding,
    MapFunctionExpression, FilterExpression, FoldExpression, WildcardPattern,
    # Types
    Type, SimpleType, ListType, OptionalType, ResponseType, MapType, TupleType
)


class ASTVisitor:
    """
    Base visitor pattern for AST traversal.

    Subclasses should implement visit_* methods for each node type they care about.
    The default behavior is to recursively visit all child nodes.

    Example:
        class MyVisitor(ASTVisitor):
            def visit_FunctionDeclaration(self, node):
                print(f"Found function: {node.name}")
                # Visit children
                self.generic_visit(node)
    """

    def visit(self, node: Node) -> Any:
        """
        Dispatch to the appropriate visit_* method based on node type.

        Args:
            node: The AST node to visit

        Returns:
            The result of the visit_* method
        """
        if node is None:
            return None

        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: Node) -> None:
        """
        Default visitor that recursively visits all child nodes.

        Override this method to change default behavior.
        """
        if node is None:
            return

        # Visit children based on node type
        if isinstance(node, Program):
            for stmt in node.statements:
                self.visit(stmt)

        elif isinstance(node, Block):
            for stmt in node.statements:
                self.visit(stmt)

        elif isinstance(node, FunctionDeclaration):
            for param in node.parameters:
                self.visit(param)
            if node.return_type:
                self.visit(node.return_type)
            if node.body:
                self.visit(node.body)

        elif isinstance(node, VariableDeclaration):
            if node.var_type:
                self.visit(node.var_type)
            if node.value:
                self.visit(node.value)

        elif isinstance(node, ConstantDeclaration):
            if node.const_type:
                self.visit(node.const_type)
            if node.value:
                self.visit(node.value)

        elif isinstance(node, ClassDeclaration):
            for member in node.members:
                self.visit(member)

        elif isinstance(node, TraitDeclaration):
            for method in node.methods:
                self.visit(method)

        elif isinstance(node, TraitMethod):
            for param in node.parameters:
                self.visit(param)
            if node.return_type:
                self.visit(node.return_type)

        elif isinstance(node, FieldDeclaration):
            if node.field_type:
                self.visit(node.field_type)
            if node.value:
                self.visit(node.value)

        elif isinstance(node, Parameter):
            if node.param_type:
                self.visit(node.param_type)

        elif isinstance(node, MapDeclaration):
            if node.key_type:
                self.visit(node.key_type)
            if node.value_type:
                self.visit(node.value_type)

        elif isinstance(node, AssignmentStatement):
            if node.target:
                self.visit(node.target)
            if node.value:
                self.visit(node.value)

        elif isinstance(node, ReturnStatement):
            if node.expression:
                self.visit(node.expression)

        elif isinstance(node, IfStatement):
            if node.condition:
                self.visit(node.condition)
            if node.then_block:
                self.visit(node.then_block)
            if node.else_block:
                self.visit(node.else_block)

        elif isinstance(node, ExpressionStatement):
            if node.expression:
                self.visit(node.expression)

        elif isinstance(node, (MapInsert, MapUpdate)):
            if node.key:
                self.visit(node.key)
            if node.value:
                self.visit(node.value)

        elif isinstance(node, MapDelete):
            if node.key:
                self.visit(node.key)

        elif isinstance(node, BinaryExpression):
            if node.left:
                self.visit(node.left)
            if node.right:
                self.visit(node.right)

        elif isinstance(node, UnaryExpression):
            if node.operand:
                self.visit(node.operand)

        elif isinstance(node, NullishCoalescing):
            if node.expression:
                self.visit(node.expression)
            if node.default:
                self.visit(node.default)

        elif isinstance(node, ForceUnwrap):
            if node.expression:
                self.visit(node.expression)

        elif isinstance(node, IndexExpression):
            if node.object:
                self.visit(node.object)
            if node.index:
                self.visit(node.index)

        elif isinstance(node, MemberExpression):
            if node.object:
                self.visit(node.object)

        elif isinstance(node, MethodCallExpression):
            if node.object:
                self.visit(node.object)
            for arg in node.arguments:
                self.visit(arg)

        elif isinstance(node, CallExpression):
            if isinstance(node.callee, Node):
                self.visit(node.callee)
            for arg in node.arguments:
                self.visit(arg)

        elif isinstance(node, ContractCallExpression):
            for arg in node.arguments:
                self.visit(arg)

        elif isinstance(node, ListLiteral):
            for elem in node.elements:
                self.visit(elem)

        elif isinstance(node, TupleLiteral):
            for field_expr in node.fields.values():
                self.visit(field_expr)

        elif isinstance(node, (SomeExpression, OkExpression, ErrExpression)):
            if node.value:
                self.visit(node.value)

        elif isinstance(node, (UnwrapExpression, TryExpression, GroupedExpression)):
            if node.expression:
                self.visit(node.expression)

        elif isinstance(node, LambdaExpression):
            for param in node.parameters:
                self.visit(param)
            if node.return_type:
                self.visit(node.return_type)
            if node.body:
                self.visit(node.body)

        elif isinstance(node, MatchExpression):
            if node.expression:
                self.visit(node.expression)
            for arm in node.arms:
                self.visit(arm)

        elif isinstance(node, MatchArm):
            if node.pattern:
                self.visit(node.pattern)
            if node.expression:
                self.visit(node.expression)

        elif isinstance(node, LetExpression):
            for binding in node.bindings:
                self.visit(binding)
            if node.body:
                self.visit(node.body)

        elif isinstance(node, LetBinding):
            if node.value:
                self.visit(node.value)

        elif isinstance(node, (MapFunctionExpression, FilterExpression)):
            if node.list_expr:
                self.visit(node.list_expr)
            if node.function:
                self.visit(node.function)

        elif isinstance(node, FoldExpression):
            if node.list_expr:
                self.visit(node.list_expr)
            if node.initial:
                self.visit(node.initial)
            if node.function:
                self.visit(node.function)

        # Generic types
        elif isinstance(node, ListType):
            if node.element_type:
                self.visit(node.element_type)

        elif isinstance(node, OptionalType):
            if node.value_type:
                self.visit(node.value_type)

        elif isinstance(node, ResponseType):
            if node.ok_type:
                self.visit(node.ok_type)
            if node.err_type:
                self.visit(node.err_type)

        elif isinstance(node, MapType):
            if node.key_type:
                self.visit(node.key_type)
            if node.value_type:
                self.visit(node.value_type)

        elif isinstance(node, TupleType):
            for field_type in node.fields.values():
                self.visit(field_type)

    def visit_children(self, node: Node) -> None:
        """Explicitly visit all children of a node."""
        self.generic_visit(node)
