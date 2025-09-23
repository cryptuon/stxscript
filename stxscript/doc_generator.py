"""
StxScript Documentation Generator
Automatically generates documentation from StxScript source code
"""

import re
import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
from lark import Tree, Token, Lark
from lark.visitors import Interpreter

from .transpiler import StxScriptTranspiler


@dataclass
class DocFunction:
    """Represents a documented function"""
    name: str
    parameters: List[Dict[str, str]]
    return_type: Optional[str]
    description: str
    examples: List[str]
    access: str  # 'public', 'read-only', 'private'
    line_number: Optional[int] = None


@dataclass
class DocVariable:
    """Represents a documented variable or constant"""
    name: str
    type: str
    value: Optional[str]
    description: str
    is_constant: bool
    access: str
    line_number: Optional[int] = None


@dataclass
class DocMap:
    """Represents a documented map"""
    name: str
    key_type: str
    value_type: str
    description: str
    line_number: Optional[int] = None


@dataclass
class DocTrait:
    """Represents a documented trait"""
    name: str
    methods: List[DocFunction]
    description: str
    line_number: Optional[int] = None


@dataclass
class DocumentationData:
    """Contains all documentation data for a contract"""
    name: str
    description: str
    functions: List[DocFunction]
    variables: List[DocVariable]
    maps: List[DocMap]
    traits: List[DocTrait]
    source_file: str
    generated_date: str


class DocCommentParser:
    """Parses documentation comments from source code"""

    def __init__(self):
        # Regex patterns for doc comments
        self.doc_comment_pattern = re.compile(r'///(.*?)(?=\n|$)', re.MULTILINE)
        self.multi_doc_comment_pattern = re.compile(r'/\*\*(.*?)\*/', re.DOTALL)

    def parse_doc_comments(self, source_code: str) -> Dict[int, str]:
        """Extract documentation comments mapped to line numbers"""
        doc_comments = {}
        lines = source_code.split('\n')

        current_doc = []
        doc_line_start = None

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Triple slash comments
            if stripped.startswith('///'):
                if doc_line_start is None:
                    doc_line_start = i
                comment_text = stripped[3:].strip()
                current_doc.append(comment_text)

            # Multi-line doc comments
            elif '/**' in line:
                doc_start = line.find('/**')
                doc_end = line.find('*/', doc_start)

                if doc_end != -1:
                    # Single line doc comment
                    comment_text = line[doc_start + 3:doc_end].strip()
                    doc_comments[i] = comment_text
                else:
                    # Multi-line doc comment start
                    if doc_line_start is None:
                        doc_line_start = i
                    comment_text = line[doc_start + 3:].strip()
                    if comment_text:
                        current_doc.append(comment_text)

            elif '*/' in line and doc_line_start is not None:
                # Multi-line doc comment end
                doc_end = line.find('*/')
                comment_text = line[:doc_end].strip()
                if comment_text.startswith('*'):
                    comment_text = comment_text[1:].strip()
                if comment_text:
                    current_doc.append(comment_text)

                # Store the accumulated comment
                if current_doc:
                    doc_comments[doc_line_start] = '\n'.join(current_doc)
                current_doc = []
                doc_line_start = None

            elif doc_line_start is not None and stripped.startswith('*'):
                # Continuation of multi-line doc comment
                comment_text = stripped[1:].strip()
                if comment_text:
                    current_doc.append(comment_text)

            else:
                # Not a doc comment line
                if current_doc and doc_line_start is not None:
                    # Store accumulated doc comment
                    doc_comments[doc_line_start] = '\n'.join(current_doc)
                    current_doc = []
                    doc_line_start = None

        return doc_comments

    def parse_doc_tags(self, doc_text: str) -> Dict[str, Any]:
        """Parse special tags from documentation text"""
        tags = {
            'description': '',
            'parameters': [],
            'returns': '',
            'examples': [],
            'access': 'public',
            'deprecated': False,
            'since': ''
        }

        lines = doc_text.split('\n')
        current_section = 'description'
        description_lines = []

        for line in lines:
            line = line.strip()

            if line.startswith('@param'):
                # @param name type description
                match = re.match(r'@param\s+(\w+)\s+(\w+)\s+(.*)', line)
                if match:
                    param_name, param_type, param_desc = match.groups()
                    tags['parameters'].append({
                        'name': param_name,
                        'type': param_type,
                        'description': param_desc
                    })
                current_section = None

            elif line.startswith('@returns'):
                # @returns type description
                match = re.match(r'@returns\s+(\w+)?\s*(.*)', line)
                if match:
                    return_type, return_desc = match.groups()
                    tags['returns'] = return_desc or ''
                current_section = None

            elif line.startswith('@return'):
                # Alternative @return syntax
                match = re.match(r'@return\s+(\w+)?\s*(.*)', line)
                if match:
                    return_type, return_desc = match.groups()
                    tags['returns'] = return_desc or ''
                current_section = None

            elif line.startswith('@example'):
                current_section = 'example'

            elif line.startswith('@access'):
                # @access public|private|read-only
                match = re.match(r'@access\s+(\w+)', line)
                if match:
                    tags['access'] = match.group(1)
                current_section = None

            elif line.startswith('@deprecated'):
                tags['deprecated'] = True
                current_section = None

            elif line.startswith('@since'):
                match = re.match(r'@since\s+(.*)', line)
                if match:
                    tags['since'] = match.group(1)
                current_section = None

            elif current_section == 'description' and line:
                description_lines.append(line)

            elif current_section == 'example' and line:
                tags['examples'].append(line)

        tags['description'] = ' '.join(description_lines)
        return tags


