from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any

@dataclass
class Node:
    pass

@dataclass
class Program(Node):
    statements: List[Node]

@dataclass
class Statement(Node):
    pass

@dataclass
class Expression(Node):
    pass

@dataclass
class Type(Node):
    name: str

class Identifier(Expression):
    name: str
    
    def __init__(self, name: str):
        self.name = name

    def __hash__(self):
        return hash(self.name)
    
    def __repr__(self) -> str:
        return self.name

@dataclass
class FunctionDeclaration(Statement):
    decorators: List[str]
    name: str
    parameters: List['Parameter']
    return_type: Optional[Type]
    body: 'Block'

@dataclass
class VariableDeclaration(Statement):
    name: str
    type: Optional[Type]
    value: Expression

@dataclass
class ConstantDeclaration(Statement):
    name: str
    type: Optional[Type]
    value: Expression

@dataclass
class MapDeclaration(Statement):
    name: str
    key_type: Type
    value_type: Type

@dataclass
class AssetDeclaration(Statement):
    name: str
    fields: List['Parameter']

@dataclass
class TraitDeclaration(Statement):
    name: str
    functions: List[FunctionDeclaration]

@dataclass
class Parameter(Node):
    name: str
    type: Type

@dataclass
class Block(Node):
    statements: List[Statement]

@dataclass
class IfStatement(Statement):
    condition: Expression
    true_block: Block
    else_ifs: List['ElseIf']
    else_block: Optional[Block]

@dataclass
class ElseIf(Node):
    condition: Expression
    block: Block

@dataclass
class TryCatchStatement(Statement):
    try_block: Block
    error_var: str
    catch_block: Block

@dataclass
class ThrowStatement(Statement):
    expression: Expression

@dataclass
class ReturnStatement(Statement):
    expression: Optional[Expression]

@dataclass
class ExpressionStatement(Statement):
    expression: Expression

@dataclass
class ImportDeclaration(Statement):
    module: str
    imports: List[str]

@dataclass
class ExportDeclaration(Statement):
    declaration: Union[FunctionDeclaration, VariableDeclaration, ConstantDeclaration]

@dataclass
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class UnaryExpression(Expression):
    operator: str
    expression: Expression

@dataclass
class TernaryExpression(Expression):
    condition: Expression
    true_expr: Expression
    false_expr: Expression

@dataclass
class CallExpression(Expression):
    callee: Expression
    arguments: List[Expression]

@dataclass
class MemberExpression(Expression):
    object: Expression
    property: str

@dataclass
class Literal(Expression):
    value: Union[int, float, str, bool]

@dataclass
class ListLiteral(Expression):
    elements: List[Expression]

@dataclass
class TupleLiteral(Expression):
    elements: Dict[str, Expression]

@dataclass
class OptionalLiteral(Expression):
    value: Optional[Expression]

@dataclass
class PrincipalLiteral(Expression):
    value: str

@dataclass
class ListType(Type):
    element_type: Type
    def __init__(self, element_type):
        super().__init__(f"List<{element_type.name}>")
        self.element_type = element_type

@dataclass
class TupleType(Type):
    fields: Dict[str, Type]
    def __init__(self,fields):
        super().__init__(f"Tuple<{', '.join(f'{k}: {v.name}' for k, v in fields.items())}>")
        self.fields = fields

@dataclass
class Field(Node):
    def __init__(self, name, type):
        self.name = name
        self.type = type
@dataclass
class OptionalType(Type):
    value_type: Type

@dataclass
class ResponseType(Type):
    ok_type: Type
    err_type: Type

    def __init__(self, ok_type: Type, err_type: Type):
        super().__init__(f"Response<{ok_type.name}, {err_type.name}>")
        self.ok_type = ok_type
        self.err_type = err_type

@dataclass
class TypeCheck(Expression):
    expression: Expression
    checked_type: Type

@dataclass
class TypeAssertion(Expression):
    expression: Expression
    asserted_type: Type

@dataclass
class ListComprehension(Expression):
    expression: Expression
    iterable: Expression
    iterator: Identifier
    condition: Optional[Expression]

@dataclass
class ContractCallExpression(Expression):
    contract: Expression
    function: str
    arguments: List[Expression]

@dataclass
class AssetCallExpression(Expression):
    asset: str
    function: str
    arguments: List[Expression]

@dataclass
class MapExpression(Expression):
    list: Expression
    function: Expression

@dataclass
class FilterExpression(Expression):
    list: Expression
    function: Expression

@dataclass
class FoldExpression(Expression):
    list: Expression
    initial: Expression
    function: Expression

@dataclass
class Decorator(Node):
    name: str

@dataclass
class FunctionSignature(Node):
    name: str
    parameters: List[Parameter]
    return_type: Type

@dataclass
class LambdaExpression(Expression):
    parameters: List[Parameter]
    body: Expression

    def __init__(self, parameters, body):
        super().__init__()
        self.parameters = parameters
        self.body = body