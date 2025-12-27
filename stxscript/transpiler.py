"""
StxScript Transpiler
Transforms StxScript source code into Clarity smart contract code

Pipeline: Source → Parser → AST Builder → AST Nodes → Semantic Analyzer → ClarityGenerator → Clarity
"""

import lark
import os
import sys
import hashlib
from typing import Optional
from .ast_builder import ASTBuilder
from .clarity_generator import ClarityGenerator
from .error_handler import EnhancedErrorHandler, create_helpful_error_message
from .semantic_analyzer import ASTSemanticAnalyzer, SemanticIssue


# Module-level parser cache for performance
_parser_cache: Optional[lark.Lark] = None
_grammar_hash: Optional[str] = None


def _get_cached_parser(grammar_path: str) -> lark.Lark:
    """
    Get or create a cached parser instance.

    Uses module-level caching to avoid re-parsing the grammar
    on every transpiler instantiation.
    """
    global _parser_cache, _grammar_hash

    with open(grammar_path, 'r') as grammar_file:
        grammar = grammar_file.read()

    # Calculate grammar hash to detect changes
    current_hash = hashlib.md5(grammar.encode()).hexdigest()

    # Return cached parser if grammar hasn't changed
    if _parser_cache is not None and _grammar_hash == current_hash:
        return _parser_cache

    # Create new parser with caching enabled
    cache_path = os.path.join(os.path.dirname(grammar_path), '.parser_cache')

    try:
        _parser_cache = lark.Lark(
            grammar,
            start='start',
            parser='lalr',
            propagate_positions=True,
            cache=cache_path  # Enable Lark's built-in cache
        )
    except TypeError:
        # Fallback if cache parameter not supported
        _parser_cache = lark.Lark(
            grammar,
            start='start',
            parser='lalr',
            propagate_positions=True
        )

    _grammar_hash = current_hash
    return _parser_cache


class SemanticError(Exception):
    """Exception raised for semantic analysis errors."""

    def __init__(self, errors: list, source: str = None):
        self.errors = errors
        self.source = source
        super().__init__(self._format_errors())

    def _format_errors(self) -> str:
        """Format errors into a readable message."""
        lines = [f"Semantic analysis found {len(self.errors)} error(s):"]
        for i, error in enumerate(self.errors, 1):
            lines.append(f"  {i}. {error}")
        return "\n".join(lines)


class StxScriptTranspiler:
    """
    Main transpiler class that orchestrates the StxScript to Clarity transformation.

    Pipeline:
    1. Parse source code using Lark LALR parser
    2. Build AST using ASTBuilder transformer
    3. Generate Clarity code using ClarityGenerator
    """

    def __init__(self):
        # Get the directory of this file to locate working_grammar.lark
        current_dir = os.path.dirname(__file__)
        grammar_path = os.path.join(current_dir, 'working_grammar.lark')

        # Use cached parser for performance
        self.parser = _get_cached_parser(grammar_path)

        # AST builder transforms parse tree to AST nodes
        self.ast_builder = ASTBuilder()

        # Semantic analyzer for type checking and validation
        self.semantic_analyzer = ASTSemanticAnalyzer()

        # Code generator transforms AST to Clarity code
        self.generator = ClarityGenerator()

        # Error handler for enhanced error messages
        self.error_handler = EnhancedErrorHandler()

    def transpile(self, source: str) -> str:
        """
        Transpile StxScript source code to Clarity.

        Args:
            source: StxScript source code

        Returns:
            Clarity smart contract code

        Raises:
            Exception: If parsing or generation fails
        """
        try:
            # Step 1: Parse source code to Lark tree
            tree = self.parser.parse(source)

            # Step 2: Build AST from parse tree
            ast = self.ast_builder.transform(tree)

            # Step 3: Semantic analysis (type checking, validation)
            # Reset analyzer for fresh analysis
            self.semantic_analyzer = ASTSemanticAnalyzer()
            errors, warnings = self.semantic_analyzer.analyze(ast)

            # Report warnings to stderr
            for warning in warnings:
                print(f"Warning: {warning}", file=sys.stderr)

            # Fail on errors
            if errors:
                raise SemanticError(errors, source)

            # Step 4: Generate Clarity code from AST
            clarity_code = self.generator.generate(ast)

            return clarity_code

        except SemanticError:
            # Re-raise semantic errors as-is
            raise

        except lark.exceptions.UnexpectedInput as e:
            # Enhanced error for parsing failures
            enhanced_error = self.error_handler.enhance_error(e, source)
            raise Exception(str(enhanced_error)) from e

        except Exception as e:
            # Create enhanced error message for other errors
            enhanced_error = self.error_handler.enhance_error(e, source)
            raise Exception(str(enhanced_error)) from e

    def transpile_with_error_handling(self, source: str) -> dict:
        """
        Transpile with comprehensive error handling and suggestions.

        Args:
            source: StxScript source code

        Returns:
            dict with keys:
                - success: bool indicating if transpilation succeeded
                - clarity: Clarity code (if success)
                - error: Error message (if failure)
                - warnings: List of warnings (always present)
        """
        try:
            clarity_code = self.transpile(source)
            return {"success": True, "clarity": clarity_code, "warnings": []}
        except SemanticError as e:
            return {
                "success": False,
                "error": str(e),
                "errors": e.errors,
                "warnings": []
            }
        except Exception as e:
            error_message = create_helpful_error_message(e, source)
            return {"success": False, "error": error_message, "warnings": []}

    def parse_only(self, source: str):
        """
        Parse source code and return AST without generating Clarity.
        Useful for validation and tooling.

        Args:
            source: StxScript source code

        Returns:
            Program AST node
        """
        tree = self.parser.parse(source)
        return self.ast_builder.transform(tree)