class StxScriptDocExtractor(Interpreter):
    """Extracts documentation from StxScript AST"""

    def __init__(self, source_code: str, file_path: str):
        super().__init__()
        self.source_code = source_code
        self.file_path = file_path
        self.doc_parser = DocCommentParser()
        self.doc_comments = self.doc_parser.parse_doc_comments(source_code)

        # Documentation data
        self.functions: List[DocFunction] = []
        self.variables: List[DocVariable] = []
        self.maps: List[DocMap] = []
        self.traits: List[DocTrait] = []

    def extract_documentation(self, tree: Tree) -> DocumentationData:
        """Extract all documentation from AST"""
        self.visit(tree)

        # Try to extract contract-level description
        contract_description = ""
        if 1 in self.doc_comments:
            first_comment = self.doc_comments[1]
            tags = self.doc_parser.parse_doc_tags(first_comment)
            contract_description = tags['description']

        contract_name = Path(self.file_path).stem

        return DocumentationData(
            name=contract_name,
            description=contract_description,
            functions=self.functions,
            variables=self.variables,
            maps=self.maps,
            traits=self.traits,
            source_file=self.file_path,
            generated_date=datetime.now().isoformat()
        )

    def function_declaration(self, tree):
        """Extract function documentation"""
        func_name = None
        parameters = []
        return_type = None
        line_number = None

        # Extract function information
        for child in tree.children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                func_name = str(child)
                line_number = getattr(child, 'line', None)
            elif hasattr(child, 'data') and child.data == 'parameter_list':
                parameters = self._extract_parameters(child)
            elif hasattr(child, 'data') and child.data == 'type':
                return_type = self._extract_type(child)

        if func_name:
            # Find associated documentation
            doc_info = self._find_documentation_for_line(line_number)

            doc_function = DocFunction(
                name=func_name,
                parameters=parameters,
                return_type=return_type,
                description=doc_info.get('description', ''),
                examples=doc_info.get('examples', []),
                access=doc_info.get('access', 'public'),
                line_number=line_number
            )

            self.functions.append(doc_function)

        self.generic_visit(tree)

    def variable_declaration(self, tree):
        """Extract variable documentation"""
        var_name = None
        var_type = None
        line_number = None

        for child in tree.children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                var_name = str(child)
                line_number = getattr(child, 'line', None)
            elif hasattr(child, 'data') and child.data == 'type':
                var_type = self._extract_type(child)

        if var_name:
            doc_info = self._find_documentation_for_line(line_number)

            doc_variable = DocVariable(
                name=var_name,
                type=var_type or 'unknown',
                value=None,  # TODO: Extract initial value
                description=doc_info.get('description', ''),
                is_constant=False,
                access=doc_info.get('access', 'private'),
                line_number=line_number
            )

            self.variables.append(doc_variable)

        self.generic_visit(tree)

    def constant_declaration(self, tree):
        """Extract constant documentation"""
        const_name = None
        const_type = None
        line_number = None

        for child in tree.children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                const_name = str(child)
                line_number = getattr(child, 'line', None)
            elif hasattr(child, 'data') and child.data == 'type':
                const_type = self._extract_type(child)

        if const_name:
            doc_info = self._find_documentation_for_line(line_number)

            doc_variable = DocVariable(
                name=const_name,
                type=const_type or 'unknown',
                value=None,  # TODO: Extract value
                description=doc_info.get('description', ''),
                is_constant=True,
                access=doc_info.get('access', 'public'),
                line_number=line_number
            )

            self.variables.append(doc_variable)

        self.generic_visit(tree)

    def map_declaration(self, tree):
        """Extract map documentation"""
        map_name = None
        key_type = None
        value_type = None
        line_number = None

        # Extract map information (simplified)
        for child in tree.children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                map_name = str(child)
                line_number = getattr(child, 'line', None)

        if map_name:
            doc_info = self._find_documentation_for_line(line_number)

            doc_map = DocMap(
                name=map_name,
                key_type=key_type or 'unknown',
                value_type=value_type or 'unknown',
                description=doc_info.get('description', ''),
                line_number=line_number
            )

            self.maps.append(doc_map)

        self.generic_visit(tree)

    def trait_declaration(self, tree):
        """Extract trait documentation"""
        trait_name = None
        methods = []
        line_number = None

        for child in tree.children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                trait_name = str(child)
                line_number = getattr(child, 'line', None)

        if trait_name:
            doc_info = self._find_documentation_for_line(line_number)

            doc_trait = DocTrait(
                name=trait_name,
                methods=methods,  # TODO: Extract trait methods
                description=doc_info.get('description', ''),
                line_number=line_number
            )

            self.traits.append(doc_trait)

        self.generic_visit(tree)

    def _extract_parameters(self, param_list: Tree) -> List[Dict[str, str]]:
        """Extract parameter information from parameter list"""
        parameters = []

        for child in param_list.children:
            if hasattr(child, 'data') and child.data == 'parameter':
                param_name = None
                param_type = None

                for param_child in child.children:
                    if isinstance(param_child, Token) and param_child.type == 'IDENTIFIER':
                        param_name = str(param_child)
                    elif hasattr(param_child, 'data') and param_child.data == 'type':
                        param_type = self._extract_type(param_child)

                if param_name:
                    parameters.append({
                        'name': param_name,
                        'type': param_type or 'unknown',
                        'description': ''
                    })

        return parameters

    def _extract_type(self, type_tree: Tree) -> str:
        """Extract type information from type tree"""
        if type_tree.children:
            return str(type_tree.children[0])
        return 'unknown'

    def _find_documentation_for_line(self, line_number: Optional[int]) -> Dict[str, Any]:
        """Find documentation comment for a given line number"""
        if line_number is None:
            return {}

        # Look for doc comment on the line before or same line
        for check_line in range(max(1, line_number - 5), line_number + 1):
            if check_line in self.doc_comments:
                return self.doc_parser.parse_doc_tags(self.doc_comments[check_line])

        return {}


