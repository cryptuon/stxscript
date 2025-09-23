"""
StxScript Code Formatter
Provides automatic code formatting with configurable style options
"""

import re
from typing import List, Dict, Optional, Union
from lark import Lark, Tree, Token
from lark.visitors import Transformer
import os


class FormatterConfig:
    """Configuration options for the StxScript formatter"""

    def __init__(self, **kwargs):
        # Indentation settings
        self.indent_size = kwargs.get('indent_size', 4)
        self.use_tabs = kwargs.get('use_tabs', False)
        self.max_line_length = kwargs.get('max_line_length', 100)

        # Spacing settings
        self.space_before_paren = kwargs.get('space_before_paren', False)
        self.space_after_comma = kwargs.get('space_after_comma', True)
        self.space_around_operators = kwargs.get('space_around_operators', True)
        self.space_before_colon = kwargs.get('space_before_colon', False)
        self.space_after_colon = kwargs.get('space_after_colon', True)

        # Brace and block settings
        self.brace_style = kwargs.get('brace_style', 'same_line')  # 'same_line' or 'new_line'
        self.blank_lines_before_function = kwargs.get('blank_lines_before_function', 2)
        self.blank_lines_before_trait = kwargs.get('blank_lines_before_trait', 2)

        # Statement settings
        self.align_assignments = kwargs.get('align_assignments', False)
        self.sort_imports = kwargs.get('sort_imports', True)

    @classmethod
    def from_file(cls, config_path: str) -> 'FormatterConfig':
        """Load configuration from a file"""
        # TODO: Implement config file loading (JSON/TOML)
        return cls()


class StxScriptFormatter:
    """Main formatter class that handles AST-based code formatting"""

    def __init__(self, config: FormatterConfig = None):
        self.config = config or FormatterConfig()
        self.grammar_path = os.path.join(os.path.dirname(__file__), 'working_grammar.lark')

        with open(self.grammar_path, 'r') as f:
            grammar_content = f.read()

        self.parser = Lark(grammar_content, start='start', parser='lalr')
        self.current_indent = 0
        self.in_function_params = False
        self.pending_blank_lines = 0

    def format(self, source_code: str) -> str:
        """Format StxScript source code"""
        try:
            # Parse the source code into an AST
            tree = self.parser.parse(source_code)

            # Apply formatting transformations
            formatter = FormattingTransformer(self.config)
            formatted_tree = formatter.transform(tree)

            # Convert back to formatted string
            return self._tree_to_string(formatted_tree)

        except Exception as e:
            raise FormatterError(f"Failed to format code: {str(e)}")

    def format_file(self, file_path: str, in_place: bool = False) -> str:
        """Format a StxScript file"""
        with open(file_path, 'r') as f:
            source_code = f.read()

        formatted_code = self.format(source_code)

        if in_place:
            with open(file_path, 'w') as f:
                f.write(formatted_code)

        return formatted_code

    def _tree_to_string(self, tree: Tree) -> str:
        """Convert formatted AST back to string representation"""
        formatter = StringFormatter(self.config)
        return formatter.format_tree(tree)


