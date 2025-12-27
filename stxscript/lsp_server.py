"""
StxScript Language Server Protocol (LSP) Implementation

Provides IDE features for StxScript:
- Diagnostics (errors and warnings)
- Hover information
- Code completion
- Go to definition
- Document symbols
"""

import re
import logging
from typing import List, Optional, Dict, Any

from lsprotocol import types as lsp
from pygls.server import LanguageServer
from pygls.workspace import TextDocument

from .transpiler import StxScriptTranspiler, SemanticError
from .semantic_analyzer import ASTSemanticAnalyzer, SymbolInfo
from .ast_nodes import (
    Program, FunctionDeclaration, VariableDeclaration, ConstantDeclaration,
    MapDeclaration, TraitDeclaration, TypeAliasDeclaration, Parameter
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create language server instance
server = LanguageServer("stxscript-lsp", "v0.3.0")

# Cache for parsed documents
document_cache: Dict[str, Dict[str, Any]] = {}

# StxScript keywords for completion
KEYWORDS = [
    "let", "const", "function", "if", "else", "return", "match",
    "for", "while", "import", "export", "from", "type", "trait",
    "map", "class", "implements", "true", "false", "some", "none",
    "ok", "err", "try", "unwrap"
]

# StxScript types for completion
TYPES = [
    "int", "uint", "bool", "boolean", "string", "principal",
    "buffer", "list", "optional", "Response", "Map"
]

# StxScript decorators
DECORATORS = ["@public", "@readonly", "@private"]

# Built-in functions
BUILTINS = [
    "print", "assert", "unwrap!", "unwrap-err!", "unwrap-panic",
    "map-get?", "map-set", "map-insert", "map-delete",
    "var-get", "var-set", "contract-call?", "as-contract",
    "tx-sender", "block-height", "stx-get-balance", "stx-transfer?"
]


def get_transpiler() -> StxScriptTranspiler:
    """Get or create transpiler instance."""
    return StxScriptTranspiler()


def analyze_document(uri: str, source: str) -> Dict[str, Any]:
    """Analyze a document and cache the results."""
    transpiler = get_transpiler()
    result = {
        "uri": uri,
        "source": source,
        "ast": None,
        "errors": [],
        "warnings": [],
        "symbols": {}
    }

    try:
        # Parse and analyze
        ast = transpiler.parse_only(source)
        result["ast"] = ast

        # Run semantic analysis
        analyzer = ASTSemanticAnalyzer()
        errors, warnings = analyzer.analyze(ast)
        result["errors"] = errors
        result["warnings"] = warnings
        result["symbols"] = extract_symbols(ast)

    except SemanticError as e:
        result["errors"] = e.errors
    except Exception as e:
        # Parse error
        result["errors"] = [str(e)]

    document_cache[uri] = result
    return result


def extract_symbols(ast: Program) -> Dict[str, SymbolInfo]:
    """Extract symbol information from AST."""
    symbols = {}

    for stmt in ast.statements:
        if isinstance(stmt, FunctionDeclaration):
            symbols[stmt.name] = SymbolInfo(
                name=stmt.name,
                kind="function",
                data_type=stmt.return_type,
                location=stmt.location,
                parameters=[
                    SymbolInfo(name=p.name, kind="parameter", data_type=p.param_type)
                    for p in stmt.parameters
                ],
                return_type=stmt.return_type,
                decorators=stmt.decorators
            )
        elif isinstance(stmt, VariableDeclaration):
            symbols[stmt.name] = SymbolInfo(
                name=stmt.name,
                kind="variable",
                data_type=stmt.var_type,
                location=stmt.location,
                is_mutable=True
            )
        elif isinstance(stmt, ConstantDeclaration):
            symbols[stmt.name] = SymbolInfo(
                name=stmt.name,
                kind="constant",
                data_type=stmt.const_type,
                location=stmt.location,
                is_mutable=False
            )
        elif isinstance(stmt, MapDeclaration):
            symbols[stmt.name] = SymbolInfo(
                name=stmt.name,
                kind="map",
                data_type=None,
                location=stmt.location
            )
        elif isinstance(stmt, TraitDeclaration):
            symbols[stmt.name] = SymbolInfo(
                name=stmt.name,
                kind="trait",
                data_type=None,
                location=stmt.location
            )
        elif isinstance(stmt, TypeAliasDeclaration):
            symbols[stmt.name] = SymbolInfo(
                name=stmt.name,
                kind="type_alias",
                data_type=stmt.target_type,
                location=stmt.location
            )

    return symbols


@server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def did_open(params: lsp.DidOpenTextDocumentParams):
    """Handle document open."""
    uri = params.text_document.uri
    source = params.text_document.text
    result = analyze_document(uri, source)
    publish_diagnostics(uri, result)


@server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
def did_change(params: lsp.DidChangeTextDocumentParams):
    """Handle document change."""
    uri = params.text_document.uri
    # Get the full text from changes
    for change in params.content_changes:
        if isinstance(change, lsp.TextDocumentContentChangeEvent_Type1):
            source = change.text
            result = analyze_document(uri, source)
            publish_diagnostics(uri, result)
            break


@server.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
def did_save(params: lsp.DidSaveTextDocumentParams):
    """Handle document save."""
    uri = params.text_document.uri
    if uri in document_cache:
        # Re-analyze on save
        doc = server.workspace.get_text_document(uri)
        result = analyze_document(uri, doc.source)
        publish_diagnostics(uri, result)


def publish_diagnostics(uri: str, result: Dict[str, Any]):
    """Publish diagnostics to the client."""
    diagnostics = []

    for error in result.get("errors", []):
        error_str = str(error)
        # Try to extract line number from error
        line = 0
        col = 0

        # Check if error has location
        if hasattr(error, 'location') and error.location:
            line = error.location.line - 1 if error.location.line else 0
            col = error.location.column - 1 if error.location.column else 0

        diagnostics.append(lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=line, character=col),
                end=lsp.Position(line=line, character=col + 10)
            ),
            message=error_str,
            severity=lsp.DiagnosticSeverity.Error,
            source="stxscript"
        ))

    for warning in result.get("warnings", []):
        warning_str = str(warning)
        line = 0
        col = 0

        if hasattr(warning, 'location') and warning.location:
            line = warning.location.line - 1 if warning.location.line else 0
            col = warning.location.column - 1 if warning.location.column else 0

        diagnostics.append(lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=line, character=col),
                end=lsp.Position(line=line, character=col + 10)
            ),
            message=warning_str,
            severity=lsp.DiagnosticSeverity.Warning,
            source="stxscript"
        ))

    server.publish_diagnostics(uri, diagnostics)


