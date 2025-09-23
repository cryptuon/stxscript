# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Building and Transpilation
```bash
# Basic transpilation (CLI)
poetry run stxscript build input.stx output.clar

# Enhanced CLI commands (Phase 5)
poetry run stxscript build src/           # Transpile directory
poetry run stxscript fmt src/             # Format code
poetry run stxscript lint src/            # Run static analysis
poetry run stxscript check src/           # Syntax validation
poetry run stxscript new my-project       # Create new project
poetry run stxscript watch src/           # Development mode
poetry run stxscript doc src/ --output docs/  # Generate docs

# Legacy compatibility
poetry run stxscript input.stx output.clar
```

### Testing
```bash
# Run unit tests
poetry run python -m pytest tests/test_transpiler.py

# Run integration tests
poetry run python tests/test_phase5_basic.py

# Run all tests
poetry run python tests/run_tests.py

# Run specific test
poetry run python -m pytest tests/test_transpiler.py::TestStxScriptTranspiler::test_variable_declaration

# Run with pytest discovery
poetry run python -m pytest tests/
```

### Code Quality
```bash
# Format Python code
poetry run black stxscript/

# Type checking
poetry run mypy stxscript/

# Linting
poetry run flake8 stxscript/
```

## Architecture Overview

### Core Transpilation Pipeline

StxScript follows a multi-stage transpilation architecture:

1. **Parsing**: Lark-based parser using `working_grammar.lark`
2. **AST Generation**: Parse tree → StxScript AST nodes (`ast_nodes.py`)
3. **Semantic Analysis**: Type checking and validation (`semantic_analyzer.py`)
4. **Code Generation**: AST → Clarity code (`clarity_generator.py`)
5. **Error Handling**: Enhanced error reporting (`error_handler.py`)

### Key Components

#### Transpiler Core (`stxscript/transpiler.py`)
- Main `StxScriptTranspiler` class orchestrates the pipeline
- Uses `StxScriptTransformer` (Lark transformer) for AST conversion
- Integrates semantic analysis and error handling
- `transpile_with_error_handling()` returns structured results with error details

#### Grammar System
- **`working_grammar.lark`**: Production grammar supporting all language features
- **`grammars/simple_grammar.lark`**: Simplified grammar for basic constructs
- **`grammars/grammar.lark`**: Alternative grammar implementation
- **`legacy/`**: Older implementations and development files
- Grammar supports comments (`//`, `///`, `/* */`) and full StxScript syntax

#### Developer Experience Tools (Phase 5)
- **`formatter.py`**: AST-based code formatter with configurable styles
- **`linter.py`**: Static analysis with naming conventions, complexity checks, security rules
- **`scaffolding.py`**: Project templates (basic, NFT, token, DeFi)
- **`watcher.py`**: File watching with auto-rebuild and development server
- **`doc_generator.py`**: Automatic documentation generation (HTML/Markdown)
- **`cli.py`**: Enhanced CLI with subcommands and modern UX

#### AST and Code Generation
- **`ast_nodes.py`**: StxScript AST node definitions
- **`clarity_generator.py`**: Converts AST to Clarity smart contract code
- **`semantic_analyzer.py`**: Type checking, scope analysis, validation

### Language Implementation Phases

The codebase implements StxScript in phases, with Phase 5 (v1.0.0) being production-ready:

- **Phase 1**: Expression system (arithmetic, operators, function bodies)
- **Phase 2**: Control flow (if/else, match expressions, error handling)
- **Phase 3**: Data structures (lists, tuples, maps, optionals)
- **Phase 4**: Advanced features (lambdas, traits, modules, type inference)
- **Phase 5**: Developer experience (formatting, linting, scaffolding, docs)

### Error Handling Strategy

The project uses a comprehensive error handling system:
- `EnhancedErrorHandler` provides actionable error messages with suggestions
- Pattern matching for common syntax errors with fix recommendations
- Line/column information with code snippet highlighting
- Integration with all development tools for consistent error reporting

### CLI Architecture

The CLI supports both legacy and modern usage patterns:
- Legacy: `stxscript input.stx output.clar`
- Modern: `stxscript build|fmt|lint|new|watch|check|doc [args]`
- Automatic detection and routing between modes
- Comprehensive help system and error handling

### Project Templates

The scaffolding system provides multiple project templates:
- **basic**: Simple counter contract with best practices
- **nft**: SIP-009 compliant NFT contract
- **token**: SIP-010 compliant fungible token
- **defi**: AMM/DeFi protocol template

Each template includes complete project structure, documentation, and configuration.

### Testing Strategy

- **Unit tests**: `tests/test_transpiler.py` for core transpilation
- **Integration tests**: `tests/test_phase5_basic.py` for end-to-end workflow
- **Legacy tests**: `tests/test_phase5_integration.py` for comprehensive testing
- **Component tests**: Individual tool testing within integration suite
- Tests validate both successful transpilation and error handling paths

### Dependencies

- **lark**: Grammar parsing and AST generation
- **watchdog**: File system watching for development mode
- **Poetry**: Dependency management and virtual environment
- **pytest**: Testing framework

### Common Development Patterns

When working with the transpiler:
- Grammar changes require updating `working_grammar.lark`
- New AST nodes go in `ast_nodes.py` with corresponding transformer methods
- Error patterns are added to `error_handler.py` with helpful suggestions
- CLI commands are implemented as handlers in `cli.py` with comprehensive error handling
- New project templates are added to `scaffolding.py` with complete file generation