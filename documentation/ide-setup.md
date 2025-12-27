# IDE Setup

StxScript provides a full Language Server Protocol (LSP) implementation and VS Code extension for IDE integration.

## VS Code Extension

### Features

- **Syntax Highlighting**: Full TextMate grammar for `.stx` files
- **Diagnostics**: Real-time error and warning reporting
- **Autocomplete**: Keywords, types, built-in functions, symbols
- **Hover Information**: Type information and documentation
- **Go to Definition**: Navigate to function and variable definitions
- **Document Symbols**: Outline view of contract structure
- **Code Snippets**: 20+ snippets for common patterns

### Installation

#### From Source

1. Navigate to the extension directory:
   ```bash
   cd vscode-extension
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Compile:
   ```bash
   npm run compile
   ```

4. Open VS Code in the extension folder:
   ```bash
   code .
   ```

5. Press `F5` to launch a development instance with the extension

#### Configuration

The extension looks for `stxscript-lsp` in your PATH. Configure the path in VS Code settings:

```json
{
  "stxscript.server.path": "/path/to/stxscript-lsp"
}
```

### Commands

| Command | Description |
|---------|-------------|
| `StxScript: Transpile` | Transpile current file to Clarity |
| `StxScript: Format` | Format current file |
| `StxScript: Restart Server` | Restart the language server |

### Snippets

Type these prefixes and press Tab:

| Prefix | Description |
|--------|-------------|
| `pubfn` | Public function |
| `fn` | Private function |
| `rofn` | Read-only function |
| `let` | Variable declaration |
| `const` | Constant declaration |
| `map` | Map declaration |
| `type` | Type alias |
| `trait` | Trait declaration |
| `if` | If statement |
| `ife` | If-else statement |
| `for` | For loop |
| `while` | While loop |
| `match` | Match expression |
| `ok` | Ok response |
| `err` | Error response |
| `some` | Some optional |
| `import` | Import statement |
| `call` | Contract call |
| `transfer` | SIP-010 transfer function |
| `nfttransfer` | SIP-009 NFT transfer function |

## LSP Server

### Running Standalone

```bash
stxscript-lsp
```

Or with Python:

```bash
python -m stxscript.lsp_server
```

### Features

The LSP server provides:

#### Diagnostics

Real-time error reporting as you type:
- Syntax errors with line/column information
- Type errors from semantic analysis
- Warnings for potential issues

#### Completion

Autocomplete suggestions for:
- Keywords (`let`, `const`, `function`, `if`, `match`, etc.)
- Types (`uint`, `int`, `bool`, `string`, `principal`, etc.)
- Built-in functions (`ok`, `err`, `some`, `none`, `map`, `filter`, `fold`)
- Symbols from current document (functions, variables, constants)

#### Hover

Hover over identifiers to see:
- Type information
- Function signatures
- Documentation (from comments)

#### Go to Definition

Navigate to:
- Function declarations
- Variable/constant declarations
- Type alias definitions

#### Document Symbols

See an outline of:
- Functions (public, private, read-only)
- Constants
- Variables
- Type aliases
- Traits

### Protocol Support

The server implements LSP 3.x with:
- `textDocument/didOpen`
- `textDocument/didChange`
- `textDocument/didClose`
- `textDocument/completion`
- `textDocument/hover`
- `textDocument/definition`
- `textDocument/documentSymbol`
- `textDocument/publishDiagnostics`

## Other Editors

### Vim/Neovim

For basic syntax highlighting, add to your config:

```vim
autocmd BufNewFile,BufRead *.stx set filetype=typescript
```

For LSP support, configure your LSP client to use `stxscript-lsp`:

**nvim-lspconfig**:
```lua
local lspconfig = require('lspconfig')
local configs = require('lspconfig.configs')

configs.stxscript = {
  default_config = {
    cmd = { 'stxscript-lsp' },
    filetypes = { 'stxscript' },
    root_dir = lspconfig.util.root_pattern('stxscript.toml', '.git'),
  },
}

lspconfig.stxscript.setup{}
```

**coc.nvim**:
```json
{
  "languageserver": {
    "stxscript": {
      "command": "stxscript-lsp",
      "filetypes": ["stxscript"],
      "rootPatterns": ["stxscript.toml", ".git"]
    }
  }
}
```

### Sublime Text

1. Install the LSP package
2. Add to LSP settings:

```json
{
  "clients": {
    "stxscript": {
      "command": ["stxscript-lsp"],
      "selector": "source.stxscript",
      "enabled": true
    }
  }
}
```

### Emacs

With `lsp-mode`:

```elisp
(require 'lsp-mode)

(add-to-list 'lsp-language-id-configuration
  '(stxscript-mode . "stxscript"))

(lsp-register-client
  (make-lsp-client
    :new-connection (lsp-stdio-connection '("stxscript-lsp"))
    :major-modes '(stxscript-mode)
    :server-id 'stxscript-lsp))
```

## File Associations

Associate `.stx` files with StxScript:

### VS Code

Already configured in the extension.

### System-wide

Add to your shell profile:

```bash
export STXSCRIPT_EXTENSIONS=".stx"
```

## Troubleshooting

### LSP Server Not Starting

1. Check the server is installed:
   ```bash
   which stxscript-lsp
   ```

2. Check Python path:
   ```bash
   python -c "from stxscript.lsp_server import main; print('OK')"
   ```

3. Check VS Code output panel for errors

### No Autocomplete

1. Ensure the file has `.stx` extension
2. Check the language mode in VS Code status bar
3. Restart the language server

### Diagnostics Not Showing

1. Check the file saves properly
2. Look for errors in the Output panel
3. Try restarting VS Code

## Development

### Building the Extension

```bash
cd vscode-extension
npm install
npm run compile
```

### Testing

```bash
npm test
```

### Packaging

```bash
npm run package
```

Creates a `.vsix` file for distribution.
