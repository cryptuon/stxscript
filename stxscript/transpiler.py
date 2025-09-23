import lark
import os
from .semantic_analyzer import StxScriptSemanticAnalyzer
from .error_handler import EnhancedErrorHandler, create_helpful_error_message

class StxScriptTranspiler:
    def __init__(self):
        # Get the directory of this file to locate working_grammar.lark
        current_dir = os.path.dirname(__file__)
        grammar_path = os.path.join(current_dir, 'working_grammar.lark')

        with open(grammar_path, 'r') as grammar_file:
            self.parser = lark.Lark(grammar_file.read(), start='start', parser='lalr')
        self.semantic_analyzer = StxScriptSemanticAnalyzer()
        self.error_handler = EnhancedErrorHandler()

    def transpile(self, stxscript):
        try:
            tree = self.parser.parse(stxscript)

            # TODO: Fix semantic analysis for simplified grammar
            # errors, warnings = self.semantic_analyzer.analyze(tree)
            # if errors:
            #     raise ValueError("Semantic errors found:\n" + "\n".join(errors))

            transformer = StxScriptTransformer()
            clarity_code = transformer.transform(tree)
            return clarity_code

        except Exception as e:
            # Create enhanced error message
            enhanced_error = self.error_handler.enhance_error(e, stxscript)
            raise Exception(str(enhanced_error)) from e

    def transpile_with_error_handling(self, stxscript):
        """Transpile with comprehensive error handling and suggestions"""
        try:
            clarity_code = self.transpile(stxscript)
            return {"success": True, "clarity": clarity_code}
        except Exception as e:
            error_message = create_helpful_error_message(e, stxscript)
            return {"success": False, "error": error_message}

