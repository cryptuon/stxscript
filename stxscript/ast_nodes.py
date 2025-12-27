"""
StxScript AST Node Definitions
Complete AST representation for the StxScript language
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any


# =============================================================================
# SOURCE LOCATION
# =============================================================================

@dataclass
class SourceLocation:
    """Tracks source code location for error reporting"""
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None

    def __str__(self):
        if self.end_line and self.end_column:
            return f"line {self.line}:{self.column} to {self.end_line}:{self.end_column}"
        return f"line {self.line}:{self.column}"


# =============================================================================
# BASE CLASSES
# =============================================================================

@dataclass
class Node:
    """Base class for all AST nodes"""
    location: Optional[SourceLocation] = field(default=None, compare=False)


@dataclass
class Statement(Node):
    """Base class for statements"""
    pass


@dataclass
class Expression(Node):
    """Base class for expressions"""
    pass


# =============================================================================
# TYPE NODES
# =============================================================================

@dataclass
class Type(Node):
    """Base type node"""
    name: str = ""


@dataclass
class SimpleType(Type):
    """Simple type: int, uint, bool, string, buffer, principal"""
    pass


@dataclass
class BufferType(Type):
    """Buffer type with optional size: buffer<N>"""
    size: Optional[int] = None

    def __post_init__(self):
        if self.size and not self.name:
            self.name = f"buffer<{self.size}>"
        elif not self.name:
            self.name = "buffer"


@dataclass
class ListType(Type):
    """List type: list<T>"""
    element_type: 'Type' = None

    def __post_init__(self):
        if self.element_type and not self.name:
            self.name = f"list<{self.element_type.name}>"


@dataclass
class OptionalType(Type):
    """Optional type: optional<T>"""
    value_type: 'Type' = None

    def __post_init__(self):
        if self.value_type and not self.name:
            self.name = f"optional<{self.value_type.name}>"


@dataclass
class ResponseType(Type):
    """Response type: Response<Ok, Err>"""
    ok_type: 'Type' = None
    err_type: 'Type' = None

    def __post_init__(self):
        if self.ok_type and self.err_type and not self.name:
            self.name = f"Response<{self.ok_type.name}, {self.err_type.name}>"


@dataclass
class MapType(Type):
    """Map type: Map<K, V>"""
    key_type: 'Type' = None
    value_type: 'Type' = None

    def __post_init__(self):
        if self.key_type and self.value_type and not self.name:
            self.name = f"Map<{self.key_type.name}, {self.value_type.name}>"


@dataclass
class TupleType(Type):
    """Tuple type: { field: Type, ... }"""
    fields: Dict[str, 'Type'] = field(default_factory=dict)

    def __post_init__(self):
        if self.fields and not self.name:
            fields_str = ', '.join(f'{k}: {v.name}' for k, v in self.fields.items())
            self.name = f"{{ {fields_str} }}"


@dataclass
class TypeParameter(Type):
    """Generic type parameter: T, K, V, etc."""
    # name is inherited from Type and holds the parameter name like "T"
    pass


# =============================================================================
# PROGRAM AND DECLARATIONS
# =============================================================================

@dataclass
class Program(Node):
    """Root node containing all top-level declarations"""
    statements: List[Node] = field(default_factory=list)


@dataclass
class Decorator(Node):
    """Decorator: @name"""
    name: str = ""


@dataclass
class Parameter(Node):
    """Function parameter: name: type"""
    name: str = ""
    param_type: Type = None


@dataclass
class Block(Node):
    """Block of statements: { ... }"""
    statements: List[Statement] = field(default_factory=list)


@dataclass
class FunctionDeclaration(Statement):
    """Function declaration"""
    name: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    return_type: Optional[Type] = None
    body: Optional[Block] = None
    decorators: List[str] = field(default_factory=list)
    type_params: List[str] = field(default_factory=list)  # Generic type parameters: ["T", "U"]


@dataclass
class VariableDeclaration(Statement):
    """Variable declaration: let name: type = value;"""
    name: str = ""
    value: Expression = None
    var_type: Optional[Type] = None


@dataclass
class ConstantDeclaration(Statement):
    """Constant declaration: const name: type = value;"""
    name: str = ""
    value: Expression = None
    const_type: Optional[Type] = None


@dataclass
class MapDeclaration(Statement):
    """Map declaration: map name<K, V>;"""
    name: str = ""
    key_type: Type = None
    value_type: Type = None


@dataclass
class FieldDeclaration(Statement):
    """Class field declaration: @decorator name: type = value;"""
    name: str = ""
    field_type: Type = None
    value: Optional[Expression] = None
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassDeclaration(Statement):
    """Class declaration: @decorator class Name implements Trait { ... }"""
    name: str = ""
    members: List[Node] = field(default_factory=list)
    implements: Optional[str] = None
    decorators: List[str] = field(default_factory=list)


@dataclass
class TraitMethod(Node):
    """Trait method signature: name(params): type;"""
    name: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    return_type: Optional[Type] = None


@dataclass
class TraitDeclaration(Statement):
    """Trait declaration: trait Name { methods }"""
    name: str = ""
    methods: List[TraitMethod] = field(default_factory=list)


@dataclass
class ImportDeclaration(Statement):
    """Import statement: import { names } from "module";"""
    module: str = ""
    imports: List[str] = field(default_factory=list)


@dataclass
class ExportDeclaration(Statement):
    """Export statement: export declaration"""
    declaration: Statement = None


@dataclass
class TypeAliasDeclaration(Statement):
    """Type alias declaration: type Name = Type;"""
    name: str = ""
    target_type: 'Type' = None


# =============================================================================
# STATEMENTS
# =============================================================================

@dataclass
class AssignmentStatement(Statement):
    """Assignment: target = value;"""
    target: Expression = None
    value: Expression = None


@dataclass
class ReturnStatement(Statement):
    """Return statement: return expr;"""
    expression: Optional[Expression] = None


@dataclass
class IfStatement(Statement):
    """If statement: if (cond) { } else { }"""
    condition: Expression = None
    then_block: Block = None
    else_block: Optional[Union[Block, 'IfStatement']] = None


@dataclass
class ForStatement(Statement):
    """For loop: for (let i = 0; i < 10; i = i + 1) { body }"""
    init_var: str = ""
    init_type: Optional[Type] = None
    init_value: Expression = None
    condition: Expression = None
    update_var: str = ""
    update_expr: Expression = None
    body: Optional[Block] = None


@dataclass
class WhileStatement(Statement):
    """While loop: while (condition) { body }"""
    condition: Expression = None
    body: Optional[Block] = None
    max_iterations: int = 100  # Default limit for bounded loop


@dataclass
class ExpressionStatement(Statement):
    """Expression as statement: expr;"""
    expression: Expression = None


@dataclass
class MapInsert(Statement):
    """Map insert: map.insert(key, value);"""
    map_name: str = ""
    key: Expression = None
    value: Expression = None


@dataclass
class MapUpdate(Statement):
    """Map update: map.update(key, value);"""
    map_name: str = ""
    key: Expression = None
    value: Expression = None


@dataclass
class MapDelete(Statement):
    """Map delete: map.delete(key);"""
    map_name: str = ""
    key: Expression = None


# =============================================================================
# EXPRESSIONS - Identifiers and Literals
# =============================================================================

@dataclass
class Identifier(Expression):
    """Identifier reference"""
    name: str = ""

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"Identifier({self.name})"


@dataclass
class Literal(Expression):
    """Literal value: number, string, boolean"""
    value: Union[int, str, bool] = None
    literal_type: str = "unknown"  # "int", "uint", "string", "bool"


@dataclass
class IntegerLiteral(Expression):
    """Integer literal: 42, -5"""
    value: int = 0


@dataclass
class UIntegerLiteral(Expression):
    """Unsigned integer literal: 42u"""
    value: int = 0


@dataclass
class StringLiteral(Expression):
    """String literal: "hello" """
    value: str = ""


@dataclass
class BooleanLiteral(Expression):
    """Boolean literal: true, false"""
    value: bool = False


@dataclass
class PrincipalLiteral(Expression):
    """Principal literal: 'SP123..."""
    value: str = ""