class FormattingTransformer(Transformer):
    """AST transformer that applies formatting rules"""

    def __init__(self, config: FormatterConfig):
        super().__init__()
        self.config = config

    def start(self, items):
        """Format the root of the program"""
        formatted_items = []

        for i, item in enumerate(items):
            # Add blank lines before functions and traits
            if self._is_function_or_trait(item):
                if i > 0:  # Not the first item
                    formatted_items.append(BlankLines(self.config.blank_lines_before_function))

            formatted_items.append(item)

        return Tree('start', formatted_items)

    def function_declaration(self, items):
        """Format function declarations"""
        decorators, function_keyword, name, params, return_type, body = self._extract_function_parts(items)

        # Format the function signature
        formatted_items = []

        if decorators:
            formatted_items.extend(decorators)

        formatted_items.extend([function_keyword, name])

        # Format parameters
        if params:
            formatted_items.append(FormattedParamList(params, self.config))
        else:
            formatted_items.append(Token('LPAR', '('))
            formatted_items.append(Token('RPAR', ')'))

        # Format return type
        if return_type:
            formatted_items.extend(return_type)

        # Format body
        formatted_items.append(FormattedBlock(body, self.config))

        return Tree('function_declaration', formatted_items)

    def variable_declaration(self, items):
        """Format variable declarations"""
        return Tree('variable_declaration', self._format_statement(items))

    def assignment_statement(self, items):
        """Format assignment statements"""
        return Tree('assignment_statement', self._format_statement(items))

    def if_statement(self, items):
        """Format if statements"""
        return Tree('if_statement', self._format_control_flow(items))

    def expression(self, items):
        """Format expressions with proper spacing"""
        return Tree('expression', self._format_expression(items))

    def _extract_function_parts(self, items):
        """Extract parts of a function declaration for formatting"""
        decorators = []
        function_keyword = None
        name = None
        params = None
        return_type = None
        body = None

        i = 0
        # Extract decorators
        while i < len(items) and hasattr(items[i], 'data') and items[i].data == 'decorator':
            decorators.append(items[i])
            i += 1

        # Extract function keyword and name
        if i < len(items) and items[i] == 'function':
            function_keyword = items[i]
            i += 1

        if i < len(items) and isinstance(items[i], Token):
            name = items[i]
            i += 1

        # Extract parameters and return type
        while i < len(items):
            if hasattr(items[i], 'data') and items[i].data == 'parameter_list':
                params = items[i]
            elif hasattr(items[i], 'data') and items[i].data == 'block':
                body = items[i]
                break
            i += 1

        return decorators, function_keyword, name, params, return_type, body

    def _format_statement(self, items):
        """Apply general statement formatting"""
        formatted = []

        for i, item in enumerate(items):
            if isinstance(item, Token):
                # Add spacing around operators
                if item.type in ['ASSIGN', 'EQ_OP', 'COMP_OP', 'ADD_OP', 'MUL_OP'] and self.config.space_around_operators:
                    if i > 0:
                        formatted.append(SpaceToken())
                    formatted.append(item)
                    if i < len(items) - 1:
                        formatted.append(SpaceToken())
                else:
                    formatted.append(item)
            else:
                formatted.append(item)

        return formatted

    def _format_control_flow(self, items):
        """Format control flow statements"""
        return items  # Basic implementation

    def _format_expression(self, items):
        """Format expressions with proper operator spacing"""
        return items  # Basic implementation

    def _is_function_or_trait(self, item):
        """Check if an item is a function or trait declaration"""
        return (hasattr(item, 'data') and
                item.data in ['function_declaration', 'trait_declaration'])


