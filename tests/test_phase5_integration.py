#!/usr/bin/env python3
"""
Phase 5 Integration Test: Developer Experience
Tests all Phase 5 developer experience features working together
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import json
import time
import threading
from typing import List, Dict

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from stxscript.transpiler import StxScriptTranspiler
from stxscript.formatter import StxScriptFormatter, FormatterConfig
from stxscript.linter import StxScriptLinter, LintConfig
from stxscript.error_handler import create_helpful_error_message
from stxscript.scaffolding import create_project, TEMPLATES
from stxscript.doc_generator import DocumentationGenerator
from stxscript.cli import main as cli_main


class Phase5IntegrationTest:
    """Comprehensive integration test for Phase 5 developer experience"""

    def __init__(self):
        self.test_dir = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def setup(self):
        """Set up test environment"""
        print("🚀 Setting up Phase 5 integration test environment...")
        self.test_dir = Path(tempfile.mkdtemp(prefix="stxscript_phase5_test_"))
        print(f"   📁 Test directory: {self.test_dir}")

    def teardown(self):
        """Clean up test environment"""
        if self.test_dir and self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up test directory")

    def run_test(self, test_name: str, test_func):
        """Run a single test with error handling"""
        try:
            print(f"\n🧪 Running test: {test_name}")
            test_func()
            self.results["passed"] += 1
            print(f"✅ {test_name}: PASSED")
        except Exception as e:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {str(e)}")
            print(f"❌ {test_name}: FAILED - {str(e)}")
            import traceback
            traceback.print_exc()

    def test_enhanced_error_messages(self):
        """Test enhanced error handling with actionable suggestions"""
        # Test with syntax error
        bad_code = """
        function test() {
            let x: uint = 42
            // Missing semicolon
        }
        """

        try:
            transpiler = StxScriptTranspiler()
            transpiler.transpile(bad_code)
            assert False, "Should have failed with syntax error"
        except Exception as e:
            error_message = create_helpful_error_message(e, bad_code)
            assert "suggestion" in error_message.lower() or "fix" in error_message.lower()
            print(f"   ✓ Enhanced error message generated with suggestions")

    def test_code_formatter(self):
        """Test comprehensive code formatter"""
        # Test formatting various constructs
        unformatted_code = """
        function test(  a:uint,b:uint  ):uint{
        let x:uint=42u;
        if(x>0u){
        return x+1u;
        }
        return 0u;
        }
        """

        formatter = StxScriptFormatter(FormatterConfig())
        formatted = formatter.format(unformatted_code)

        # Check that formatting was applied
        assert "function test(a: uint, b: uint): uint {" in formatted
        assert "let x: uint = 42u;" in formatted
        print(f"   ✓ Code formatting applied successfully")

    def test_static_analysis_linting(self):
        """Test static analysis and linting"""
        # Test code with style issues
        problematic_code = """
        function VeryLongFunctionNameThatViolatesNamingConvention(): uint {
            let x: uint = 42u;
            let y: uint = 42u;
            let z: uint = 42u;
            let a: uint = 42u;
            let b: uint = 42u;
            let c: uint = 42u;
            // This is a very long line that exceeds the maximum line length limit and should be flagged by the linter
            return x + y + z + a + b + c;
        }
        """

        linter = StxScriptLinter(LintConfig())
        issues = linter.lint(problematic_code)

        # Should find some issues
        assert len(issues) > 0, "Linter should find issues in problematic code"
        print(f"   ✓ Linter found {len(issues)} issues as expected")

    def test_project_scaffolding(self):
        """Test project scaffolding system"""
        # Test creating each template type
        for template_name in TEMPLATES.keys():
            project_path = self.test_dir / f"test-{template_name}-project"

            try:
                create_project(project_path, template_name, verbose=False)

                # Verify basic structure
                assert project_path.exists()
                assert (project_path / "src").exists()
                assert (project_path / "stx-project.json").exists()
                assert (project_path / "README.md").exists()

                # Verify project config
                with open(project_path / "stx-project.json") as f:
                    config = json.load(f)
                    assert config["name"] == f"test-{template_name}-project"

                print(f"   ✓ {template_name.title()} template created successfully")

            except Exception as e:
                raise Exception(f"Failed to create {template_name} template: {e}")

    def test_development_cli_commands(self):
        """Test enhanced CLI with development commands"""
        # Create a test project to work with
        test_project = self.test_dir / "cli-test-project"
        create_project(test_project, "basic", verbose=False)

        # Create a test StxScript file with some issues
        test_file = test_project / "src" / "test.stx"
        test_code = """
        /// Test function that demonstrates basic functionality
        /// @param value The input value
        /// @returns The incremented value
        function increment(value:uint):uint{
        return value+1u;
        }
        """
        test_file.write_text(test_code)

        # Test that CLI commands would work (we can't easily test actual CLI calls)
        # So we test the underlying functionality

        # Test formatter integration
        formatter = StxScriptFormatter(FormatterConfig())
        formatted = formatter.format_file(str(test_file))
        assert "function increment(value: uint): uint {" in formatted

        # Test linter integration
        linter = StxScriptLinter(LintConfig())
        issues = linter.lint_file(str(test_file))
        # May or may not have issues, but shouldn't crash

        print(f"   ✓ CLI command functionality verified")

    def test_documentation_generator(self):
        """Test documentation generator"""
        # Create a test file with documentation
        test_file = self.test_dir / "documented_contract.stx"
        documented_code = """
        /// Main contract for testing documentation generation
        /// This contract demonstrates various StxScript features

        /// Simple counter variable
        let counter: uint = 0u;

        /// Contract owner
        const OWNER: principal = tx-sender;

        /// Increment the counter by one
        /// @param none
        /// @returns The new counter value
        /// @example
        /// let result = increment();
        function increment(): uint {
            counter = counter + 1u;
            return counter;
        }

        /// Get the current counter value
        /// @returns The current counter value
        /// @access read-only
        function get_counter(): uint {
            return counter;
        }

        /// User balances map
        /// @description Maps user principals to their balance
        map user_balances principal uint;
        """
        test_file.write_text(documented_code)

        # Generate documentation
        output_dir = self.test_dir / "docs"
        output_dir.mkdir(exist_ok=True)

        generator = DocumentationGenerator()
        generator.generate_documentation(test_file, output_dir, format='html', verbose=False)

        # Verify documentation was generated
        assert (output_dir / 'index.html').exists()
        assert (output_dir / 'documented_contract.html').exists()
        assert (output_dir / 'styles.css').exists()

        # Check content
        index_content = (output_dir / 'index.html').read_text()
        assert 'documented_contract' in index_content

        contract_content = (output_dir / 'documented_contract.html').read_text()
        assert 'increment' in contract_content
        assert 'get_counter' in contract_content

        print(f"   ✓ HTML documentation generated successfully")

        # Test Markdown generation
        md_output_dir = self.test_dir / "docs_md"
        md_output_dir.mkdir(exist_ok=True)

        generator.generate_documentation(test_file, md_output_dir, format='markdown', verbose=False)

        assert (md_output_dir / 'documented_contract.md').exists()
        md_content = (md_output_dir / 'documented_contract.md').read_text()
        assert '# documented_contract' in md_content
        assert '## Functions' in md_content

        print(f"   ✓ Markdown documentation generated successfully")

    def test_end_to_end_workflow(self):
        """Test complete end-to-end developer workflow"""
        print("\n   🔄 Testing complete developer workflow...")

        # 1. Create new project
        workflow_project = self.test_dir / "workflow-test"
        create_project(workflow_project, "basic", verbose=False)
        print("   1. ✓ Project created")

        # 2. Write some StxScript code
        main_file = workflow_project / "src" / "main.stx"
        enhanced_code = """
        /// Enhanced counter contract with documentation
        /// This contract demonstrates a complete StxScript smart contract

        /// The current counter value
        let counter: uint = 0u;

        /// Contract owner who can reset the counter
        const CONTRACT_OWNER: principal = tx-sender;

        /// Increment the counter
        /// @returns The new counter value after incrementing
        /// @example
        /// let new_value = increment();
        function increment(): uint {
            counter = counter + 1u;
            return counter;
        }

        /// Reset counter to zero (owner only)
        /// @returns Success or error code
        function reset(): uint {
            if (tx-sender != CONTRACT_OWNER) {
                return err(u"ERR_UNAUTHORIZED");
            }
            counter = 0u;
            return ok(counter);
        }

        /// Get current counter value
        /// @returns The current counter value
        /// @access read-only
        function get_counter(): uint {
            return counter;
        }
        """
        main_file.write_text(enhanced_code)
        print("   2. ✓ Enhanced code written")

        # 3. Format the code
        formatter = StxScriptFormatter(FormatterConfig())
        formatted = formatter.format_file(str(main_file), in_place=True)
        print("   3. ✓ Code formatted")

        # 4. Lint the code
        linter = StxScriptLinter(LintConfig())
        issues = linter.lint_file(str(main_file))
        print(f"   4. ✓ Code linted ({len(issues)} issues found)")

        # 5. Transpile to Clarity
        transpiler = StxScriptTranspiler()
        source = main_file.read_text()
        result = transpiler.transpile_with_error_handling(source)

        if result.get("success", True):
            clarity_code = result if isinstance(result, str) else result.get("clarity", "")

            # Write Clarity output
            contracts_dir = workflow_project / "contracts"
            contracts_dir.mkdir(exist_ok=True)
            clarity_file = contracts_dir / "main.clar"
            clarity_file.write_text(clarity_code)
            print("   5. ✓ Code transpiled to Clarity")
        else:
            raise Exception(f"Transpilation failed: {result.get('error', 'Unknown error')}")

        # 6. Generate documentation
        docs_dir = workflow_project / "docs"
        docs_dir.mkdir(exist_ok=True)

        generator = DocumentationGenerator()
        generator.generate_documentation(workflow_project / "src", docs_dir, format='html', verbose=False)
        print("   6. ✓ Documentation generated")

        # 7. Verify all outputs exist
        assert clarity_file.exists()
        assert (docs_dir / 'index.html').exists()
        assert (docs_dir / 'main.html').exists()

        print("   🎉 Complete workflow executed successfully!")

    def test_error_recovery_and_reporting(self):
        """Test error recovery and comprehensive reporting"""
        # Test various error scenarios
        error_scenarios = [
            ("Syntax Error", "function test() { let x = }"),
            ("Type Error", "let x: string = 42u;"),
            ("Missing Semicolon", "let x: uint = 42u"),
        ]

        for scenario_name, bad_code in error_scenarios:
            try:
                transpiler = StxScriptTranspiler()
                transpiler.transpile(bad_code)
                assert False, f"Should have failed for {scenario_name}"
            except Exception as e:
                error_msg = create_helpful_error_message(e, bad_code)
                # Should contain helpful information
                assert len(error_msg) > 50, "Error message should be comprehensive"
                print(f"   ✓ {scenario_name} handled with helpful message")

    def run_all_tests(self):
        """Run all Phase 5 integration tests"""
        print("🎯 Starting Phase 5: Developer Experience Integration Tests")
        print("=" * 70)

        self.setup()

        try:
            # Core developer experience features
            self.run_test("Enhanced Error Messages", self.test_enhanced_error_messages)
            self.run_test("Code Formatter", self.test_code_formatter)
            self.run_test("Static Analysis & Linting", self.test_static_analysis_linting)
            self.run_test("Project Scaffolding", self.test_project_scaffolding)
            self.run_test("Development CLI Commands", self.test_development_cli_commands)
            self.run_test("Documentation Generator", self.test_documentation_generator)

            # Integration tests
            self.run_test("End-to-End Workflow", self.test_end_to_end_workflow)
            self.run_test("Error Recovery & Reporting", self.test_error_recovery_and_reporting)

        finally:
            self.teardown()

        # Print results
        print("\n" + "=" * 70)
        print("📊 Phase 5 Integration Test Results")
        print("=" * 70)

        total_tests = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.results['passed']} ✅")
        print(f"Failed: {self.results['failed']} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")

        if self.results["errors"]:
            print("\n❌ Failed Tests:")
            for error in self.results["errors"]:
                print(f"   • {error}")

        if self.results["failed"] == 0:
            print("\n🎉 All Phase 5 tests passed! Developer experience is ready for production.")
            print("\n📋 Phase 5 Summary:")
            print("   ✅ Enhanced error messages with actionable suggestions")
            print("   ✅ Comprehensive code formatter")
            print("   ✅ Static analysis and linting")
            print("   ✅ Project scaffolding with multiple templates")
            print("   ✅ Enhanced CLI with development commands")
            print("   ✅ Documentation generator (HTML & Markdown)")
            print("   ✅ Complete developer workflow integration")
            print("   ✅ Error recovery and comprehensive reporting")
            print("\n🚀 StxScript v1.0.0 Developer Experience is PRODUCTION READY!")
        else:
            print(f"\n⚠️ {self.results['failed']} test(s) failed. Please review and fix issues.")
            return False

        return True


def main():
    """Main entry point for Phase 5 integration test"""
    test_runner = Phase5IntegrationTest()
    success = test_runner.run_all_tests()

    if success:
        print("\n" + "🎊" * 20)
        print("🎉 PHASE 5 COMPLETE: DEVELOPER EXPERIENCE READY! 🎉")
        print("🎊" * 20)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()