@server.feature(lsp.TEXT_DOCUMENT_COMPLETION)
def completions(params: lsp.CompletionParams) -> lsp.CompletionList:
    """Provide code completion."""
    uri = params.text_document.uri
    position = params.position

    items = []

    # Get document content
    doc = server.workspace.get_text_document(uri)
    lines = doc.source.split('\n')

    if position.line < len(lines):
        line = lines[position.line]
        prefix = line[:position.character]

        # Check if we're after @ for decorators
        if prefix.rstrip().endswith('@'):
            for dec in DECORATORS:
                items.append(lsp.CompletionItem(
                    label=dec[1:],  # Remove @ prefix
                    kind=lsp.CompletionItemKind.Keyword,
                    insert_text=dec[1:],
                    detail="Decorator"
                ))
        else:
            # Add keywords
            for kw in KEYWORDS:
                items.append(lsp.CompletionItem(
                    label=kw,
                    kind=lsp.CompletionItemKind.Keyword,
                    detail="Keyword"
                ))

            # Add types
            for t in TYPES:
                items.append(lsp.CompletionItem(
                    label=t,
                    kind=lsp.CompletionItemKind.TypeParameter,
                    detail="Type"
                ))

            # Add built-in functions
            for fn in BUILTINS:
                items.append(lsp.CompletionItem(
                    label=fn,
                    kind=lsp.CompletionItemKind.Function,
                    detail="Built-in function"
                ))

            # Add symbols from document
            if uri in document_cache:
                symbols = document_cache[uri].get("symbols", {})
                for name, info in symbols.items():
                    kind = lsp.CompletionItemKind.Variable
                    if info.kind == "function":
                        kind = lsp.CompletionItemKind.Function
                    elif info.kind == "constant":
                        kind = lsp.CompletionItemKind.Constant
                    elif info.kind == "type_alias":
                        kind = lsp.CompletionItemKind.TypeParameter
                    elif info.kind == "trait":
                        kind = lsp.CompletionItemKind.Interface

                    items.append(lsp.CompletionItem(
                        label=name,
                        kind=kind,
                        detail=f"{info.kind}: {info.data_type}" if info.data_type else info.kind
                    ))

    return lsp.CompletionList(is_incomplete=False, items=items)


