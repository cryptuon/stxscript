"""
StxScript Static Analysis and Linting
Provides comprehensive static analysis with best practice checks
"""

import re
from typing import List, Dict, Optional, Set, Union, Any
from lark import Tree, Token, Lark
from lark.visitors import Interpreter
from dataclasses import dataclass
from enum import Enum
import os


class LintSeverity(Enum):
    """Severity levels for lint issues"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class LintIssue:
    """Represents a lint issue found in code"""
    rule: str
    message: str
    severity: LintSeverity
    line: Optional[int] = None
    column: Optional[int] = None
    fix_suggestion: Optional[str] = None
    rule_url: Optional[str] = None

    def __str__(self):
        severity_emoji = {
            LintSeverity.ERROR: "❌",
            LintSeverity.WARNING: "⚠️",
            LintSeverity.INFO: "ℹ️",
            LintSeverity.HINT: "💡"
        }

        result = f"{severity_emoji[self.severity]} {self.severity.value.upper()}: {self.message}"

        if self.line is not None:
            result += f" (line {self.line}"
            if self.column is not None:
                result += f", col {self.column}"
            result += ")"

        if self.fix_suggestion:
            result += f"\n   🔧 Fix: {self.fix_suggestion}"

        if self.rule_url:
            result += f"\n   📖 Rule: {self.rule_url}"

        return result


class LintConfig:
    """Configuration for the linter"""

    def __init__(self, **kwargs):
        # Rule categories
        self.enable_style_rules = kwargs.get('enable_style_rules', True)
        self.enable_complexity_rules = kwargs.get('enable_complexity_rules', True)
        self.enable_security_rules = kwargs.get('enable_security_rules', True)
        self.enable_performance_rules = kwargs.get('enable_performance_rules', True)
        self.enable_clarity_rules = kwargs.get('enable_clarity_rules', True)

        # Specific rule settings
        self.max_function_length = kwargs.get('max_function_length', 50)
        self.max_parameter_count = kwargs.get('max_parameter_count', 5)
        self.max_nested_depth = kwargs.get('max_nested_depth', 4)
        self.max_line_length = kwargs.get('max_line_length', 100)

        # Naming conventions
        self.function_naming = kwargs.get('function_naming', 'snake_case')  # snake_case, camelCase
        self.variable_naming = kwargs.get('variable_naming', 'snake_case')
        self.constant_naming = kwargs.get('constant_naming', 'UPPER_SNAKE_CASE')
        self.type_naming = kwargs.get('type_naming', 'PascalCase')

        # Disabled rules
        self.disabled_rules = set(kwargs.get('disabled_rules', []))

    def is_rule_enabled(self, rule_name: str) -> bool:
        """Check if a specific rule is enabled"""
        return rule_name not in self.disabled_rules


class StxScriptLinter:
    """Main linter class for StxScript code analysis"""

    def __init__(self, config: LintConfig = None):
        self.config = config or LintConfig()
        self.grammar_path = os.path.join(os.path.dirname(__file__), 'working_grammar.lark')

        with open(self.grammar_path, 'r') as f:
            grammar_content = f.read()

        self.parser = Lark(grammar_content, start='start', parser='lalr')
        self.rules = self._initialize_rules()

    def lint(self, source_code: str, file_path: str = None) -> List[LintIssue]:
        """Analyze StxScript code and return lint issues"""
        issues = []

        try:
            # Parse the source code
            tree = self.parser.parse(source_code)

            # Run AST-based analysis
            analyzer = StaticAnalyzer(self.config, source_code, file_path)
            ast_issues = analyzer.analyze(tree)
            issues.extend(ast_issues)

            # Run text-based analysis
            text_issues = self._analyze_text(source_code, file_path)
            issues.extend(text_issues)

        except Exception as e:
            issues.append(LintIssue(
                rule="parse_error",
                message=f"Failed to parse code: {str(e)}",
                severity=LintSeverity.ERROR
            ))

        return sorted(issues, key=lambda x: (x.line or 0, x.severity.value))

    def lint_file(self, file_path: str) -> List[LintIssue]:
        """Lint a StxScript file"""
        with open(file_path, 'r') as f:
            source_code = f.read()

        return self.lint(source_code, file_path)

    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize linting rules"""
        return {
            'naming_conventions': NamingConventionRules(self.config),
            'code_complexity': CodeComplexityRules(self.config),
            'security_checks': SecurityRules(self.config),
            'performance_checks': PerformanceRules(self.config),
            'clarity_best_practices': ClarityRules(self.config),
            'style_guidelines': StyleRules(self.config)
        }

    def _analyze_text(self, source_code: str, file_path: str = None) -> List[LintIssue]:
        """Perform text-based analysis (regex patterns)"""
        issues = []
        lines = source_code.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Check line length
            if len(line) > self.config.max_line_length:
                issues.append(LintIssue(
                    rule="max_line_length",
                    message=f"Line too long ({len(line)}/{self.config.max_line_length})",
                    severity=LintSeverity.WARNING,
                    line=line_num,
                    fix_suggestion="Break long line into multiple lines"
                ))

            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(LintIssue(
                    rule="trailing_whitespace",
                    message="Trailing whitespace found",
                    severity=LintSeverity.INFO,
                    line=line_num,
                    fix_suggestion="Remove trailing whitespace"
                ))

            # Check for tabs vs spaces consistency
            if '\t' in line and '    ' in line:
                issues.append(LintIssue(
                    rule="mixed_indentation",
                    message="Mixed tabs and spaces for indentation",
                    severity=LintSeverity.WARNING,
                    line=line_num,
                    fix_suggestion="Use consistent indentation (tabs or spaces)"
                ))

        return issues