@dataclass
class ListLiteral(Expression):
    """List literal: [a, b, c]"""
    elements: List[Expression] = field(default_factory=list)


@dataclass
class TupleLiteral(Expression):
    """Tuple literal: { name: value, ... }"""
    fields: Dict[str, Expression] = field(default_factory=dict)


# =============================================================================
# EXPRESSIONS - Operations
# =============================================================================

@dataclass
class BinaryExpression(Expression):
    """Binary operation: left op right"""
    left: Expression = None
    operator: str = ""
    right: Expression = None


@dataclass
class UnaryExpression(Expression):
    """Unary operation: op expr"""
    operator: str = ""
    operand: Expression = None


@dataclass
class NullishCoalescing(Expression):
    """Nullish coalescing: expr ?? default"""
    expression: Expression = None
    default: Expression = None


@dataclass
class ForceUnwrap(Expression):
    """Force unwrap: expr!"""
    expression: Expression = None


@dataclass
class IndexExpression(Expression):
    """Index access: expr[index]"""
    object: Expression = None
    index: Expression = None


@dataclass
class MemberExpression(Expression):
    """Member access: object.property"""
    object: Expression = None
    property: str = ""


@dataclass
class MethodCallExpression(Expression):
    """Method call: object.method(args)"""
    object: Expression = None
    method: str = ""
    arguments: List[Expression] = field(default_factory=list)


