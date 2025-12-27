"""
StxScript Semantic Analyzer

Performs semantic analysis on AST nodes including:
- Symbol resolution and scope management
- Type checking and inference
- Validation of language constraints

Phase A: Core checks (undefined symbols, type mismatch, duplicates)
Phase B: Enhanced checks (unused variables, unreachable code, shadowing)
Phase C: Advanced checks (trait compliance, overflow warnings)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from .ast_visitor import ASTVisitor
from .ast_nodes import (
    Node, Program, Block, SourceLocation,
    # Declarations
    FunctionDeclaration, VariableDeclaration, ConstantDeclaration,
    MapDeclaration, FieldDeclaration, ClassDeclaration, TraitDeclaration,
    ImportDeclaration, ExportDeclaration, Parameter, TraitMethod,
    TypeAliasDeclaration,
    # Statements
    AssignmentStatement, ReturnStatement, IfStatement, ForStatement, WhileStatement, ExpressionStatement,
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
    # Types
    Type, SimpleType, BufferType, ListType, OptionalType, ResponseType, MapType, TupleType, TypeParameter
)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class SemanticIssue:
    """Represents a semantic error or warning with location information."""
    message: str
    location: Optional[SourceLocation] = None
    severity: str = "error"  # "error", "warning", "info"
    suggestion: Optional[str] = None

    def __str__(self):
        loc = f" at {self.location}" if self.location else ""
        sug = f" (suggestion: {self.suggestion})" if self.suggestion else ""
        return f"[{self.severity.upper()}]{loc}: {self.message}{sug}"


@dataclass
class SymbolInfo:
    """Information about a symbol in the symbol table."""
    name: str
    kind: str  # "function", "variable", "constant", "parameter", "type", "trait", "map"
    data_type: Optional[Type]
    location: Optional[SourceLocation] = None
    is_mutable: bool = True
    used: bool = False
    # For functions
    parameters: List['SymbolInfo'] = field(default_factory=list)
    return_type: Optional[Type] = None
    decorators: List[str] = field(default_factory=list)


class SymbolTable:
    """
    Scoped symbol table for tracking declarations.

    Maintains a stack of scopes where each scope is a dictionary
    mapping symbol names to SymbolInfo objects.
    """

    def __init__(self):
        self.scopes: List[Dict[str, SymbolInfo]] = [{}]  # Start with global scope
        self.scope_names: List[str] = ["global"]

    def enter_scope(self, name: str = "block"):
        """Enter a new scope."""
        self.scopes.append({})
        self.scope_names.append(name)

    def exit_scope(self) -> Dict[str, SymbolInfo]:
        """Exit current scope and return its symbols."""
        if len(self.scopes) > 1:
            self.scope_names.pop()
            return self.scopes.pop()
        return {}

    def current_scope_name(self) -> str:
        """Get the name of the current scope."""
        return ".".join(self.scope_names)

    def define(self, name: str, info: SymbolInfo) -> Optional[SymbolInfo]:
        """
        Define a symbol in the current scope.

        Returns the existing symbol if already defined in current scope.
        """
        current = self.scopes[-1]
        if name in current:
            return current[name]  # Already defined
        current[name] = info
        return None

    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """
        Look up a symbol in all scopes (innermost first).

        Returns None if not found.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_local(self, name: str) -> Optional[SymbolInfo]:
        """Look up a symbol only in the current scope."""
        return self.scopes[-1].get(name)

    def lookup_in_outer(self, name: str) -> Optional[SymbolInfo]:
        """Look up a symbol in outer scopes (not current)."""
        for scope in reversed(self.scopes[:-1]):
            if name in scope:
                return scope[name]
        return None

    def mark_used(self, name: str):
        """Mark a symbol as used."""
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name].used = True
                return

    def get_unused_symbols(self) -> List[SymbolInfo]:
        """Get all unused symbols in the current scope."""
        return [
            info for info in self.scopes[-1].values()
            if not info.used and info.kind in ("variable", "parameter", "constant")
        ]

    def depth(self) -> int:
        """Get the current scope depth."""
        return len(self.scopes)


# =============================================================================
# SEMANTIC ANALYZER
# =============================================================================