class DocumentationGenerator:
    """Generates documentation in various formats"""

    def __init__(self):
        self.grammar_path = os.path.join(os.path.dirname(__file__), 'working_grammar.lark')

        with open(self.grammar_path, 'r') as f:
            grammar_content = f.read()

        self.parser = Lark(grammar_content, start='start', parser='lalr')

    def generate_documentation(self,
                             input_path: Path,
                             output_path: Path,
                             format: str = 'html',
                             verbose: bool = False) -> None:
        """Generate documentation for StxScript files"""

        if input_path.is_file():
            files_to_document = [input_path]
        else:
            files_to_document = list(input_path.rglob('*.stx'))

        if not files_to_document:
            raise ValueError("No .stx files found to document")

        documentation_data = []

        for file_path in files_to_document:
            if verbose:
                print(f"📝 Processing {file_path}")

            try:
                source_code = file_path.read_text(encoding='utf-8')
                tree = self.parser.parse(source_code)

                extractor = StxScriptDocExtractor(source_code, str(file_path))
                doc_data = extractor.extract_documentation(tree)
                documentation_data.append(doc_data)

            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")

        # Generate output based on format
        if format == 'html':
            self._generate_html_docs(documentation_data, output_path, verbose)
        elif format == 'markdown':
            self._generate_markdown_docs(documentation_data, output_path, verbose)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_html_docs(self, documentation_data: List[DocumentationData], output_path: Path, verbose: bool) -> None:
        """Generate HTML documentation"""
        # Create main index
        index_content = self._create_html_index(documentation_data)
        (output_path / 'index.html').write_text(index_content)

        # Generate individual contract pages
        for doc_data in documentation_data:
            contract_content = self._create_html_contract_page(doc_data)
            contract_file = output_path / f'{doc_data.name}.html'
            contract_file.write_text(contract_content)

            if verbose:
                print(f"📄 Generated {contract_file}")

        # Copy CSS (basic styling)
        css_content = self._get_default_css()
        (output_path / 'styles.css').write_text(css_content)

    def _generate_markdown_docs(self, documentation_data: List[DocumentationData], output_path: Path, verbose: bool) -> None:
        """Generate Markdown documentation"""
        for doc_data in documentation_data:
            markdown_content = self._create_markdown_contract_page(doc_data)
            markdown_file = output_path / f'{doc_data.name}.md'
            markdown_file.write_text(markdown_content)

            if verbose:
                print(f"📄 Generated {markdown_file}")

    def _create_html_index(self, documentation_data: List[DocumentationData]) -> str:
        """Create HTML index page"""
        contracts_list = '\n'.join([
            f'<li><a href="{doc.name}.html">{doc.name}</a> - {doc.description or "No description"}</li>'
            for doc in documentation_data
        ])

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StxScript Documentation</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>📚 StxScript Documentation</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </header>

    <main>
        <h2>Smart Contracts</h2>
        <ul class="contracts-list">
            {contracts_list}
        </ul>
    </main>

    <footer>
        <p>Generated by StxScript Documentation Generator</p>
    </footer>
