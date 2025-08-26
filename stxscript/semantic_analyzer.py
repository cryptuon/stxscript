import lark
from typing import Dict, List, Set, Optional
from dataclasses import dataclass

class SemanticError(Exception):
    pass

@dataclass
class FunctionType:
    parameters: List[str]
    return_type: str
    is_public: bool

@dataclass
class TraitType:
    methods: Dict[str, FunctionType]

class StxScriptSemanticAnalyzer(lark.Visitor):
    def __init__(self):
        self.symbol_table: Dict[str, Dict] = {}
        self.current_scope: List[str] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.defined_types: Set[str] = {"int", "uint", "boolean", "string", "buffer", "principal", "list", "Response"}
        self.current_function: Optional[str] = None
        self.return_paths: Dict[str, bool] = {}
        self.used_symbols: Set[str] = set()
        self.defined_traits: Dict[str, TraitType] = {}

    def visit(self, tree):
        try:
            super().visit(tree)
        except SemanticError as e:
            self.errors.append(str(e))

    def enter_scope(self, scope_name):
        self.current_scope.append(scope_name)

    def exit_scope(self):
        scope = self.current_scope_name()
        # Check for unused variables in the exiting scope
        if scope in self.symbol_table:
            for symbol, info in self.symbol_table[scope].items():
                if info["type"] in ["variable", "parameter", "constant"] and symbol not in self.used_symbols:
                    self.warnings.append(f"Unused {info['type']}: {symbol} in scope {scope}")
        self.current_scope.pop()

    def current_scope_name(self):
        return ".".join(self.current_scope)

    def add_symbol(self, name, symbol_type, data_type):
        scope = self.current_scope_name()
        if scope not in self.symbol_table:
            self.symbol_table[scope] = {}
        self.symbol_table[scope][name] = {"type": symbol_type, "data_type": data_type}

    def check_symbol(self, name):
        self.used_symbols.add(name)
        scope = self.current_scope_name()
        while scope:
            if scope in self.symbol_table and name in self.symbol_table[scope]:
                return self.symbol_table[scope][name]
            scope = scope.rsplit(".", 1)[0] if "." in scope else ""
        raise SemanticError(f"Undefined symbol: {name}")

    def function_declaration(self, tree):
        decorators = [child.children[0].value for child in tree.children if isinstance(child, lark.Tree) and child.data == 'decorator']
        name = tree.children[1].value
        is_public = '@public' in decorators
        self.enter_scope(name)
        return_type = tree.children[4].children[0].value
        params = []
        for param in tree.children[2].children:
            param_name, param_type = param.children
            params.append(param_type.value)
            self.add_symbol(param_name.value, "parameter", param_type.value)
        self.add_symbol(name, "function", FunctionType(params, return_type, is_public))
        self.current_function = name
        self.return_paths[name] = False
        self.visit(tree.children[-1])
        if not self.return_paths[name] and return_type != 'void':
            self.errors.append(f"Function {name} does not return a value in all code paths")
        self.current_function = None
        self.exit_scope()

    def variable_declaration(self, tree):
        name, var_type, value = tree.children
        self.add_symbol(name.value, "variable", var_type.value)
        value_type = self.infer_type(value)
        if not self.type_check(var_type.value, value_type):
            raise SemanticError(f"Type mismatch: {name.value} declared as {var_type.value}, but assigned {value_type}")

    def constant_declaration(self, tree):
        name, const_type, value = tree.children
        self.add_symbol(name.value, "constant", const_type.value)
        value_type = self.infer_type(value)
        if not self.type_check(const_type.value, value_type):
            raise SemanticError(f"Type mismatch: {name.value} declared as {const_type.value}, but assigned {value_type}")

    def expression(self, tree):
        if isinstance(tree.children[0], lark.Token):
            if tree.children[0].type == "IDENTIFIER":
                self.check_symbol(tree.children[0].value)
        else:
            for child in tree.children:
                self.visit(child)

    def infer_type(self, tree):
        if isinstance(tree, lark.Token):
            if tree.type == "NUMBER":
                return "int"  # This is a simplification, might be uint
            elif tree.type == "STRING":
                return "string"
            elif tree.type == "BOOLEAN":
                return "boolean"
            elif tree.type == "IDENTIFIER":
                return self.check_symbol(tree.value)["data_type"]
        elif isinstance(tree, lark.Tree):
            if tree.data == "function_call":
                func_name = tree.children[0].value
                func_type = self.check_symbol(func_name)["data_type"]
                if isinstance(func_type, FunctionType):
                    return func_type.return_type
        raise SemanticError(f"Unable to infer type for: {tree}")

    def type_check(self, expected_type, actual_type):
        # Implement more sophisticated type checking here
        # For now, we'll just check if types are exactly the same
        return expected_type == actual_type

    def trait_declaration(self, tree):
        name = tree.children[0].value
        methods = {}
        for method in tree.children[1:]:
            method_name = method.children[0].value
            params = [param.children[1].value for param in method.children[1].children]
            return_type = method.children[2].children[0].value
            methods[method_name] = FunctionType(params, return_type, False)
        self.defined_traits[name] = TraitType(methods)

    def return_statement(self, tree):
        if self.current_function:
            self.return_paths[self.current_function] = True
            func_type = self.check_symbol(self.current_function)["data_type"]
            return_type = self.infer_type(tree.children[0])
            if not self.type_check(func_type.return_type, return_type):
                raise SemanticError(f"Return type mismatch in function {self.current_function}: expected {func_type.return_type}, got {return_type}")

    def binary_operation(self, tree):
        left_type = self.infer_type(tree.children[0])
        right_type = self.infer_type(tree.children[2])
        op = tree.children[1].value
        if op in ['+', '-', '*', '/']:
            if left_type not in ['int', 'uint'] or right_type not in ['int', 'uint']:
                raise SemanticError(f"Invalid types for arithmetic operation: {left_type} {op} {right_type}")
            # Check for potential overflow
            if op in ['*', '+'] and left_type == 'uint' and right_type == 'uint':
                self.warnings.append(f"Potential overflow in operation: {tree.children[0]} {op} {tree.children[2]}")

    def analyze(self, tree):
        self.visit(tree)
        return self.errors, self.warnings