class ASTSemanticAnalyzer(ASTVisitor):
    """
    Semantic analyzer that walks AST nodes and performs validation.

    Checks include:
    - Phase A: Undefined symbols, type mismatch, duplicates, argument count
    - Phase B: Unused variables, unreachable code, shadowing, missing returns
    - Phase C: Trait compliance, overflow warnings
    """

    # Built-in types
    BUILTIN_TYPES = {"int", "uint", "bool", "boolean", "string", "buffer", "principal"}

    # Arithmetic operators
    ARITHMETIC_OPS = {"+", "-", "*", "/", "%", "**"}

    # Comparison operators
    COMPARISON_OPS = {"==", "!=", "<", ">", "<=", ">="}

    # Logical operators
    LOGICAL_OPS = {"&&", "||", "!"}

    # Bitwise operators
    BITWISE_OPS = {"&", "|", "^", "~", "<<", ">>"}

    def __init__(self):
        self.symbols = SymbolTable()
        self.errors: List[SemanticIssue] = []
        self.warnings: List[SemanticIssue] = []

        # Context tracking
        self.current_function: Optional[FunctionDeclaration] = None
        self.current_class: Optional[ClassDeclaration] = None
        self.has_returned: bool = False  # Track if current block has returned
        self.defined_traits: Dict[str, TraitDeclaration] = {}
        self.defined_maps: Dict[str, MapDeclaration] = {}

    def analyze(self, program: Program) -> Tuple[List[SemanticIssue], List[SemanticIssue]]:
        """
        Analyze a program and return errors and warnings.

        Args:
            program: The Program AST node to analyze

        Returns:
            Tuple of (errors, warnings)
        """
        self.visit(program)
        return self.errors, self.warnings

    def error(self, message: str, node: Optional[Node] = None, suggestion: str = None):
        """Record an error."""
        location = node.location if node else None
        self.errors.append(SemanticIssue(message, location, "error", suggestion))

    def warning(self, message: str, node: Optional[Node] = None, suggestion: str = None):
        """Record a warning."""
        location = node.location if node else None
        self.warnings.append(SemanticIssue(message, location, "warning", suggestion))

    # =========================================================================
    # TYPE UTILITIES
    # =========================================================================

    def get_type_name(self, t: Optional[Type]) -> str:
        """Get a string representation of a type."""
        if t is None:
            return "unknown"
        if isinstance(t, SimpleType):
            return t.name
        if isinstance(t, TypeParameter):
            return t.name  # Just return T, K, V, etc.
        if isinstance(t, BufferType):
            if t.size:
                return f"buffer<{t.size}>"
            return "buffer"
        if isinstance(t, ListType):
            elem = self.get_type_name(t.element_type)
            return f"list<{elem}>"
        if isinstance(t, OptionalType):
            val = self.get_type_name(t.value_type)
            return f"optional<{val}>"
        if isinstance(t, ResponseType):
            ok = self.get_type_name(t.ok_type)
            err = self.get_type_name(t.err_type)
            return f"Response<{ok}, {err}>"
        if isinstance(t, MapType):
            key = self.get_type_name(t.key_type)
            val = self.get_type_name(t.value_type)
            return f"Map<{key}, {val}>"
        if isinstance(t, TupleType):
            fields = ", ".join(f"{k}: {self.get_type_name(v)}" for k, v in t.fields.items())
            return f"{{ {fields} }}"
        return str(type(t).__name__)

    def types_compatible(self, expected: Optional[Type], actual: Optional[Type]) -> bool:
        """Check if actual type is compatible with expected type."""
        if expected is None or actual is None:
            return True  # Unknown types are compatible (lenient)

        # Resolve type aliases before comparison
        expected = self.resolve_type_alias(expected)
        actual = self.resolve_type_alias(actual)

        # Handle 'unknown' type as wildcard (compatible with anything)
        if isinstance(expected, SimpleType) and expected.name == "unknown":
            return True
        if isinstance(actual, SimpleType) and actual.name == "unknown":
            return True

        # Type parameters are compatible with any type (generic)
        if isinstance(expected, TypeParameter) or isinstance(actual, TypeParameter):
            return True

        # Same type class
        if type(expected) == type(actual):
            if isinstance(expected, SimpleType):
                # bool and boolean are equivalent
                exp_name = expected.name.lower()
                act_name = actual.name.lower()
                if exp_name in ("bool", "boolean") and act_name in ("bool", "boolean"):
                    return True
                # 'unknown' is compatible with anything
                if exp_name == "unknown" or act_name == "unknown":
                    return True
                return exp_name == act_name

            if isinstance(expected, ListType):
                return self.types_compatible(expected.element_type, actual.element_type)

            if isinstance(expected, OptionalType):
                return self.types_compatible(expected.value_type, actual.value_type)

            if isinstance(expected, ResponseType):
                return (self.types_compatible(expected.ok_type, actual.ok_type) and
                        self.types_compatible(expected.err_type, actual.err_type))

            if isinstance(expected, MapType):
                return (self.types_compatible(expected.key_type, actual.key_type) and
                        self.types_compatible(expected.value_type, actual.value_type))

            if isinstance(expected, BufferType):
                # Buffer types are compatible if both are buffers
                # Size checking is lenient - allows different sizes
                return True

        # Special case: int and uint are sometimes compatible
        if isinstance(expected, SimpleType) and isinstance(actual, SimpleType):
            if expected.name in ("int", "uint") and actual.name in ("int", "uint"):
                return True  # Allow int/uint mixing (with warning potentially)

        return False

    def infer_type(self, expr: Node) -> Optional[Type]:
        """Infer the type of an expression."""
        if expr is None:
            return None

        if isinstance(expr, IntegerLiteral):
            return SimpleType(name="int")

        if isinstance(expr, UIntegerLiteral):
            return SimpleType(name="uint")

        if isinstance(expr, StringLiteral):
            return SimpleType(name="string")

        if isinstance(expr, BooleanLiteral):
            return SimpleType(name="bool")

        if isinstance(expr, PrincipalLiteral):
            return SimpleType(name="principal")

        if isinstance(expr, Identifier):
            symbol = self.symbols.lookup(expr.name)
            if symbol:
                return symbol.data_type
            return None

        if isinstance(expr, ListLiteral):
            if expr.elements:
                elem_type = self.infer_type(expr.elements[0])
                return ListType(element_type=elem_type)
            return ListType(element_type=SimpleType(name="unknown"))

        if isinstance(expr, TupleLiteral):
            fields = {k: self.infer_type(v) for k, v in expr.fields.items()}
            return TupleType(fields=fields)

        if isinstance(expr, SomeExpression):
            val_type = self.infer_type(expr.value)
            return OptionalType(value_type=val_type)

        if isinstance(expr, NoneExpression):
            return OptionalType(value_type=SimpleType(name="unknown"))

        if isinstance(expr, OkExpression):
            ok_type = self.infer_type(expr.value)
            return ResponseType(ok_type=ok_type, err_type=SimpleType(name="unknown"))

        if isinstance(expr, ErrExpression):
            err_type = self.infer_type(expr.value)
            return ResponseType(ok_type=SimpleType(name="unknown"), err_type=err_type)

        if isinstance(expr, BinaryExpression):
            left_type = self.infer_type(expr.left)
            right_type = self.infer_type(expr.right)

            if expr.operator in self.ARITHMETIC_OPS:
                # Arithmetic returns the type of operands
                if isinstance(left_type, SimpleType) and left_type.name == "uint":
                    return SimpleType(name="uint")
                return SimpleType(name="int")

            if expr.operator in self.COMPARISON_OPS or expr.operator in self.LOGICAL_OPS:
                return SimpleType(name="bool")

            if expr.operator in self.BITWISE_OPS:
                return left_type or SimpleType(name="int")

            return left_type

        if isinstance(expr, UnaryExpression):
            if expr.operator == "!":
                return SimpleType(name="bool")
            return self.infer_type(expr.operand)

        if isinstance(expr, NullishCoalescing):
            # Result is the unwrapped optional type
            expr_type = self.infer_type(expr.expression)
            if isinstance(expr_type, OptionalType):
                return expr_type.value_type
            return expr_type

        if isinstance(expr, ForceUnwrap):
            expr_type = self.infer_type(expr.expression)
            if isinstance(expr_type, OptionalType):
                return expr_type.value_type
            return expr_type

        if isinstance(expr, CallExpression):
            callee_name = expr.callee if isinstance(expr.callee, str) else getattr(expr.callee, 'name', None)
            if callee_name:
                symbol = self.symbols.lookup(callee_name)
                if symbol and symbol.return_type:
                    return symbol.return_type
            return None

        if isinstance(expr, MethodCallExpression):
            # Handle map.get() returning optional
            if expr.method == "get":
                obj_type = self.infer_type(expr.object)
                if isinstance(obj_type, MapType):
                    return OptionalType(value_type=obj_type.value_type)
            return None

        if isinstance(expr, MemberExpression):
            obj_type = self.infer_type(expr.object)
            if isinstance(obj_type, TupleType) and expr.property in obj_type.fields:
                return obj_type.fields[expr.property]
            return None

        if isinstance(expr, IndexExpression):
            obj_type = self.infer_type(expr.object)
            if isinstance(obj_type, ListType):
                return OptionalType(value_type=obj_type.element_type)
            return None

        if isinstance(expr, LambdaExpression):
            # Lambda type is inferred from parameters and return type
            return expr.return_type

        if isinstance(expr, GroupedExpression):
            return self.infer_type(expr.expression)

        if isinstance(expr, (UnwrapExpression, TryExpression)):
            expr_type = self.infer_type(expr.expression)
            if isinstance(expr_type, (OptionalType, ResponseType)):
                if isinstance(expr_type, OptionalType):
                    return expr_type.value_type
                return expr_type.ok_type
            return expr_type

        if isinstance(expr, ThisExpression):
            # 'this' refers to current class
            if self.current_class:
                return SimpleType(name=self.current_class.name)
            return None

        return None

    # =========================================================================
    # VISIT METHODS - DECLARATIONS
    # =========================================================================

    def visit_Program(self, node: Program):
        """Visit program root."""
        # First pass: collect all top-level declarations
        for stmt in node.statements:
            if isinstance(stmt, FunctionDeclaration):
                self._declare_function(stmt)
            elif isinstance(stmt, TraitDeclaration):
                self._declare_trait(stmt)
            elif isinstance(stmt, ClassDeclaration):
                self._declare_class(stmt)
            elif isinstance(stmt, MapDeclaration):
                self._declare_map(stmt)
            elif isinstance(stmt, TypeAliasDeclaration):
                self._declare_type_alias(stmt)

        # Second pass: analyze all statements
        for stmt in node.statements:
            self.visit(stmt)

    def _declare_function(self, node: FunctionDeclaration):
        """Pre-declare a function for forward references."""
        existing = self.symbols.lookup_local(node.name)
        if existing:
            self.error(f"Function '{node.name}' already defined", node,
                       f"Previous definition at {existing.location}")
            return

        params = [
            SymbolInfo(name=p.name, kind="parameter", data_type=p.param_type)
            for p in node.parameters
        ]

        self.symbols.define(node.name, SymbolInfo(
            name=node.name,
            kind="function",
            data_type=node.return_type,
            location=node.location,
            is_mutable=False,
            parameters=params,
            return_type=node.return_type,
            decorators=node.decorators
        ))

    def _declare_trait(self, node: TraitDeclaration):
        """Pre-declare a trait."""
        self.defined_traits[node.name] = node

    def _declare_class(self, node: ClassDeclaration):
        """Pre-declare a class."""
        existing = self.symbols.lookup_local(node.name)
        if existing:
            self.error(f"Class '{node.name}' already defined", node)
            return

        self.symbols.define(node.name, SymbolInfo(
            name=node.name,
            kind="type",
            data_type=SimpleType(name=node.name),
            location=node.location,
            is_mutable=False,
            decorators=node.decorators
        ))

    def _declare_map(self, node: MapDeclaration):
        """Pre-declare a map."""
        self.defined_maps[node.name] = node
        self.symbols.define(node.name, SymbolInfo(
            name=node.name,
            kind="map",
            data_type=MapType(key_type=node.key_type, value_type=node.value_type),
            location=node.location,
            is_mutable=True
        ))

    def _declare_type_alias(self, node: TypeAliasDeclaration):
        """Pre-declare a type alias."""
        existing = self.symbols.lookup_local(node.name)
        if existing:
            self.error(f"Type alias '{node.name}' already defined", node,
                       f"Previous definition at {existing.location}")
            return

        self.symbols.define(node.name, SymbolInfo(
            name=node.name,
            kind="type_alias",
            data_type=node.target_type,
            location=node.location,
            is_mutable=False
        ))

    def visit_TypeAliasDeclaration(self, node: TypeAliasDeclaration):
        """Analyze type alias declaration."""
        # Already pre-declared, just validate the target type exists
        if node.target_type:
            self._validate_type(node.target_type, node)

    def _validate_type(self, t: Type, node: Node):
        """Validate that a type reference is valid."""
        if isinstance(t, SimpleType):
            # Check if it's a built-in type or a defined type alias
            if t.name not in self.BUILTIN_TYPES:
                symbol = self.symbols.lookup(t.name)
                if not symbol or symbol.kind != "type_alias":
                    # Could be a class or other user-defined type
                    if not symbol or symbol.kind not in ("type_alias", "type"):
                        pass  # Allow for now - may be a forward reference
        elif isinstance(t, ListType):
            if t.element_type:
                self._validate_type(t.element_type, node)
        elif isinstance(t, OptionalType):
            if t.value_type:
                self._validate_type(t.value_type, node)
        elif isinstance(t, ResponseType):
            if t.ok_type:
                self._validate_type(t.ok_type, node)
            if t.err_type:
                self._validate_type(t.err_type, node)
        elif isinstance(t, MapType):
            if t.key_type:
                self._validate_type(t.key_type, node)
            if t.value_type:
                self._validate_type(t.value_type, node)

    def resolve_type_alias(self, t: Optional[Type]) -> Optional[Type]:
        """Resolve type aliases to their underlying types."""
        if t is None:
            return None

        if isinstance(t, SimpleType):
            # Check if it's a type alias
            if t.name not in self.BUILTIN_TYPES:
                symbol = self.symbols.lookup(t.name)
                if symbol and symbol.kind == "type_alias" and symbol.data_type:
                    # Recursively resolve in case of chained aliases
                    return self.resolve_type_alias(symbol.data_type)
            return t

        # Recursively resolve container types
        if isinstance(t, ListType):
            return ListType(
                name=t.name,
                element_type=self.resolve_type_alias(t.element_type)
            )
        if isinstance(t, OptionalType):
            return OptionalType(
                name=t.name,
                value_type=self.resolve_type_alias(t.value_type)
            )
        if isinstance(t, ResponseType):
            return ResponseType(
                name=t.name,
                ok_type=self.resolve_type_alias(t.ok_type),
                err_type=self.resolve_type_alias(t.err_type)
            )
        if isinstance(t, MapType):
            return MapType(
                name=t.name,
                key_type=self.resolve_type_alias(t.key_type),
                value_type=self.resolve_type_alias(t.value_type)
            )

        return t

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        """Analyze function declaration."""
        old_function = self.current_function
        self.current_function = node
        self.has_returned = False

        self.symbols.enter_scope(node.name)

        # Register type parameters in scope (for generic functions)
        for type_param in node.type_params:
            self.symbols.define(type_param, SymbolInfo(
                name=type_param,
                kind="type_param",
                data_type=TypeParameter(name=type_param),
                location=node.location,
                is_mutable=False
            ))

        # Add parameters to scope
        for param in node.parameters:
            existing = self.symbols.lookup_local(param.name)
            if existing:
                self.error(f"Duplicate parameter '{param.name}'", param)
            else:
                self.symbols.define(param.name, SymbolInfo(
                    name=param.name,
                    kind="parameter",
                    data_type=param.param_type,
                    location=param.location,
                    is_mutable=False  # Parameters are immutable
                ))

        # Visit body
        if node.body:
            self.visit(node.body)

        # Check for missing return (Phase B)
        if node.return_type and not self.has_returned:
            # Check if return type is not void/unit
            if not (isinstance(node.return_type, SimpleType) and
                    node.return_type.name.lower() in ("void", "unit", "()")):
                self.warning(f"Function '{node.name}' may not return a value in all paths", node)

        # Check for unused parameters (Phase B)
        for symbol in self.symbols.get_unused_symbols():
            if symbol.kind == "parameter":
                self.warning(f"Unused parameter '{symbol.name}'", node)

        self.symbols.exit_scope()
        self.current_function = old_function

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        """Analyze variable declaration."""
        # Check for duplicate in current scope
        existing = self.symbols.lookup_local(node.name)
        if existing:
            self.error(f"Variable '{node.name}' already defined in this scope", node,
                       f"Previous definition at {existing.location}")
            return

        # Check for shadowing (Phase B)
        outer = self.symbols.lookup_in_outer(node.name)
        if outer:
            self.warning(f"Variable '{node.name}' shadows outer scope variable", node)

        # Visit the initializer
        if node.value:
            self.visit(node.value)

            # Type check if type is specified
            if node.var_type:
                actual_type = self.infer_type(node.value)
                if actual_type and not self.types_compatible(node.var_type, actual_type):
                    self.error(
                        f"Type mismatch: cannot assign {self.get_type_name(actual_type)} "
                        f"to {self.get_type_name(node.var_type)}",
                        node
                    )

        # Add to symbol table
        self.symbols.define(node.name, SymbolInfo(
            name=node.name,
            kind="variable",
            data_type=node.var_type or self.infer_type(node.value),
            location=node.location,
            is_mutable=True
        ))

    def visit_ConstantDeclaration(self, node: ConstantDeclaration):
        """Analyze constant declaration."""
        # Check for duplicate
        existing = self.symbols.lookup_local(node.name)
        if existing:
            self.error(f"Constant '{node.name}' already defined", node)
            return

        # Visit the initializer
        if node.value:
            self.visit(node.value)

            # Type check
            if node.const_type:
                actual_type = self.infer_type(node.value)
                if actual_type and not self.types_compatible(node.const_type, actual_type):
                    self.error(
                        f"Type mismatch: cannot assign {self.get_type_name(actual_type)} "
                        f"to {self.get_type_name(node.const_type)}",
                        node
                    )

        # Add to symbol table (immutable)
        self.symbols.define(node.name, SymbolInfo(
            name=node.name,
            kind="constant",
            data_type=node.const_type or self.infer_type(node.value),
            location=node.location,
            is_mutable=False
        ))

    def visit_ClassDeclaration(self, node: ClassDeclaration):
        """Analyze class declaration."""
        old_class = self.current_class
        self.current_class = node

        self.symbols.enter_scope(node.name)

        # Check trait implementation (Phase C)
        if node.implements:
            trait = self.defined_traits.get(node.implements)
            if trait:
                self._check_trait_compliance(node, trait)
            else:
                self.error(f"Trait '{node.implements}' not defined", node)

        # Visit members
        for member in node.members:
            self.visit(member)

        self.symbols.exit_scope()
        self.current_class = old_class

    def _check_trait_compliance(self, cls: ClassDeclaration, trait: TraitDeclaration):
        """Check if class implements all trait methods (Phase C)."""
        class_methods = {
            m.name: m for m in cls.members
            if isinstance(m, FunctionDeclaration)
        }

        for trait_method in trait.methods:
            if trait_method.name not in class_methods:
                self.error(
                    f"Class '{cls.name}' does not implement trait method '{trait_method.name}'",
                    cls
                )
            else:
                # Check signature compatibility
                impl = class_methods[trait_method.name]
                if len(impl.parameters) != len(trait_method.parameters):
                    self.error(
                        f"Method '{trait_method.name}' has wrong number of parameters "
                        f"(expected {len(trait_method.parameters)}, got {len(impl.parameters)})",
                        impl
                    )

    def visit_TraitDeclaration(self, node: TraitDeclaration):
        """Analyze trait declaration."""
        # Already pre-declared, just validate methods
        for method in node.methods:
            self.visit(method)

    def visit_MapDeclaration(self, node: MapDeclaration):
        """Analyze map declaration."""
        # Already handled in _declare_map
        pass

    # =========================================================================
    # VISIT METHODS - STATEMENTS
    # =========================================================================

    def visit_Block(self, node: Block):
        """Analyze block of statements."""
        for stmt in node.statements:
            if self.has_returned:
                self.warning("Unreachable code after return statement", stmt)
                break
            self.visit(stmt)

    def visit_AssignmentStatement(self, node: AssignmentStatement):
        """Analyze assignment statement."""
        # Check target exists
        target_name = None
        if isinstance(node.target, Identifier):
            target_name = node.target.name
        elif hasattr(node.target, 'name'):
            target_name = node.target.name

        if target_name:
            symbol = self.symbols.lookup(target_name)
            if not symbol:
                self.error(f"Undefined variable '{target_name}'", node)
            elif not symbol.is_mutable:
                self.error(f"Cannot assign to constant '{target_name}'", node,
                           "Use 'let' instead of 'const' if you need to reassign")
            else:
                symbol.used = True

                # Type check
                if node.value:
                    self.visit(node.value)
                    actual_type = self.infer_type(node.value)
                    if symbol.data_type and actual_type:
                        if not self.types_compatible(symbol.data_type, actual_type):
                            self.error(
                                f"Type mismatch: cannot assign {self.get_type_name(actual_type)} "
                                f"to {self.get_type_name(symbol.data_type)}",
                                node
                            )
        else:
            # Complex target (member access, index)
            self.visit(node.target)
            if node.value:
                self.visit(node.value)

    def visit_ReturnStatement(self, node: ReturnStatement):
        """Analyze return statement."""
        if not self.current_function:
            self.error("Return statement outside of function", node)
            return

        self.has_returned = True

        if node.expression:
            self.visit(node.expression)
            actual_type = self.infer_type(node.expression)
            expected_type = self.current_function.return_type

            if expected_type and actual_type:
                if not self.types_compatible(expected_type, actual_type):
                    self.error(
                        f"Return type mismatch: expected {self.get_type_name(expected_type)}, "
                        f"got {self.get_type_name(actual_type)}",
                        node
                    )

    def visit_IfStatement(self, node: IfStatement):
        """Analyze if statement."""
        # Check condition
        if node.condition:
            self.visit(node.condition)
            cond_type = self.infer_type(node.condition)
            if cond_type and isinstance(cond_type, SimpleType):
                if cond_type.name not in ("bool", "boolean"):
                    self.warning("If condition should be a boolean expression", node.condition)

        # Visit branches
        old_returned = self.has_returned

        if node.then_block:
            self.has_returned = False
            self.visit(node.then_block)
            then_returned = self.has_returned

        if node.else_block:
            self.has_returned = False
            self.visit(node.else_block)
            else_returned = self.has_returned

            # Only mark as returned if both branches return
            self.has_returned = then_returned and else_returned
        else:
            self.has_returned = old_returned

    def visit_ForStatement(self, node: ForStatement):
        """Analyze for statement."""
        # Enter a new scope for the loop variable
        self.symbols.enter_scope("for")

        # Register loop variable
        if node.init_var:
            var_type = node.init_type or self.infer_type(node.init_value)
            self.symbols.define(node.init_var, SymbolInfo(
                name=node.init_var,
                kind="variable",
                data_type=var_type,
                location=node.location,
                is_mutable=True
            ))

        # Validate init value
        if node.init_value:
            self.visit(node.init_value)

        # Validate condition
        if node.condition:
            self.visit(node.condition)
            cond_type = self.infer_type(node.condition)
            if cond_type and isinstance(cond_type, SimpleType):
                if cond_type.name not in ("bool", "boolean"):
                    self.warning("For loop condition should be a boolean expression", node)

        # Validate update expression
        if node.update_expr:
            self.visit(node.update_expr)

        # Visit body
        if node.body:
            self.visit(node.body)

        self.symbols.exit_scope()

    def visit_WhileStatement(self, node: WhileStatement):
        """Analyze while statement."""
        # Validate condition
        if node.condition:
            self.visit(node.condition)
            cond_type = self.infer_type(node.condition)
            if cond_type and isinstance(cond_type, SimpleType):
                if cond_type.name not in ("bool", "boolean"):
                    self.warning("While loop condition should be a boolean expression", node)

        # Warn about unbounded loops
        if node.max_iterations >= 1000:
            self.warning(f"While loop with {node.max_iterations} max iterations may be expensive", node)

        # Visit body
        if node.body:
            self.visit(node.body)

    def visit_ExpressionStatement(self, node: ExpressionStatement):
        """Analyze expression statement."""
        if node.expression:
            self.visit(node.expression)

    # =========================================================================
    # VISIT METHODS - EXPRESSIONS
    # =========================================================================

    def visit_Identifier(self, node: Identifier):
        """Check identifier is defined."""
        symbol = self.symbols.lookup(node.name)
        if not symbol:
            # Check if it's a built-in
            if node.name not in self.BUILTIN_TYPES:
                self.error(f"Undefined symbol '{node.name}'", node)
        else:
            self.symbols.mark_used(node.name)

    def visit_BinaryExpression(self, node: BinaryExpression):
        """Analyze binary expression."""
        self.visit(node.left)
        self.visit(node.right)

        left_type = self.infer_type(node.left)
        right_type = self.infer_type(node.right)

        # Check operator compatibility
        if node.operator in self.ARITHMETIC_OPS:
            if left_type and isinstance(left_type, SimpleType):
                if left_type.name not in ("int", "uint"):
                    self.error(
                        f"Invalid left operand type for '{node.operator}': {self.get_type_name(left_type)}",
                        node.left
                    )
            if right_type and isinstance(right_type, SimpleType):
                if right_type.name not in ("int", "uint"):
                    self.error(
                        f"Invalid right operand type for '{node.operator}': {self.get_type_name(right_type)}",
                        node.right
                    )

            # Overflow warning (Phase C)
            if node.operator in ("*", "+", "**"):
                if (left_type and right_type and
                        isinstance(left_type, SimpleType) and isinstance(right_type, SimpleType)):
                    if left_type.name == "uint" and right_type.name == "uint":
                        self.warning("Potential overflow in unsigned arithmetic", node)

    def visit_UnaryExpression(self, node: UnaryExpression):
        """Analyze unary expression."""
        self.visit(node.operand)

    def visit_CallExpression(self, node: CallExpression):
        """Analyze function call."""
        callee_name = node.callee if isinstance(node.callee, str) else getattr(node.callee, 'name', None)

        if callee_name:
            symbol = self.symbols.lookup(callee_name)
            if not symbol:
                # Check if it's a built-in function
                builtins = {"print", "map", "fold", "filter", "len", "concat", "append"}
                if callee_name not in builtins:
                    self.error(f"Undefined function '{callee_name}'", node)
            elif symbol.kind == "function":
                # Check argument count
                expected_count = len(symbol.parameters)
                actual_count = len(node.arguments)
                if expected_count != actual_count:
                    self.error(
                        f"Function '{callee_name}' expects {expected_count} arguments, got {actual_count}",
                        node
                    )

                # Check argument types
                for i, (param, arg) in enumerate(zip(symbol.parameters, node.arguments)):
                    self.visit(arg)
                    arg_type = self.infer_type(arg)
                    if param.data_type and arg_type:
                        if not self.types_compatible(param.data_type, arg_type):
                            self.error(
                                f"Argument {i + 1} type mismatch: expected {self.get_type_name(param.data_type)}, "
                                f"got {self.get_type_name(arg_type)}",
                                arg
                            )
                symbol.used = True
            else:
                self.error(f"'{callee_name}' is not a function", node)
        else:
            # Visit callee and arguments
            if isinstance(node.callee, Node):
                self.visit(node.callee)
            for arg in node.arguments:
                self.visit(arg)

    def visit_ContractCallExpression(self, node: ContractCallExpression):
        """Analyze contract call."""
        for arg in node.arguments:
            self.visit(arg)

    def visit_MethodCallExpression(self, node: MethodCallExpression):
        """Analyze method call."""
        self.visit(node.object)
        for arg in node.arguments:
            self.visit(arg)

    def visit_MemberExpression(self, node: MemberExpression):
        """Analyze member access."""
        self.visit(node.object)

    def visit_IndexExpression(self, node: IndexExpression):
        """Analyze index access."""
        self.visit(node.object)
        self.visit(node.index)

    def visit_NullishCoalescing(self, node: NullishCoalescing):
        """Analyze nullish coalescing."""
        self.visit(node.expression)
        self.visit(node.default)

    def visit_ForceUnwrap(self, node: ForceUnwrap):
        """Analyze force unwrap."""
        self.visit(node.expression)
        expr_type = self.infer_type(node.expression)
        if expr_type and not isinstance(expr_type, (OptionalType, ResponseType)):
            self.warning("Force unwrap on non-optional type", node)

    def visit_LambdaExpression(self, node: LambdaExpression):
        """Analyze lambda expression."""
        self.symbols.enter_scope("lambda")

        for param in node.parameters:
            self.symbols.define(param.name, SymbolInfo(
                name=param.name,
                kind="parameter",
                data_type=param.param_type,
                is_mutable=False
            ))

        if node.body:
            self.visit(node.body)

        self.symbols.exit_scope()

    # Literal visitors (no checks needed, just mark visited)
    def visit_IntegerLiteral(self, node): pass
    def visit_UIntegerLiteral(self, node): pass
    def visit_StringLiteral(self, node): pass
    def visit_BooleanLiteral(self, node): pass
    def visit_PrincipalLiteral(self, node): pass
    def visit_ThisExpression(self, node): pass
    def visit_NoneExpression(self, node): pass

    def visit_ListLiteral(self, node: ListLiteral):
        """Analyze list literal."""
        if not node.elements:
            return

        first_type = None
        for i, elem in enumerate(node.elements):
            self.visit(elem)
            elem_type = self.infer_type(elem)
            if i == 0:
                first_type = elem_type
            elif first_type and elem_type and not self.types_compatible(first_type, elem_type):
                self.warning(
                    f"Inconsistent list element type at index {i}: expected {self.get_type_name(first_type)}, "
                    f"got {self.get_type_name(elem_type)}",
                    elem
                )

    def visit_TupleLiteral(self, node: TupleLiteral):
        """Analyze tuple literal."""
        for field_expr in node.fields.values():
            self.visit(field_expr)

    def visit_SomeExpression(self, node: SomeExpression):
        """Analyze some() expression."""
        if node.value:
            self.visit(node.value)

    def visit_OkExpression(self, node: OkExpression):
        """Analyze ok() expression."""
        if node.value:
            self.visit(node.value)

    def visit_ErrExpression(self, node: ErrExpression):
        """Analyze err() expression."""
        if node.value:
            self.visit(node.value)

    def visit_UnwrapExpression(self, node: UnwrapExpression):
        """Analyze unwrap! expression."""
        if node.expression:
            self.visit(node.expression)

    def visit_TryExpression(self, node: TryExpression):
        """Analyze try! expression."""
        if node.expression:
            self.visit(node.expression)

    def visit_GroupedExpression(self, node: GroupedExpression):
        """Analyze grouped expression."""
        if node.expression:
            self.visit(node.expression)

    def visit_MatchExpression(self, node: MatchExpression):
        """Analyze match expression."""
        if node.expression:
            self.visit(node.expression)
        for arm in node.arms:
            self.visit(arm)

    def visit_MatchArm(self, node: MatchArm):
        """Analyze match arm."""
        self.symbols.enter_scope("match_arm")
        if node.pattern:
            # Pattern can introduce bindings
            if isinstance(node.pattern, Identifier):
                self.symbols.define(node.pattern.name, SymbolInfo(
                    name=node.pattern.name,
                    kind="variable",
                    data_type=None,
                    is_mutable=False
                ))
        if node.expression:
            self.visit(node.expression)
        self.symbols.exit_scope()

    def visit_LetExpression(self, node: LetExpression):
        """Analyze let expression."""
        self.symbols.enter_scope("let")
        for binding in node.bindings:
            self.visit(binding)
        if node.body:
            self.visit(node.body)
        self.symbols.exit_scope()

    def visit_LetBinding(self, node: LetBinding):
        """Analyze let binding."""
        if node.value:
            self.visit(node.value)
        self.symbols.define(node.name, SymbolInfo(
            name=node.name,
            kind="variable",
            data_type=self.infer_type(node.value),
            is_mutable=False
        ))


# Legacy alias for backward compatibility
class StxScriptSemanticAnalyzer(ASTSemanticAnalyzer):
    """Alias for backward compatibility."""
    pass
