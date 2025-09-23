"""
Enhanced Error Handler for StxScript
Provides detailed error messages with actionable suggestions
"""

import re
from typing import List, Dict, Optional, Tuple
from lark.exceptions import LarkError, UnexpectedToken, UnexpectedCharacters


class StxScriptError:
    def __init__(self, error_type: str, message: str, line: int = None, column: int = None,
                 suggestion: str = None, code_snippet: str = None):
        self.error_type = error_type
        self.message = message
        self.line = line
        self.column = column
        self.suggestion = suggestion
        self.code_snippet = code_snippet

    def __str__(self):
        result = f"❌ {self.error_type}: {self.message}"

        if self.line is not None:
            result += f"\n   📍 Line {self.line}"
            if self.column is not None:
                result += f", Column {self.column}"

        if self.code_snippet:
            result += f"\n   📝 {self.code_snippet}"

        if self.suggestion:
            result += f"\n   💡 Suggestion: {self.suggestion}"

        return result


class EnhancedErrorHandler:
    def __init__(self):
        self.error_patterns = {
            # Common syntax errors
            'missing_semicolon': {
                'pattern': r"Expected.*SEMICOLON",
                'suggestion': "Add a semicolon ';' at the end of the statement"
            },
            'missing_brace': {
                'pattern': r"Expected.*RBRACE",
                'suggestion': "Add a closing brace '}' to match the opening brace"
            },
            'missing_paren': {
                'pattern': r"Expected.*RPAR",
                'suggestion': "Add a closing parenthesis ')' to match the opening parenthesis"
            },
            'unexpected_token': {
                'pattern': r"Unexpected token.*Token\('(\w+)', '(.+?)'\)",
                'suggestion': "Check the syntax around this token"
            },

            # Type-related errors
            'unknown_type': {
                'pattern': r"unknown.*type",
                'suggestion': "Add explicit type annotation or ensure the expression has a determinable type"
            },

            # Function-related errors
            'function_syntax': {
                'pattern': r"function.*declaration",
                'suggestion': "Check function syntax: function name(param: type): returnType { ... }"
            },

            # Map-related errors
            'map_syntax': {
                'pattern': r"map.*declaration",
                'suggestion': "Check map syntax: map name<keyType, valueType>;"
            }
        }

    def enhance_error(self, error: Exception, source_code: str = None) -> StxScriptError:
        """Convert a raw error into an enhanced StxScript error with suggestions"""

        if isinstance(error, UnexpectedToken):
            return self._handle_unexpected_token(error, source_code)
        elif isinstance(error, UnexpectedCharacters):
            return self._handle_unexpected_characters(error, source_code)
        elif isinstance(error, LarkError):
            return self._handle_lark_error(error, source_code)
        else:
            return self._handle_generic_error(error, source_code)

    def _handle_unexpected_token(self, error: UnexpectedToken, source_code: str) -> StxScriptError:
        """Handle UnexpectedToken errors with specific suggestions"""

        line = getattr(error, 'line', None)
        column = getattr(error, 'column', None)

        # Extract the problematic token
        token_match = re.search(r"Token\('(\w+)', '(.+?)'\)", str(error))
        if token_match:
            token_type, token_value = token_match.groups()

            # Provide specific suggestions based on token type
            suggestions = {
                'LBRACE': "You might be missing a closing brace '}' somewhere above this line",
                'RBRACE': "Check for unmatched opening braces '{' or missing semicolons",
                'SEMICOLON': "Add a semicolon ';' to end the previous statement",
                'IDENTIFIER': "Check if this identifier is correctly spelled or declared",
                'INTEGER': "Check if this number is in the right context (use 'u' suffix for unsigned integers)",
                'STRING': "Check string syntax - ensure quotes are properly matched"
            }

            suggestion = suggestions.get(token_type, f"Unexpected {token_type.lower()} '{token_value}' - check the syntax")

            # Get code snippet if available
            code_snippet = self._get_code_snippet(source_code, line) if source_code and line else None

            return StxScriptError(
                error_type="Syntax Error",
                message=f"Unexpected {token_type.lower()} '{token_value}'",
                line=line,
                column=column,
                suggestion=suggestion,
                code_snippet=code_snippet
            )

        return StxScriptError(
            error_type="Syntax Error",
            message=str(error),
            line=line,
            column=column,
            suggestion="Check the syntax around this location"
        )

    def _handle_unexpected_characters(self, error: UnexpectedCharacters, source_code: str) -> StxScriptError:
        """Handle UnexpectedCharacters errors"""

        line = getattr(error, 'line', None)
        column = getattr(error, 'column', None)

        return StxScriptError(
            error_type="Lexical Error",
            message=f"Unexpected character sequence",
            line=line,
            column=column,
            suggestion="Check for invalid characters or typos in identifiers/operators",
            code_snippet=self._get_code_snippet(source_code, line) if source_code and line else None
        )

    def _handle_lark_error(self, error: LarkError, source_code: str) -> StxScriptError:
        """Handle general Lark parsing errors"""

        error_str = str(error)

        # Pattern matching for common error types
        for error_name, pattern_info in self.error_patterns.items():
            if re.search(pattern_info['pattern'], error_str, re.IGNORECASE):
                return StxScriptError(
                    error_type="Parse Error",
                    message=error_str,
                    suggestion=pattern_info['suggestion']
                )

        return StxScriptError(
            error_type="Parse Error",
            message=error_str,
            suggestion="Check the overall syntax structure"
        )

    def _handle_generic_error(self, error: Exception, source_code: str) -> StxScriptError:
        """Handle generic errors"""

        return StxScriptError(
            error_type=type(error).__name__,
            message=str(error),
            suggestion="Please check the documentation or report this issue"
        )

    def _get_code_snippet(self, source_code: str, line_number: int, context_lines: int = 2) -> str:
        """Extract a code snippet around the error location"""

        if not source_code or not line_number:
            return None

        lines = source_code.split('\n')
        if line_number > len(lines):
            return None

        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)

        snippet_lines = []
        for i in range(start, end):
            prefix = ">>>" if i == line_number - 1 else "   "
            snippet_lines.append(f"{prefix} {i + 1:3}: {lines[i]}")

        return '\n'.join(snippet_lines)

    def format_suggestions(self, errors: List[StxScriptError]) -> str:
        """Format multiple errors with helpful suggestions"""

        if not errors:
            return "✅ No errors found!"

        result = [f"Found {len(errors)} error(s):\n"]

        for i, error in enumerate(errors, 1):
            result.append(f"{i}. {error}\n")

        # Add general tips
        if len(errors) > 0:
            result.append("📚 General Tips:")
            result.append("   • Check semicolons at the end of statements")
            result.append("   • Ensure all braces {} and parentheses () are matched")
            result.append("   • Use 'u' suffix for unsigned integers (e.g., 42u)")
            result.append("   • Add explicit type annotations when inference fails")
            result.append("   • Check the StxScript documentation for syntax examples")

        return '\n'.join(result)


def create_helpful_error_message(error: Exception, source_code: str = None) -> str:
    """Create a user-friendly error message with suggestions"""

    handler = EnhancedErrorHandler()
    enhanced_error = handler.enhance_error(error, source_code)

    return str(enhanced_error)