@server.feature(lsp.TEXT_DOCUMENT_HOVER)
def hover(params: lsp.HoverParams) -> Optional[lsp.Hover]:
    """Provide hover information."""
    uri = params.text_document.uri
    position = params.position

    # Get word at position
    doc = server.workspace.get_text_document(uri)
    word = get_word_at_position(doc.source, position)

    if not word:
        return None

    # Check if it's a keyword
    if word in KEYWORDS:
        return lsp.Hover(
            contents=lsp.MarkupContent(
                kind=lsp.MarkupKind.Markdown,
                value=f"**Keyword:** `{word}`"
            )
        )

    # Check if it's a type
    if word in TYPES:
        return lsp.Hover(
            contents=lsp.MarkupContent(
                kind=lsp.MarkupKind.Markdown,
                value=f"**Type:** `{word}`\n\nBuilt-in StxScript type."
            )
        )

    # Check if it's a built-in
    if word in BUILTINS:
        return lsp.Hover(
            contents=lsp.MarkupContent(
                kind=lsp.MarkupKind.Markdown,
                value=f"**Built-in Function:** `{word}`"
            )
        )

    # Check document symbols
    if uri in document_cache:
        symbols = document_cache[uri].get("symbols", {})
        if word in symbols:
            info = symbols[word]
            type_str = str(info.data_type) if info.data_type else "unknown"

            if info.kind == "function":
                params_str = ", ".join(
                    f"{p.name}: {p.data_type}" for p in info.parameters
                ) if info.parameters else ""
                return lsp.Hover(
                    contents=lsp.MarkupContent(
                        kind=lsp.MarkupKind.Markdown,
                        value=f"**Function:** `{word}({params_str}): {type_str}`"
                    )
                )
            else:
                return lsp.Hover(
                    contents=lsp.MarkupContent(
                        kind=lsp.MarkupKind.Markdown,
                        value=f"**{info.kind.title()}:** `{word}: {type_str}`"
                    )
                )

    return None


def get_word_at_position(source: str, position: lsp.Position) -> Optional[str]:
    """Extract the word at a given position."""
    lines = source.split('\n')
    if position.line >= len(lines):
        return None

    line = lines[position.line]
    if position.character >= len(line):
        return None

    # Find word boundaries
    start = position.character
    end = position.character

    while start > 0 and (line[start - 1].isalnum() or line[start - 1] in '_-!?'):
        start -= 1

    while end < len(line) and (line[end].isalnum() or line[end] in '_-!?'):
        end += 1

    if start == end:
        return None

    return line[start:end]


@server.feature(lsp.TEXT_DOCUMENT_DEFINITION)
def goto_definition(params: lsp.DefinitionParams) -> Optional[lsp.Location]:
    """Go to symbol definition."""
    uri = params.text_document.uri
    position = params.position

    doc = server.workspace.get_text_document(uri)
    word = get_word_at_position(doc.source, position)

    if not word:
        return None

    # Check document symbols
    if uri in document_cache:
        symbols = document_cache[uri].get("symbols", {})
        if word in symbols:
            info = symbols[word]
            if info.location:
                return lsp.Location(
                    uri=uri,
                    range=lsp.Range(
                        start=lsp.Position(
                            line=info.location.line - 1 if info.location.line else 0,
                            character=info.location.column - 1 if info.location.column else 0
                        ),
                        end=lsp.Position(
                            line=info.location.line - 1 if info.location.line else 0,
                            character=(info.location.column - 1 if info.location.column else 0) + len(word)
                        )
                    )
                )

    return None


@server.feature(lsp.TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbols(params: lsp.DocumentSymbolParams) -> List[lsp.DocumentSymbol]:
    """Provide document symbols for outline view."""
    uri = params.text_document.uri
    symbols_list = []

    if uri in document_cache:
        symbols = document_cache[uri].get("symbols", {})
        for name, info in symbols.items():
            # Map kind to LSP symbol kind
            kind = lsp.SymbolKind.Variable
            if info.kind == "function":
                kind = lsp.SymbolKind.Function
            elif info.kind == "constant":
                kind = lsp.SymbolKind.Constant
            elif info.kind == "type_alias":
                kind = lsp.SymbolKind.TypeParameter
            elif info.kind == "trait":
                kind = lsp.SymbolKind.Interface
            elif info.kind == "map":
                kind = lsp.SymbolKind.Field

            line = info.location.line - 1 if info.location and info.location.line else 0
            col = info.location.column - 1 if info.location and info.location.column else 0

            symbols_list.append(lsp.DocumentSymbol(
                name=name,
                kind=kind,
                range=lsp.Range(
                    start=lsp.Position(line=line, character=col),
                    end=lsp.Position(line=line, character=col + len(name))
                ),
                selection_range=lsp.Range(
                    start=lsp.Position(line=line, character=col),
                    end=lsp.Position(line=line, character=col + len(name))
                ),
                detail=str(info.data_type) if info.data_type else None
            ))

    return symbols_list


@server.feature(lsp.INITIALIZE)
def initialize(params: lsp.InitializeParams) -> lsp.InitializeResult:
    """Handle initialization."""
    logger.info("StxScript Language Server initializing...")
    return lsp.InitializeResult(
        capabilities=lsp.ServerCapabilities(
            text_document_sync=lsp.TextDocumentSyncOptions(
                open_close=True,
                change=lsp.TextDocumentSyncKind.Full,
                save=lsp.SaveOptions(include_text=True)
            ),
            completion_provider=lsp.CompletionOptions(
                trigger_characters=[".", "@", "<"]
            ),
            hover_provider=True,
            definition_provider=True,
            document_symbol_provider=True
        ),
        server_info=lsp.ServerInfo(
            name="stxscript-lsp",
            version="0.3.0"
        )
    )


def main():
    """Start the language server."""
    logger.info("Starting StxScript Language Server...")
    server.start_io()


if __name__ == "__main__":
    main()
