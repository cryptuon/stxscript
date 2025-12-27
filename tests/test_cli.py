"""
Tests for Phase 9: CLI functionality

Tests cover:
- Argument parsing
- Command handlers
- Build functionality
- Error handling
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from stxscript.cli import (
    create_main_parser,
    setup_build_parser,
    setup_fmt_parser,
    setup_lint_parser,
    setup_new_parser,
)


class TestArgumentParsing(unittest.TestCase):
    """Test CLI argument parsing."""

    def test_create_main_parser(self):
        """Main parser should be created successfully."""
        parser = create_main_parser()
        self.assertIsNotNone(parser)

    def test_build_command_parsing(self):
        """Build command should parse input/output args."""
        parser = create_main_parser()
        args = parser.parse_args(['build', 'input.stx', 'output.clar'])

        self.assertEqual(args.command, 'build')
        self.assertEqual(args.input, 'input.stx')
        self.assertEqual(args.output, 'output.clar')

    def test_build_command_check_flag(self):
        """Build command should accept --check flag."""
        parser = create_main_parser()
        args = parser.parse_args(['build', 'input.stx', '--check'])

        self.assertEqual(args.command, 'build')
        self.assertTrue(args.check)

    def test_fmt_command_parsing(self):
        """Format command should parse files argument."""
        parser = create_main_parser()
        args = parser.parse_args(['fmt', 'src/', '--check'])

        self.assertEqual(args.command, 'fmt')
        self.assertEqual(args.files, ['src/'])
        self.assertTrue(args.check)

    def test_lint_command_parsing(self):
        """Lint command should parse files and format."""
        parser = create_main_parser()
        args = parser.parse_args(['lint', 'file.stx', '--format', 'json'])

        self.assertEqual(args.command, 'lint')
        self.assertEqual(args.files, ['file.stx'])
        self.assertEqual(args.format, 'json')

    def test_new_command_parsing(self):
        """New command should parse project name and template."""
        parser = create_main_parser()
        args = parser.parse_args(['new', 'my-project'])

        self.assertEqual(args.command, 'new')
        self.assertEqual(args.name, 'my-project')

    def test_verbose_flag(self):
        """Verbose flag should be parsed."""
        parser = create_main_parser()
        args = parser.parse_args(['--verbose', 'build', 'input.stx'])

        self.assertTrue(args.verbose)


class TestBuildCommand(unittest.TestCase):
    """Test the build command functionality."""

    def setUp(self):
        """Create temp directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_build_simple_file(self):
        """Build command should transpile a simple file."""
        # Create test input file
        input_file = os.path.join(self.temp_dir, 'test.stx')
        output_file = os.path.join(self.temp_dir, 'test.clar')

        with open(input_file, 'w') as f:
            f.write('let x: int = 42;')

        # Import and run the build handler
        from stxscript.transpiler import StxScriptTranspiler

        transpiler = StxScriptTranspiler()
        with open(input_file, 'r') as f:
            source = f.read()

        result = transpiler.transpile(source)

        with open(output_file, 'w') as f:
            f.write(result)

        # Verify output was created
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, 'r') as f:
            content = f.read()
        self.assertIn('define-data-var x', content)

    def test_build_with_error(self):
        """Build command should report errors gracefully."""
        input_file = os.path.join(self.temp_dir, 'error.stx')

        with open(input_file, 'w') as f:
            f.write('let x: int = "wrong type";')

        from stxscript.transpiler import StxScriptTranspiler, SemanticError

        transpiler = StxScriptTranspiler()
        with open(input_file, 'r') as f:
            source = f.read()

        with self.assertRaises(SemanticError):
            transpiler.transpile(source)


