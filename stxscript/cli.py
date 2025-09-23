#!/usr/bin/env python3
"""
StxScript CLI - Command-line interface for transpiling StxScript to Clarity.
"""

import argparse
import sys
import os
import time
import json
from pathlib import Path
from typing import List, Optional, Dict
from .transpiler import StxScriptTranspiler
from .formatter import StxScriptFormatter, FormatterConfig, format_file
from .linter import StxScriptLinter, LintConfig, lint_file
from .error_handler import create_helpful_error_message


def create_main_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="StxScript - Modern TypeScript-inspired language for Stacks blockchain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  stxscript build contract.stx              # Transpile to Clarity
  stxscript fmt src/                        # Format all files in directory
  stxscript lint contract.stx               # Check code quality
  stxscript new my-contract                 # Create new project
  stxscript watch src/                      # Watch for changes

For more information, visit: https://github.com/cryptuon/stxscript
        """.strip()
    )

    parser.add_argument(
        '--version',
        action='version',
        version='StxScript 0.1.0 (Phase 5: Developer Experience)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )

    # Build command (default/legacy behavior)
    build_parser = subparsers.add_parser(
        'build',
        help='Transpile StxScript to Clarity',
        description='Transpile StxScript source code to Clarity smart contracts'
    )
    setup_build_parser(build_parser)

    # Format command
    fmt_parser = subparsers.add_parser(
        'fmt',
        help='Format StxScript code',
        description='Format StxScript code according to style guidelines'
    )
    setup_fmt_parser(fmt_parser)

    # Lint command
    lint_parser = subparsers.add_parser(
        'lint',
        help='Analyze code quality',
        description='Run static analysis and check code quality'
    )
    setup_lint_parser(lint_parser)

    # New project command
    new_parser = subparsers.add_parser(
        'new',
        help='Create new StxScript project',
        description='Create a new StxScript project with scaffolding'
    )
    setup_new_parser(new_parser)

    # Watch command
    watch_parser = subparsers.add_parser(
        'watch',
        help='Watch for file changes',
        description='Watch for file changes and auto-rebuild'
    )
    setup_watch_parser(watch_parser)

    # Check command
    check_parser = subparsers.add_parser(
        'check',
        help='Check syntax and types',
        description='Check syntax and type validity without generating output'
    )
    setup_check_parser(check_parser)

    # Doc command
    doc_parser = subparsers.add_parser(
        'doc',
        help='Generate documentation',
        description='Generate documentation from StxScript code'
    )
    setup_doc_parser(doc_parser)

    return parser


def setup_build_parser(parser: argparse.ArgumentParser):
    """Setup the build command parser."""
    parser.add_argument(
        'input',
        help='Input StxScript file or directory'
    )

    parser.add_argument(
        'output',
        nargs='?',
        help='Output Clarity file or directory (defaults to stdout for single files)'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Check syntax only, don\'t generate output'
    )

    parser.add_argument(
        '--optimize',
        action='store_true',
        help='Enable code optimizations'
    )


def setup_fmt_parser(parser: argparse.ArgumentParser):
    """Setup the format command parser."""
    parser.add_argument(
        'files',
        nargs='+',
        help='Files or directories to format'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if files are formatted (exit 1 if not)'
    )

    parser.add_argument(
        '--diff',
        action='store_true',
        help='Show diff of formatting changes'
    )

    parser.add_argument(
        '--config',
        help='Path to formatter config file'
    )


def setup_lint_parser(parser: argparse.ArgumentParser):
    """Setup the lint command parser."""
    parser.add_argument(
        'files',
        nargs='+',
        help='Files or directories to lint'
    )

    parser.add_argument(
        '--fix',
        action='store_true',
        help='Automatically fix issues where possible'
    )

    parser.add_argument(
        '--config',
        help='Path to linter config file'
    )

    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )


def setup_new_parser(parser: argparse.ArgumentParser):
    """Setup the new project command parser."""
    parser.add_argument(
        'name',
        help='Project name'
    )

    parser.add_argument(
        '--template',
        choices=['basic', 'nft', 'token', 'defi'],
        default='basic',
        help='Project template to use'
    )

    parser.add_argument(
        '--path',
        help='Directory to create project in (defaults to current directory)'
    )


def setup_watch_parser(parser: argparse.ArgumentParser):
    """Setup the watch command parser."""
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Directory to watch (defaults to current directory)'
    )

    parser.add_argument(
        '--output',
        help='Output directory for transpiled files'
    )

    parser.add_argument(
        '--ignore',
        action='append',
        help='Patterns to ignore (can be used multiple times)'
    )


def setup_check_parser(parser: argparse.ArgumentParser):
    """Setup the check command parser."""
    parser.add_argument(
        'files',
        nargs='+',
        help='Files or directories to check'
    )


def setup_doc_parser(parser: argparse.ArgumentParser):
    """Setup the documentation command parser."""
    parser.add_argument(
        'input',
        help='Input StxScript file or directory'
    )

    parser.add_argument(
        '--output',
        default='docs/',
        help='Output directory for documentation'
    )

    parser.add_argument(
        '--format',
        choices=['html', 'markdown'],
        default='html',
        help='Documentation format'
    )


def main():
    """Enhanced main CLI entry point with subcommands."""
    parser = create_main_parser()

    # Handle legacy usage (no subcommand)
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # Check if first argument looks like a file (legacy mode)
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-') and sys.argv[1] not in [
        'build', 'fmt', 'lint', 'new', 'watch', 'check', 'doc'
    ]:
        # Legacy mode - treat as build command
        sys.argv.insert(1, 'build')

    args = parser.parse_args()

    # Route to appropriate command handler
    try:
        if args.command == 'build' or args.command is None:
            handle_build_command(args)
        elif args.command == 'fmt':
            handle_fmt_command(args)
        elif args.command == 'lint':
            handle_lint_command(args)
        elif args.command == 'new':
            handle_new_command(args)
        elif args.command == 'watch':
            handle_watch_command(args)
        elif args.command == 'check':
            handle_check_command(args)
        elif args.command == 'doc':
            handle_doc_command(args)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\nAborted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        if args.verbose:
            raise
        else:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


def handle_build_command(args):
    """Handle the build command."""
    # Handle input
    try:
        if args.input == '-':
            # Read from stdin
            if args.verbose:
                print("Reading from stdin...", file=sys.stderr)
            stx_code = sys.stdin.read()
            input_name = "<stdin>"
        else:
            # Read from file
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Error: File '{args.input}' not found", file=sys.stderr)
                sys.exit(1)

            if args.verbose:
                print(f"Reading from {args.input}...", file=sys.stderr)

            with open(input_path, 'r', encoding='utf-8') as f:
                stx_code = f.read()
            input_name = str(input_path)

    except IOError as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)

    # Transpile
    try:
        transpiler = StxScriptTranspiler()

        if args.verbose:
            print(f"Transpiling {input_name}...", file=sys.stderr)

        result = transpiler.transpile_with_error_handling(stx_code)

        if not result.get("success", True):
            print(result["error"], file=sys.stderr)
            sys.exit(1)

        clarity_code = result if isinstance(result, str) else result.get("clarity", "")

        if args.check:
            if args.verbose:
                print("Syntax check passed!", file=sys.stderr)
            return

    except Exception as e:
        error_message = create_helpful_error_message(e, stx_code)
        print(error_message, file=sys.stderr)
        sys.exit(1)

    # Handle output
    try:
        if args.output:
            # Write to file
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(clarity_code)

            if args.verbose:
                print(f"Generated {args.output}", file=sys.stderr)
        else:
            # Write to stdout
            print(clarity_code, end='')

    except IOError as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)


def handle_fmt_command(args):
    """Handle the format command."""
    try:
        config = FormatterConfig()
        if args.config:
            config = FormatterConfig.from_file(args.config)

        files_to_format = []
        for file_pattern in args.files:
            path = Path(file_pattern)
            if path.is_file() and path.suffix == '.stx':
                files_to_format.append(path)
            elif path.is_dir():
                files_to_format.extend(path.rglob('*.stx'))

        if not files_to_format:
            print("No .stx files found to format", file=sys.stderr)
            return

        formatter = StxScriptFormatter(config)
        changes_made = False

        for file_path in files_to_format:
            try:
                original_content = file_path.read_text(encoding='utf-8')
                formatted_content = formatter.format(original_content)

                if original_content != formatted_content:
                    changes_made = True

                    if args.check:
                        print(f"❌ {file_path} needs formatting")
                    elif args.diff:
                        # TODO: Show diff
                        print(f"📝 {file_path} would be formatted")
                    else:
                        # Write formatted content
                        file_path.write_text(formatted_content, encoding='utf-8')
                        if args.verbose:
                            print(f"✅ Formatted {file_path}")
                else:
                    if args.verbose:
                        print(f"✓ {file_path} already formatted")

            except Exception as e:
                print(f"Error formatting {file_path}: {e}", file=sys.stderr)

        if args.check and changes_made:
            sys.exit(1)

    except Exception as e:
        print(f"Error in format command: {e}", file=sys.stderr)
        sys.exit(1)


def handle_lint_command(args):
    """Handle the lint command."""
    try:
        config = LintConfig()
        if args.config:
            # TODO: Load config from file
            pass

        files_to_lint = []
        for file_pattern in args.files:
            path = Path(file_pattern)
            if path.is_file() and path.suffix == '.stx':
                files_to_lint.append(path)
            elif path.is_dir():
                files_to_lint.extend(path.rglob('*.stx'))

        if not files_to_lint:
            print("No .stx files found to lint", file=sys.stderr)
            return

        all_issues = []

        for file_path in files_to_lint:
            try:
                issues = lint_file(str(file_path), config)
                all_issues.extend(issues)

                if args.format == 'text':
                    if issues:
                        print(f"\n📂 {file_path}:")
                        for issue in issues:
                            print(f"  {issue}")
                    elif args.verbose:
                        print(f"✅ {file_path}: No issues found")

            except Exception as e:
                print(f"Error linting {file_path}: {e}", file=sys.stderr)

        # Summary
        if args.format == 'text':
            error_count = sum(1 for issue in all_issues if issue.severity.value == 'error')
            warning_count = sum(1 for issue in all_issues if issue.severity.value == 'warning')

            print(f"\n📊 Found {len(all_issues)} issues: {error_count} errors, {warning_count} warnings")

            if error_count > 0:
                sys.exit(1)
        elif args.format == 'json':
            # TODO: Implement JSON output
            print(json.dumps([{
                'rule': issue.rule,
                'message': issue.message,
                'severity': issue.severity.value,
                'line': issue.line,
                'column': issue.column
            } for issue in all_issues], indent=2))

    except Exception as e:
        print(f"Error in lint command: {e}", file=sys.stderr)
        sys.exit(1)


def handle_new_command(args):
    """Handle the new project command."""
    from .scaffolding import create_project
    try:
        project_path = Path(args.path) / args.name if args.path else Path(args.name)

        if project_path.exists():
            print(f"Error: Directory '{project_path}' already exists", file=sys.stderr)
            sys.exit(1)

        create_project(project_path, args.template, args.verbose)
        print(f"✅ Created new StxScript project: {project_path}")
        print(f"\nGet started:")
        print(f"  cd {args.name}")
        print(f"  stxscript build src/main.stx")

    except Exception as e:
        print(f"Error creating project: {e}", file=sys.stderr)
        sys.exit(1)


def handle_watch_command(args):
    """Handle the watch command."""
    try:
        from .watcher import start_watcher
        watch_path = Path(args.path)

        if not watch_path.exists():
            print(f"Error: Path '{watch_path}' does not exist", file=sys.stderr)
            sys.exit(1)

        print(f"👁️  Watching {watch_path} for changes...")
        print("Press Ctrl+C to stop")

        start_watcher(
            watch_path=watch_path,
            output_dir=Path(args.output) if args.output else None,
            ignore_patterns=args.ignore or [],
            verbose=args.verbose
        )

    except Exception as e:
        print(f"Error in watch mode: {e}", file=sys.stderr)
        sys.exit(1)


def handle_check_command(args):
    """Handle the check command."""
    try:
        files_to_check = []
        for file_pattern in args.files:
            path = Path(file_pattern)
            if path.is_file() and path.suffix == '.stx':
                files_to_check.append(path)
            elif path.is_dir():
                files_to_check.extend(path.rglob('*.stx'))

        if not files_to_check:
            print("No .stx files found to check", file=sys.stderr)
            return

        transpiler = StxScriptTranspiler()
        all_passed = True

        for file_path in files_to_check:
            try:
                source_code = file_path.read_text(encoding='utf-8')
                result = transpiler.transpile_with_error_handling(source_code)

                if result.get("success", True):
                    if args.verbose:
                        print(f"✅ {file_path}: Check passed")
                else:
                    print(f"❌ {file_path}:")
                    print(result["error"])
                    all_passed = False

            except Exception as e:
                error_message = create_helpful_error_message(e, file_path.read_text())
                print(f"❌ {file_path}:")
                print(error_message)
                all_passed = False

        if not all_passed:
            sys.exit(1)
        else:
            print(f"✅ All {len(files_to_check)} files passed checks")

    except Exception as e:
        print(f"Error in check command: {e}", file=sys.stderr)
        sys.exit(1)


def handle_doc_command(args):
    """Handle the documentation command."""
    try:
        from .doc_generator import generate_documentation

        input_path = Path(args.input)
        output_path = Path(args.output)

        if not input_path.exists():
            print(f"Error: Input path '{input_path}' does not exist", file=sys.stderr)
            sys.exit(1)

        output_path.mkdir(parents=True, exist_ok=True)

        generate_documentation(
            input_path=input_path,
            output_path=output_path,
            format=args.format,
            verbose=args.verbose
        )

        print(f"📚 Generated documentation in {output_path}")

    except Exception as e:
        print(f"Error generating documentation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()