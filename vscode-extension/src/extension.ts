import * as path from 'path';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    console.log('StxScript extension is now active!');

    // Get the server path from configuration
    const config = vscode.workspace.getConfiguration('stxscript');
    const serverPath = config.get<string>('server.path', 'stxscript-lsp');

    // Server options
    const serverOptions: ServerOptions = {
        command: serverPath,
        args: [],
        transport: TransportKind.stdio
    };

    // Client options
    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'stxscript' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.stx')
        },
        outputChannelName: 'StxScript Language Server'
    };

    // Create and start the language client
    client = new LanguageClient(
        'stxscript',
        'StxScript Language Server',
        serverOptions,
        clientOptions
    );

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('stxscript.transpile', transpileCommand),
        vscode.commands.registerCommand('stxscript.format', formatCommand),
        vscode.commands.registerCommand('stxscript.restartServer', restartServerCommand)
    );

    // Start the client
    client.start().then(() => {
        console.log('StxScript Language Server started');
    }).catch((error) => {
        console.error('Failed to start StxScript Language Server:', error);
        vscode.window.showErrorMessage(
            'Failed to start StxScript Language Server. Make sure stxscript-lsp is installed.'
        );
    });
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

async function transpileCommand() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    if (editor.document.languageId !== 'stxscript') {
        vscode.window.showErrorMessage('Current file is not a StxScript file');
        return;
    }

    const terminal = vscode.window.createTerminal('StxScript');
    const filePath = editor.document.uri.fsPath;
    const outputPath = filePath.replace(/\.stx$/, '.clar');

    terminal.sendText(`stxscript build "${filePath}" "${outputPath}"`);
    terminal.show();
}

async function formatCommand() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }

    if (editor.document.languageId !== 'stxscript') {
        vscode.window.showErrorMessage('Current file is not a StxScript file');
        return;
    }

    // Request formatting through the language server
    await vscode.commands.executeCommand('editor.action.formatDocument');
}

async function restartServerCommand() {
    if (client) {
        await client.stop();
        await client.start();
        vscode.window.showInformationMessage('StxScript Language Server restarted');
    }
}