# =============================================================================
# EXPRESSIONS - Calls
# =============================================================================

@dataclass
class CallExpression(Expression):
    """Function call: func(args)"""
    callee: Union[str, Expression] = ""
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class ContractCallExpression(Expression):
    """Contract call: Contract.method(args)"""
    contract: str = ""
    method: str = ""
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class NewExpression(Expression):
    """New expression: new Type<T>(args)"""
    type_name: str = ""
    type_params: List[Type] = field(default_factory=list)


# =============================================================================
# EXPRESSIONS - Special
# =============================================================================

@dataclass
class ThisExpression(Expression):
    """This reference: this"""
    pass


@dataclass
class SomeExpression(Expression):
    """Some expression: some(value)"""
    value: Expression = None


@dataclass
class NoneExpression(Expression):
    """None expression: none()"""
    pass


@dataclass
class OkExpression(Expression):
    """Ok expression: ok(value)"""
    value: Expression = None


@dataclass
class ErrExpression(Expression):
    """Err expression: err(value)"""
    value: Expression = None


@dataclass
class UnwrapExpression(Expression):
    """Unwrap expression: unwrap!(expr)"""
    expression: Expression = None


@dataclass
class TryExpression(Expression):
    """Try expression: try!(expr)"""
    expression: Expression = None


@dataclass
class GroupedExpression(Expression):
    """Grouped expression: (expr)"""
    expression: Expression = None


# =============================================================================
# EXPRESSIONS - Lambda
# =============================================================================

@dataclass
class LambdaExpression(Expression):
    """Lambda expression: (params): type => body"""
    parameters: List[Parameter] = field(default_factory=list)
    body: Expression = None
    return_type: Optional[Type] = None


# =============================================================================
# EXPRESSIONS - Match and Let
# =============================================================================

@dataclass
class MatchArm(Node):
    """Match arm: pattern => expression;"""
    pattern: Expression = None
    expression: Expression = None


@dataclass
class MatchExpression(Expression):
    """Match expression: match expr { arms }"""
    expression: Expression = None
    arms: List[MatchArm] = field(default_factory=list)


@dataclass
class LetBinding(Node):
    """Let binding: name = value;"""
    name: str = ""
    value: Expression = None


@dataclass
class LetExpression(Expression):
    """Let expression: let { bindings } in expr"""
    bindings: List[LetBinding] = field(default_factory=list)
    body: Expression = None


# =============================================================================
# UTILITY EXPRESSIONS (for higher-order operations)
# =============================================================================

@dataclass
class MapFunctionExpression(Expression):
    """Map operation: map(list, fn)"""
    list_expr: Expression = None
    function: Expression = None


@dataclass
class FilterExpression(Expression):
    """Filter operation: filter(list, fn)"""
    list_expr: Expression = None
    function: Expression = None


@dataclass
class FoldExpression(Expression):
    """Fold operation: fold(list, init, fn)"""
    list_expr: Expression = None
    initial: Expression = None
    function: Expression = None


# =============================================================================
# PATTERN NODES
# =============================================================================

@dataclass
class WildcardPattern(Expression):
    """Wildcard pattern: _"""
    pass