class StaticAnalyzer(Interpreter):
    """AST-based static analyzer"""

    def __init__(self, config: LintConfig, source_code: str, file_path: str = None):
        super().__init__()
        self.config = config
        self.source_code = source_code
        self.file_path = file_path
        self.issues = []
        self.scope_stack = [{}]  # Stack of scopes for variable tracking
        self.function_depth = 0
        self.nested_depth = 0
        self.current_function = None

    def analyze(self, tree: Tree) -> List[LintIssue]:
        """Run analysis on the AST"""
        self.issues = []
        self.visit(tree)
        return self.issues

    def function_declaration(self, tree):
        """Analyze function declarations"""
        self.function_depth += 1
        old_function = self.current_function

        # Extract function information
        func_name = None
        parameters = []
        body = None

        for child in tree.children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                func_name = str(child)
                self.current_function = func_name
            elif hasattr(child, 'data') and child.data == 'parameter_list':
                parameters = self._extract_parameters(child)
            elif hasattr(child, 'data') and child.data == 'block':
                body = child

        # Check function naming convention
        if func_name and self.config.is_rule_enabled("function_naming"):
            self._check_naming_convention(func_name, "function", self._get_line_number(tree))

        # Check parameter count
        if len(parameters) > self.config.max_parameter_count:
            self.issues.append(LintIssue(
                rule="max_parameters",
                message=f"Function has too many parameters ({len(parameters)}/{self.config.max_parameter_count})",
                severity=LintSeverity.WARNING,
                line=self._get_line_number(tree),
                fix_suggestion="Consider using a configuration object or breaking into smaller functions"
            ))

        # Check function length
        if body:
            func_lines = self._count_function_lines(body)
            if func_lines > self.config.max_function_length:
                self.issues.append(LintIssue(
                    rule="max_function_length",
                    message=f"Function is too long ({func_lines}/{self.config.max_function_length} lines)",
                    severity=LintSeverity.WARNING,
                    line=self._get_line_number(tree),
                    fix_suggestion="Break large function into smaller, focused functions"
                ))

        # Analyze function body
        if body:
            self._push_scope()
            # Add parameters to scope
            for param in parameters:
                self.scope_stack[-1][param] = 'parameter'

            self.visit(body)
            self._pop_scope()

        self.function_depth -= 1
        self.current_function = old_function

    def variable_declaration(self, tree):
        """Analyze variable declarations"""
        var_name = None

        for child in tree.children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                var_name = str(child)
                break

        if var_name:
            # Check naming convention
            if self.config.is_rule_enabled("variable_naming"):
                self._check_naming_convention(var_name, "variable", self._get_line_number(tree))

            # Check for shadowing
            if self._is_variable_shadowed(var_name):
                self.issues.append(LintIssue(
                    rule="variable_shadowing",
                    message=f"Variable '{var_name}' shadows outer scope variable",
                    severity=LintSeverity.WARNING,
                    line=self._get_line_number(tree),
                    fix_suggestion="Use a different variable name"
                ))

            # Add to current scope
            self.scope_stack[-1][var_name] = 'variable'

        self.generic_visit(tree)

    def constant_declaration(self, tree):
        """Analyze constant declarations"""
        const_name = None

        for child in tree.children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                const_name = str(child)
                break

        if const_name:
            # Check naming convention for constants
            if self.config.is_rule_enabled("constant_naming"):
                self._check_naming_convention(const_name, "constant", self._get_line_number(tree))

            # Add to current scope
            self.scope_stack[-1][const_name] = 'constant'

        self.generic_visit(tree)

    def if_statement(self, tree):
        """Analyze if statements for nesting depth"""
        self.nested_depth += 1

        if self.nested_depth > self.config.max_nested_depth:
            self.issues.append(LintIssue(
                rule="max_nesting_depth",
                message=f"Nesting depth too high ({self.nested_depth}/{self.config.max_nested_depth})",
                severity=LintSeverity.WARNING,
                line=self._get_line_number(tree),
                fix_suggestion="Consider extracting nested logic into separate functions"
            ))

        self.generic_visit(tree)
        self.nested_depth -= 1

    def map_declaration(self, tree):
        """Analyze map declarations"""
        # Check for potential performance issues with maps
        self.issues.append(LintIssue(
            rule="map_usage_info",
            message="Consider map size limits and gas costs for large maps",
            severity=LintSeverity.INFO,
            line=self._get_line_number(tree),
            fix_suggestion="Document expected map size and implement size limits if needed"
        ))

        self.generic_visit(tree)

    def _check_naming_convention(self, name: str, name_type: str, line: int):
        """Check if name follows naming conventions"""
        convention = getattr(self.config, f"{name_type}_naming", "snake_case")

        is_valid = False
        if convention == "snake_case":
            is_valid = re.match(r'^[a-z][a-z0-9_]*$', name)
        elif convention == "camelCase":
            is_valid = re.match(r'^[a-z][a-zA-Z0-9]*$', name)
        elif convention == "PascalCase":
            is_valid = re.match(r'^[A-Z][a-zA-Z0-9]*$', name)
        elif convention == "UPPER_SNAKE_CASE":
            is_valid = re.match(r'^[A-Z][A-Z0-9_]*$', name)

        if not is_valid:
            self.issues.append(LintIssue(
                rule=f"{name_type}_naming_convention",
                message=f"{name_type.title()} '{name}' should follow {convention} convention",
                severity=LintSeverity.WARNING,
                line=line,
                fix_suggestion=f"Rename to follow {convention} convention"
            ))

    def _extract_parameters(self, param_list: Tree) -> List[str]:
        """Extract parameter names from parameter list"""
        parameters = []
        for child in param_list.children:
            if hasattr(child, 'data') and child.data == 'parameter':
                for param_child in child.children:
                    if isinstance(param_child, Token) and param_child.type == 'IDENTIFIER':
                        parameters.append(str(param_child))
                        break
        return parameters

    def _count_function_lines(self, body: Tree) -> int:
        """Count lines in function body"""
        # Simple implementation - count statements
        statement_count = 0
        for child in body.children:
            if hasattr(child, 'data'):
                statement_count += 1
        return statement_count

    def _push_scope(self):
        """Push new scope onto scope stack"""
        self.scope_stack.append({})

    def _pop_scope(self):
        """Pop scope from scope stack"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def _is_variable_shadowed(self, var_name: str) -> bool:
        """Check if variable shadows outer scope variable"""
        for scope in self.scope_stack[:-1]:
            if var_name in scope:
                return True
        return False

    def _get_line_number(self, tree: Tree) -> int:
        """Extract line number from tree node"""
        # This is a simplified implementation
        # In practice, you'd need to track line numbers through the parser
        return 1  # Placeholder


# Rule implementations
class NamingConventionRules:
    """Naming convention rules"""
    def __init__(self, config: LintConfig):
        self.config = config


class CodeComplexityRules:
    """Code complexity analysis rules"""
    def __init__(self, config: LintConfig):
        self.config = config


class SecurityRules:
    """Security-focused lint rules"""
    def __init__(self, config: LintConfig):
        self.config = config


class PerformanceRules:
    """Performance-focused lint rules"""
    def __init__(self, config: LintConfig):
        self.config = config


class ClarityRules:
    """Clarity blockchain specific rules"""
    def __init__(self, config: LintConfig):
        self.config = config


class StyleRules:
    """Code style rules"""
    def __init__(self, config: LintConfig):
        self.config = config


def lint_stxscript(source_code: str, config: LintConfig = None, file_path: str = None) -> List[LintIssue]:
    """Convenience function to lint StxScript code"""
    linter = StxScriptLinter(config)
    return linter.lint(source_code, file_path)


def lint_file(file_path: str, config: LintConfig = None) -> List[LintIssue]:
    """Convenience function to lint a StxScript file"""
    linter = StxScriptLinter(config)
    return linter.lint_file(file_path)