class StxScriptTransformer(lark.Transformer):
    def start(self, statements):
        result = []
        for statement in statements:
            if hasattr(statement, 'children') and statement.children:
                result.extend(statement.children)
            elif statement:
                result.append(str(statement))
        return "\n".join(result)

    def statement(self, items):
        return items[0]

    def variable_declaration(self, items):
        # Handle two cases: "let x = value;" or "let x: type = value;"
        if len(items) == 2:  # let x = value;
            name, value = items[0], items[1]
            return f"(define-data-var {name} {self.infer_type(str(value))} {value})"
        elif len(items) == 3:  # let x: type = value;
            name, type_annotation, value = items[0], items[1], items[2]
            return f"(define-data-var {name} {type_annotation} {value})"
        else:
            raise ValueError(f"Unexpected number of items in variable_declaration: {len(items)}")

    def constant_declaration(self, items):
        if len(items) == 2:  # const x = value;
            name, value = items[0], items[1]
            return f"(define-constant {name} {value})"
        else:  # const x: type = value;
            name, type_annotation, value = items[0], items[1], items[2]
            return f"(define-constant {name} {value})"

    def expression_statement(self, items):
        return str(items[0])

    def function_declaration(self, items):
        # Items are already processed by the transformer
        # Expected: [decorator, name, params, return_type, body] or [name, params, return_type, body]

        decorators = []
        idx = 0

        # Check for decorators (strings starting with @)
        while idx < len(items) and isinstance(items[idx], str) and items[idx].startswith('@'):
            decorators.append(items[idx])
            idx += 1

        name = items[idx]
        idx += 1

        # Handle parameters (could be None or a list)
        params = items[idx] if idx < len(items) and isinstance(items[idx], list) else None
        idx += 1  # Always increment for parameter slot

        # Handle return type (could be None or a string)
        return_type = None
        if idx < len(items) and isinstance(items[idx], str) and not items[idx].startswith('('):
            return_type = items[idx]
        idx += 1  # Always increment for return type slot

        body = items[idx] if idx < len(items) else ""

        is_public = any('public' in d for d in decorators)

        if is_public:
            define_keyword = "define-public"
        else:
            define_keyword = "define-private"

        if params:
            params_str = " ".join(f"({p[0]} {p[1]})" for p in params)
        else:
            params_str = ""

        return f"({define_keyword} ({name} {params_str})\n  {body})"

    def block(self, items):
        return "\n".join(str(item) for item in items if item)

    def decorator(self, items):
        return f"@{items[0]}"

    def parameter_list(self, items):
        return items

    def parameter(self, items):
        return items

    def function_call(self, items):
        func = items[0]
        args = items[1].children if len(items) > 1 and hasattr(items[1], 'children') else []
        return f"({func} {' '.join(str(arg) for arg in args)})"

    def argument_list(self, items):
        return items

    def expression(self, items):
        return str(items[0])

    # Type handling
    def type(self, items):
        if items:
            return str(items[0])
        return "unknown"

    # Literal handlers
    def literal(self, items):
        return str(items[0])

    def INTEGER(self, token):
        return str(token)

    def UINTEGER(self, token):
        return f"u{token.value[:-1]}"

    def STRING(self, token):
        return str(token)

    def BOOLEAN(self, token):
        return str(token)

    def IDENTIFIER(self, token):
        return str(token)

    def INT_TYPE(self, token):
        return "int"

    def UINT_TYPE(self, token):
        return "uint"

    def BOOLEAN_TYPE(self, token):
        return "bool"

    def STRING_TYPE(self, token):
        return "string"

    def BUFFER_TYPE(self, token):
        return "buffer"

    def PRINCIPAL_TYPE(self, token):
        return "principal"

    # Expression methods
    def logical_or(self, items):
        if len(items) == 1:
            return items[0]
        # Handle left (or_op right)*
        result = items[0]
        for i in range(1, len(items), 2):
            op = items[i]  # or_op
            right = items[i + 1]
            result = f"(or {result} {right})"
        return result

    def logical_and(self, items):
        if len(items) == 1:
            return items[0]
        # Handle left (and_op right)*
        result = items[0]
        for i in range(1, len(items), 2):
            op = items[i]  # and_op
            right = items[i + 1]
            result = f"(and {result} {right})"
        return result

    def equality(self, items):
        if len(items) == 1:
            return items[0]
        # Handle left (eq_op right)*
        result = items[0]
        for i in range(1, len(items), 2):
            op = items[i]  # eq_op
            right = items[i + 1]
            if str(op) == "==":
                result = f"(is-eq {result} {right})"
            else:  # !=
                result = f"(not (is-eq {result} {right}))"
        return result

    def comparison(self, items):
        if len(items) == 1:
            return items[0]
        # Handle left (comp_op right)*
        result = items[0]
        for i in range(1, len(items), 2):
            op = items[i]  # comp_op
            right = items[i + 1]
            result = f"({op} {result} {right})"
        return result

    def addition(self, items):
        if len(items) == 1:
            return items[0]
        # Handle left (add_op right)*
        result = items[0]
        for i in range(1, len(items), 2):
            op = items[i]  # This is now an add_op tree
            right = items[i + 1]
            result = f"({op} {result} {right})"
        return result

    # Operator token methods - these receive the actual token directly
    def ADD_OP(self, token):
        return str(token)

    def MUL_OP(self, token):
        op = str(token)
        return "mod" if op == "%" else op

    def COMP_OP(self, token):
        return str(token)

    def EQ_OP(self, token):
        return str(token)

    def AND_OP(self, token):
        return "&&"

    def OR_OP(self, token):
        return "||"

    def UNARY_OP(self, token):
        return str(token)

    def POW_OP(self, token):
        return str(token)

    def multiplication(self, items):
        if len(items) == 1:
            return items[0]
        # Handle left (mul_op right)*
        result = items[0]
        for i in range(1, len(items), 2):
            op = items[i]  # This is now a mul_op tree
            right = items[i + 1]
            result = f"({op} {result} {right})"
        return result

    def unary(self, items):
        if len(items) == 1:
            return items[0]
        elif len(items) == 2:  # op expr
            op, expr = items
            if op == "!":
                return f"(not {expr})"
            elif op == "-":
                return f"(- {expr})"
            elif op == "+":
                return expr  # Unary + is a no-op
        else:
            raise ValueError(f"Unexpected unary items: {items}")

    def power(self, items):
        if len(items) == 1:
            return items[0]
        elif len(items) == 3:  # base POW_OP exp
            base, op, exp = items
            return f"(pow {base} {exp})"
        else:
            raise ValueError(f"Unexpected power items: {items}")

    def atom(self, items):
        return items[0]

    # Statement methods
    def assignment_statement(self, items):
        var_name, value = items[0], items[1]
        return f"(var-set {var_name} {value})"

    def return_statement(self, items):
        if items and items[0] is not None:
            return f"(ok {items[0]})"
        else:
            return "(ok true)"

    def if_statement(self, items):
        # if_statement: "if" "(" expression ")" block ["else" (if_statement | block)]
        # items: [condition, then_block] or [condition, then_block, else_part]

        condition = items[0]
        then_block = items[1]

        if len(items) == 3:  # Has else clause
            else_part = items[2]
            return f"(if {condition}\n  {then_block}\n  {else_part})"
        else:
            return f"(if {condition}\n  {then_block})"

    def match_expression(self, items):
        # match_expression: "match" expression "{" match_arm+ "}"
        # items: [expression, match_arm1, match_arm2, ...]

        expr = items[0]
        arms = items[1:]

        # Build nested if-else chain from right to left
        result = "none"  # Default if no match

        # Process arms in reverse to build the chain
        for arm in reversed(arms):
            pattern, value = arm  # Each arm is [pattern, expression]

            if pattern == "_":  # Wildcard pattern (always matches)
                result = str(value)
            else:
                condition = f"(is-eq {expr} {pattern})"
                result = f"(if {condition} {value} {result})"

        return result

    def match_arm(self, items):
        # match_arm: pattern "=>" expression ";"
        # items: [pattern, expression]
        return [items[0], items[1]]

    def pattern(self, items):
        # pattern: IDENTIFIER | literal | "_"
        if items:
            return str(items[0])
        else:
            return "_"

    def let_expression(self, items):
        # let_expression: "let" "{" let_binding+ "}" "in" expression
        # items: [binding1, binding2, ..., in_expression]

        bindings = items[:-1]  # All but the last item
        in_expr = items[-1]    # Last item is the 'in' expression

        # Build nested let structure for Clarity
        # (let ((var1 val1) (var2 val2)) in_expr)
        binding_pairs = []
        for binding in bindings:
            var_name, value = binding
            binding_pairs.append(f"({var_name} {value})")

        bindings_str = " ".join(binding_pairs)
        return f"(let ({bindings_str}) {in_expr})"

    def let_binding(self, items):
        # let_binding: IDENTIFIER "=" expression ";"
        # items: [identifier, expression]
        return [items[0], items[1]]

    def unwrap_expression(self, items):
        # unwrap_expression: UNWRAP "(" expression ")"
        # items: [UNWRAP_token, expression]
        expr = items[1] if len(items) > 1 else items[0]
        return f"(unwrap! {expr} (err u100))"

    def try_expression(self, items):
        # try_expression: TRY "(" expression ")"
        # items: [TRY_token, expression]
        expr = items[1] if len(items) > 1 else items[0]
        return f"(try! {expr})"

    def list_literal(self, items):
        # list_literal: "[" [expression ("," expression)*] "]"
        # items: [expr1, expr2, expr3, ...] or []

        if not items or (len(items) == 1 and items[0] is None):
            return "(list)"  # Empty list

        # Filter out None values
        valid_items = [item for item in items if item is not None]

        if not valid_items:
            return "(list)"  # Empty list

        elements = " ".join(str(item) for item in valid_items)
        return f"(list {elements})"

    def list_index(self, items):
        # list_index: IDENTIFIER "[" expression "]"
        # items: [identifier, index_expression]
        # Note: This handles both list indexing and map access
        # For now, we'll use element-at (list operation)
        # In a more sophisticated implementation, we'd need type information
        container_name = items[0]
        key = items[1]
        return f"(element-at {container_name} {key})"

    def tuple_literal(self, items):
        # tuple_literal: "{" [tuple_field ("," tuple_field)*] "}"
        # items: [field1, field2, field3, ...] where each field is [name, value]

        if not items:
            return "(tuple)"  # Empty tuple

        # Filter out None values
        valid_fields = [field for field in items if field is not None]

        if not valid_fields:
            return "(tuple)"  # Empty tuple

        field_pairs = []
        for field in valid_fields:
            if isinstance(field, list) and len(field) == 2:
                name, value = field
                field_pairs.append(f"({name} {value})")

        fields_str = " ".join(field_pairs)
        return f"(tuple {fields_str})"

    def tuple_field(self, items):
        # tuple_field: IDENTIFIER ":" expression
        # items: [identifier, expression]
        return [items[0], items[1]]

    def tuple_access(self, items):
        # tuple_access: IDENTIFIER "." IDENTIFIER
        # items: [tuple_name, field_name]
        tuple_name = items[0]
        field_name = items[1]
        return f"(get {field_name} {tuple_name})"

    def map_declaration(self, items):
        # map_declaration: MAP IDENTIFIER "<" type "," type ">" ";"
        # items: [MAP_token, map_name, key_type, value_type]

        # Skip the MAP token (first item)
        map_name = items[1]
        key_type = items[2]
        value_type = items[3]

        return f"(define-map {map_name} {key_type} {value_type})"

    def map_operation(self, items):
        # map_operation: map_insert | map_update | map_delete
        # items: [operation_result]
        return items[0]

    def map_insert(self, items):
        # map_insert: IDENTIFIER ".insert" "(" expression "," expression ")" ";"
        # items: [map_name, key, value]
        map_name = items[0]
        key = items[1]
        value = items[2]
        return f"(map-insert {map_name} {key} {value})"

    def map_update(self, items):
        # map_update: IDENTIFIER ".update" "(" expression "," expression ")" ";"
        # items: [map_name, key, value]
        map_name = items[0]
        key = items[1]
        value = items[2]
        return f"(map-set {map_name} {key} {value})"

    def map_delete(self, items):
        # map_delete: IDENTIFIER ".delete" "(" expression ")" ";"
        # items: [map_name, key]
        map_name = items[0]
        key = items[1]
        return f"(map-delete {map_name} {key})"

    def import_statement(self, items):
        # import_statement: "import" "{" import_list "}" "from" STRING ";"
        # items: [import_list, module_name]
        import_list = items[0]
        module_name = items[1]

        # For basic module system, just generate a comment
        imports = ", ".join(import_list) if isinstance(import_list, list) else str(import_list)
        return f";; Import {imports} from {module_name}"

    def import_list(self, items):
        # import_list: IDENTIFIER ("," IDENTIFIER)*
        # items: [name1, name2, ...]
        return items

    def export_statement(self, items):
        # export_statement: "export" (function_declaration | variable_declaration | constant_declaration | map_declaration)
        # items: [declaration]
        declaration = items[0]

        # For basic module system, add export comment
        return f";; Export\n{declaration}"

    def trait_declaration(self, items):
        # trait_declaration: "trait" IDENTIFIER "{" trait_method* "}"
        # items: [trait_name, method1, method2, ...]

        trait_name = items[0]
        methods = items[1:] if len(items) > 1 else []

        # Generate trait as comments with method signatures
        result = [f";; Trait {trait_name}"]

        for method in methods:
            if method:
                result.append(f";;   {method}")

        return "\n".join(result)

    def trait_method(self, items):
        # trait_method: IDENTIFIER "(" [parameter_list] ")" [":" type] ";"
        # items: [method_name, ...] with optional params and return type

        method_name = items[0]

        # For simplicity, just generate basic method signature
        # A more sophisticated version would parse parameters properly
        return f"{method_name}(...)"

    def some_expression(self, items):
        # some_expression: "some" "(" expression ")"
        # items: [expression]
        value = items[0]
        return f"(some {value})"

    def none_expression(self, items):
        # none_expression: "none" "()"
        # items: []
        return "none"

    def ok_expression(self, items):
        # ok_expression: "ok" "(" expression ")"
        # items: [expression]
        value = items[0]
        return f"(ok {value})"

    def err_expression(self, items):
        # err_expression: "err" "(" expression ")"
        # items: [expression]
        error = items[0]
        return f"(err {error})"

    def lambda_expression(self, items):
        # lambda_expression: lambda_signature "=>" expression
        # items: [signature, expression]

        signature = items[0]
        expression = items[1]

        if not signature or signature == [] or (isinstance(signature, list) and len(signature) == 0):
            return f"(lambda () {expression})"
        else:  # Has parameters
            if isinstance(signature, list):
                # Filter out None values
                valid_params = [p for p in signature if p is not None]
                if not valid_params:
                    return f"(lambda () {expression})"
                param_str = " ".join(str(p) for p in valid_params)
            else:
                param_str = str(signature)
            return f"(lambda ({param_str}) {expression})"

    def lambda_signature(self, items):
        # lambda_signature: "(" [IDENTIFIER ("," IDENTIFIER)*] ")"
        # items: [param1, param2, ...] or []
        return items if items else []


    def infer_type(self, value):
        value_str = str(value)

        # Handle literal values
        if value_str.isdigit():
            return "uint"
        elif value_str.endswith('u') and value_str[:-1].isdigit():
            return "uint"
        elif value_str.startswith('-') and value_str[1:].isdigit():
            return "int"
        elif value_str in ["true", "false"]:
            return "bool"
        elif value_str.startswith('"') and value_str.endswith('"'):
            return "string"
        elif value_str.startswith("'"):
            return "principal"

        # Handle complex expressions
        elif value_str.startswith('(list'):
            return "list"
        elif value_str.startswith('(tuple'):
            return "tuple"
        elif value_str.startswith('(some'):
            return "optional"
        elif value_str == 'none':
            return "optional"
        elif value_str.startswith('(ok') or value_str.startswith('(err'):
            return "response"
        elif value_str.startswith('(lambda'):
            return "function"

        # Handle arithmetic expressions (assume uint for now)
        elif any(op in value_str for op in ['+', '-', '*', '/', 'mod', 'pow']):
            return "uint"

        # Handle comparison expressions
        elif any(op in value_str for op in ['>', '<', '>=', '<=', 'is-eq', 'and', 'or', 'not']):
            return "bool"

        else:
            return "unknown"