</body>
</html>"""

    def _create_html_contract_page(self, doc_data: DocumentationData) -> str:
        """Create HTML page for a single contract"""
        functions_html = self._create_functions_html(doc_data.functions)
        variables_html = self._create_variables_html(doc_data.variables)
        maps_html = self._create_maps_html(doc_data.maps)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_data.name} - StxScript Documentation</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <nav>
        <a href="index.html">← Back to Index</a>
    </nav>

    <header>
        <h1>📄 {doc_data.name}</h1>
        <p>{doc_data.description or 'No description available.'}</p>
        <p><small>Source: {doc_data.source_file}</small></p>
    </header>

    <main>
        {functions_html}
        {variables_html}
        {maps_html}
    </main>
</body>
</html>"""

    def _create_markdown_contract_page(self, doc_data: DocumentationData) -> str:
        """Create Markdown page for a single contract"""
        content = f"""# {doc_data.name}

{doc_data.description or 'No description available.'}

**Source:** `{doc_data.source_file}`
**Generated:** {doc_data.generated_date}

"""

        if doc_data.functions:
            content += "## Functions\n\n"
            for func in doc_data.functions:
                content += self._create_function_markdown(func)

        if doc_data.variables:
            content += "\n## Variables\n\n"
            for var in doc_data.variables:
                content += self._create_variable_markdown(var)

        if doc_data.maps:
            content += "\n## Maps\n\n"
            for map_item in doc_data.maps:
                content += self._create_map_markdown(map_item)

        return content

    def _create_functions_html(self, functions: List[DocFunction]) -> str:
        """Create HTML for functions section"""
        if not functions:
            return ""

        functions_html = "\n".join([
            self._create_function_html(func) for func in functions
        ])

        return f"""
        <section class="functions">
            <h2>🔧 Functions</h2>
            {functions_html}
        </section>
        """

    def _create_function_html(self, func: DocFunction) -> str:
        """Create HTML for a single function"""
        params_html = ", ".join([
            f"<span class='param'>{p['name']}: <span class='type'>{p['type']}</span></span>"
            for p in func.parameters
        ])

        return_html = f" → <span class='type'>{func.return_type}</span>" if func.return_type else ""

        examples_html = ""
        if func.examples:
            examples_html = "<h4>Examples:</h4><pre><code>" + "\n".join(func.examples) + "</code></pre>"

        return f"""
        <div class="function">
            <h3>⚡ {func.name}</h3>
            <p class="signature">
                <code>{func.name}({params_html}){return_html}</code>
                <span class="access {func.access}">{func.access}</span>
            </p>
            <p>{func.description or 'No description available.'}</p>
            {examples_html}
        </div>
        """

    def _create_variables_html(self, variables: List[DocVariable]) -> str:
        """Create HTML for variables section"""
        if not variables:
            return ""

        variables_html = "\n".join([
            f"""
            <div class="variable">
                <h3>📦 {var.name}</h3>
                <p class="type">Type: <span class="type">{var.type}</span></p>
                <p>{var.description or 'No description available.'}</p>
            </div>
            """ for var in variables
        ])

        return f"""
        <section class="variables">
            <h2>📦 Variables</h2>
            {variables_html}
        </section>
        """

    def _create_maps_html(self, maps: List[DocMap]) -> str:
        """Create HTML for maps section"""
        if not maps:
            return ""

        maps_html = "\n".join([
            f"""
            <div class="map">
                <h3>🗺️ {map_item.name}</h3>
                <p class="signature">
                    <code>map {map_item.name}&lt;{map_item.key_type}, {map_item.value_type}&gt;</code>
                </p>
                <p>{map_item.description or 'No description available.'}</p>
            </div>
            """ for map_item in maps
        ])

        return f"""
        <section class="maps">
            <h2>🗺️ Maps</h2>
            {maps_html}
        </section>
        """

    def _create_function_markdown(self, func: DocFunction) -> str:
        """Create Markdown for a single function"""
        params_md = ", ".join([f"{p['name']}: {p['type']}" for p in func.parameters])
        return_md = f" → {func.return_type}" if func.return_type else ""

        content = f"### ⚡ {func.name}\n\n"
        content += f"**Signature:** `{func.name}({params_md}){return_md}` ({func.access})\n\n"
        content += f"{func.description or 'No description available.'}\n\n"

        if func.examples:
            content += "**Examples:**\n```stxscript\n" + "\n".join(func.examples) + "\n```\n\n"

        return content

    def _create_variable_markdown(self, var: DocVariable) -> str:
        """Create Markdown for a single variable"""
        var_type = "constant" if var.is_constant else "variable"
        content = f"### 📦 {var.name}\n\n"
        content += f"**Type:** {var.type} ({var_type})\n\n"
        content += f"{var.description or 'No description available.'}\n\n"
        return content

    def _create_map_markdown(self, map_item: DocMap) -> str:
        """Create Markdown for a single map"""
        content = f"### 🗺️ {map_item.name}\n\n"
        content += f"**Type:** `map<{map_item.key_type}, {map_item.value_type}>`\n\n"
        content += f"{map_item.description or 'No description available.'}\n\n"
        return content

    def _get_default_css(self) -> str:
        """Get default CSS for HTML documentation"""
        return """
/* StxScript Documentation Styles */
* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f8f9fa;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
}

header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2.5rem;
}

nav {
    margin-bottom: 1rem;
}

nav a {
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
}

nav a:hover {
    text-decoration: underline;
}

section {
    background: white;
    padding: 2rem;
    margin-bottom: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.function, .variable, .map {
    border-left: 4px solid #667eea;
    padding-left: 1rem;
    margin-bottom: 2rem;
}

.function h3, .variable h3, .map h3 {
    margin-top: 0;
    color: #667eea;
}

.signature {
    background-color: #f8f9fa;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-family: 'Monaco', 'Consolas', monospace;
    margin: 1rem 0;
}

.type {
    color: #e83e8c;
    font-weight: 500;
}

.param {
    color: #6f42c1;
}

.access {
    font-size: 0.8rem;
    padding: 0.2rem 0.5rem;
    border-radius: 3px;
    text-transform: uppercase;
    font-weight: bold;
}

.access.public {
    background-color: #28a745;
    color: white;
}

.access.private {
    background-color: #dc3545;
    color: white;
}

.access.read-only {
    background-color: #ffc107;
    color: black;
}

pre {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
}

code {
    background-color: #f8f9fa;
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.9rem;
}

.contracts-list {
    list-style: none;
    padding: 0;
}

.contracts-list li {
    background: white;
    margin-bottom: 1rem;
    padding: 1rem;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.contracts-list a {
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
    font-size: 1.1rem;
}

.contracts-list a:hover {
    text-decoration: underline;
}

footer {
    text-align: center;
    color: #6c757d;
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid #dee2e6;
}
"""


def generate_documentation(input_path: Path, output_path: Path, format: str = 'html', verbose: bool = False) -> None:
    """Generate documentation for StxScript files"""
    generator = DocumentationGenerator()
    generator.generate_documentation(input_path, output_path, format, verbose)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python doc_generator.py <input_path> <output_path> [format]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    format = sys.argv[3] if len(sys.argv) > 3 else 'html'

    generate_documentation(input_path, output_path, format, verbose=True)