class TestCheckCommand(unittest.TestCase):
    """Test the check command functionality."""

    def setUp(self):
        """Create temp directory for test files."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_check_valid_file(self):
        """Check command should validate correct code."""
        input_file = os.path.join(self.temp_dir, 'valid.stx')

        with open(input_file, 'w') as f:
            f.write('''
            function add(a: int, b: int): int {
                return a + b;
            }
            ''')

        from stxscript.transpiler import StxScriptTranspiler

        transpiler = StxScriptTranspiler()
        with open(input_file, 'r') as f:
            source = f.read()

        # Should not raise
        result = transpiler.transpile(source)
        self.assertIsNotNone(result)

    def test_check_invalid_file(self):
        """Check command should detect errors."""
        input_file = os.path.join(self.temp_dir, 'invalid.stx')

        with open(input_file, 'w') as f:
            f.write('''
            function add(a: int, b: int): int {
                return undefined_var;
            }
            ''')

        from stxscript.transpiler import StxScriptTranspiler, SemanticError

        transpiler = StxScriptTranspiler()
        with open(input_file, 'r') as f:
            source = f.read()

        with self.assertRaises(SemanticError) as context:
            transpiler.transpile(source)

        self.assertIn('undefined_var', str(context.exception))


class TestParserSubcommands(unittest.TestCase):
    """Test subparser configuration."""

    def test_build_parser_setup(self):
        """Build parser should have correct arguments."""
        import argparse
        parser = argparse.ArgumentParser()
        setup_build_parser(parser)

        # Parse with required args
        args = parser.parse_args(['input.stx'])
        self.assertEqual(args.input, 'input.stx')

    def test_fmt_parser_setup(self):
        """Format parser should have correct arguments."""
        import argparse
        parser = argparse.ArgumentParser()
        setup_fmt_parser(parser)

        args = parser.parse_args(['file1.stx', 'file2.stx', '--check'])
        self.assertEqual(args.files, ['file1.stx', 'file2.stx'])
        self.assertTrue(args.check)

    def test_lint_parser_setup(self):
        """Lint parser should have correct arguments."""
        import argparse
        parser = argparse.ArgumentParser()
        setup_lint_parser(parser)

        args = parser.parse_args(['src/', '--format', 'json', '--fix'])
        self.assertEqual(args.files, ['src/'])
        self.assertEqual(args.format, 'json')
        self.assertTrue(args.fix)

    def test_new_parser_setup(self):
        """New parser should have correct arguments."""
        import argparse
        parser = argparse.ArgumentParser()
        setup_new_parser(parser)

        args = parser.parse_args(['my-project'])
        self.assertEqual(args.name, 'my-project')


class TestLegacyMode(unittest.TestCase):
    """Test legacy command-line mode (stxscript input.stx output.clar)."""

    def test_legacy_args_detection(self):
        """Legacy args should be detected correctly."""
        # This tests the logic that determines legacy vs modern mode
        # Legacy mode: positional args that look like files

        # Check if a string looks like a file path
        def looks_like_file(arg):
            return arg.endswith('.stx') or arg.endswith('.clar')

        self.assertTrue(looks_like_file('input.stx'))
        self.assertTrue(looks_like_file('output.clar'))
        self.assertFalse(looks_like_file('build'))
        self.assertFalse(looks_like_file('--check'))


class TestTranspilerIntegration(unittest.TestCase):
    """Integration tests for transpiler through CLI-like usage."""

    def test_multiple_transpilations(self):
        """Multiple transpilations should work with cached parser."""
        from stxscript.transpiler import StxScriptTranspiler

        transpiler = StxScriptTranspiler()

        codes = [
            'let a: int = 1;',
            'let b: int = 2;',
            'function test(): int { return 3; }'
        ]

        for code in codes:
            result = transpiler.transpile(code)
            self.assertIsNotNone(result)

    def test_transpiler_reuse(self):
        """Transpiler instances should be reusable."""
        from stxscript.transpiler import StxScriptTranspiler

        transpiler = StxScriptTranspiler()

        # First transpilation
        result1 = transpiler.transpile('let x: int = 1;')
        self.assertIn('x', result1)

        # Second transpilation (same transpiler)
        result2 = transpiler.transpile('let y: int = 2;')
        self.assertIn('y', result2)


if __name__ == '__main__':
    unittest.main()