class StringFormatter:
    """Converts formatted AST back to string with proper indentation and spacing"""

    def __init__(self, config: FormatterConfig):
        self.config = config
        self.indent_level = 0
        self.output = []
        self.current_line = ""
        self.at_line_start = True

    def format_tree(self, tree: Tree) -> str:
        """Convert the entire tree to formatted string"""
        self.output = []
        self.current_line = ""
        self.indent_level = 0
        self.at_line_start = True

        self._format_node(tree)

        # Add final line if needed
        if self.current_line.strip():
            self.output.append(self.current_line)

        # Join lines and clean up
        result = '\n'.join(self.output)

        # Clean up extra blank lines
        result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)

        # Ensure file ends with newline
        if not result.endswith('\n'):
            result += '\n'

        return result

    def _format_node(self, node):
        """Format a single AST node"""
        if isinstance(node, Tree):
            self._format_tree_node(node)
        elif isinstance(node, Token):
            self._format_token(node)
        elif isinstance(node, str):
            self._add_text(node)
        elif isinstance(node, (SpaceToken, BlankLines, FormattedParamList, FormattedBlock)):
            self._format_special_node(node)

    def _format_tree_node(self, tree: Tree):
        """Format a tree node based on its type"""
        if tree.data == 'start':
            for child in tree.children:
                self._format_node(child)

        elif tree.data == 'function_declaration':
            self._format_function(tree)

        elif tree.data == 'block':
            self._format_block(tree)

        elif tree.data in ['variable_declaration', 'assignment_statement']:
            self._format_statement(tree)

        else:
            # Default: format all children
            for child in tree.children:
                self._format_node(child)

    def _format_function(self, tree: Tree):
        """Format a function declaration"""
        for child in tree.children:
            self._format_node(child)

    def _format_block(self, tree: Tree):
        """Format a code block with proper indentation"""
        self._add_text(' {')
        self._new_line()
        self._increase_indent()

        for child in tree.children:
            self._format_node(child)

        self._decrease_indent()
        self._add_indented_text('}')
        self._new_line()

    def _format_statement(self, tree: Tree):
        """Format a statement"""
        for child in tree.children:
            self._format_node(child)
        self._new_line()

    def _format_token(self, token: Token):
        """Format a single token"""
        if token.type == 'SEMICOLON':
            self._add_text(';')
        elif token.type in ['LBRACE', 'RBRACE']:
            # Handled by block formatting
            pass
        else:
            self._add_text(str(token))

    def _format_special_node(self, node):
        """Format special formatting nodes"""
        if isinstance(node, SpaceToken):
            self._add_text(' ')
        elif isinstance(node, BlankLines):
            for _ in range(node.count):
                self._new_line()
        elif isinstance(node, FormattedParamList):
            self._format_param_list(node)
        elif isinstance(node, FormattedBlock):
            self._format_node(node.block)

    def _format_param_list(self, param_list):
        """Format function parameter list"""
        self._add_text('(')
        # TODO: Implement parameter formatting
        self._add_text(')')

    def _add_text(self, text: str):
        """Add text to current line"""
        if self.at_line_start and text.strip():
            self.current_line = self._get_indent() + text
            self.at_line_start = False
        else:
            self.current_line += text

    def _add_indented_text(self, text: str):
        """Add indented text (forces new line first)"""
        if not self.at_line_start:
            self._new_line()
        self._add_text(text)

    def _new_line(self):
        """Start a new line"""
        if self.current_line.strip() or not self.output:
            self.output.append(self.current_line)
        self.current_line = ""
        self.at_line_start = True

    def _increase_indent(self):
        """Increase indentation level"""
        self.indent_level += 1

    def _decrease_indent(self):
        """Decrease indentation level"""
        self.indent_level = max(0, self.indent_level - 1)

    def _get_indent(self) -> str:
        """Get current indentation string"""
        if self.config.use_tabs:
            return '\t' * self.indent_level
        else:
            return ' ' * (self.indent_level * self.config.indent_size)


# Special formatting nodes
class SpaceToken:
    """Represents a space in the formatted output"""
    pass


class BlankLines:
    """Represents blank lines in the formatted output"""
    def __init__(self, count: int):
        self.count = count


class FormattedParamList:
    """Represents a formatted parameter list"""
    def __init__(self, params, config: FormatterConfig):
        self.params = params
        self.config = config


class FormattedBlock:
    """Represents a formatted code block"""
    def __init__(self, block, config: FormatterConfig):
        self.block = block
        self.config = config


class FormatterError(Exception):
    """Exception raised when formatting fails"""
    pass


def format_stxscript(source_code: str, config: FormatterConfig = None) -> str:
    """Convenience function to format StxScript code"""
    formatter = StxScriptFormatter(config)
    return formatter.format(source_code)


def format_file(file_path: str, config: FormatterConfig = None, in_place: bool = False) -> str:
    """Convenience function to format a StxScript file"""
    formatter = StxScriptFormatter(config)
    return formatter.format_file(file_path, in_place)