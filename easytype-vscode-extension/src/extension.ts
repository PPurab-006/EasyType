import * as vscode from 'vscode';
import * as path from 'path';

let terminal: vscode.Terminal | undefined;

export function activate(context: vscode.ExtensionContext) {
    // Command to run the file normally
    let runCommand = vscode.commands.registerCommand('easytype.run', () => {
        runEasyTypeFile(context, false);
    });

    // Command to run with the debug flag
    let runDebugCommand = vscode.commands.registerCommand('easytype.runDebug', () => {
        runEasyTypeFile(context, true);
    });

    context.subscriptions.push(runCommand, runDebugCommand);

    // Setup diagnostics
    const collection = vscode.languages.createDiagnosticCollection('easytype');
    context.subscriptions.push(collection);

    if (vscode.window.activeTextEditor) {
        updateDiagnostics(vscode.window.activeTextEditor.document, collection);
    }

    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument(event => {
            if (event.document.languageId === 'easytype') {
                updateDiagnostics(event.document, collection);
            }
        }),
        vscode.workspace.onDidOpenTextDocument(doc => {
            if (doc.languageId === 'easytype') {
                updateDiagnostics(doc, collection);
            }
        }),
        vscode.workspace.onDidCloseTextDocument(doc => {
            collection.delete(doc.uri);
        })
    );
}

function runEasyTypeFile(context: vscode.ExtensionContext, debug: boolean) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No file currently open.');
        return;
    }

    const document = editor.document;
    if (document.languageId !== 'easytype' && !document.fileName.endsWith('.esy')) {
        vscode.window.showErrorMessage('Not an EasyType file (.esy).');
        return;
    }

    document.save().then(saved => {
        if (!saved) {
            vscode.window.showErrorMessage('Failed to save the file before running.');
            return;
        }

        const filePath = document.fileName;
        const easyTypePyPath = path.join(context.extensionPath, 'easytype.py');

        if (!terminal || terminal.exitStatus !== undefined) {
            terminal = vscode.window.createTerminal('EasyType');
        }

        terminal.show(true);

        const command = `python "${easyTypePyPath}" "${filePath}"${debug ? ' --debug' : ''}`;
        terminal.sendText(command);
    });
}

function updateDiagnostics(document: vscode.TextDocument, collection: vscode.DiagnosticCollection) {
    const diagnostics: vscode.Diagnostic[] = [];
    const text = document.getText();

    // Reserved words that shouldn't be used as variable names
    const reservedWords = [
        'if', 'what-if', 'else', 'repeat', 'times', 'while',
        'equals', 'plus', 'minus', 'times', 'divided-by', 'power', 'remainder', 'percent',
        'more-than', 'less-than', 'and', 'or',
        'type', 'ask', 'list', 'position', 'insert', 'remove', 'size', 'at', 'in', 'from', 'of', 'number', 'decimal'
    ];

    const lines = text.split('\n');

    let inBlockComment = false;

    lines.forEach((lineText, lineIndex) => {
        // Strip block comments for line-level checks to avoid false positives inside comments
        // Simple heuristic: if there are odd number of '*' we might be toggling comment state, but let's just do a naive check.
        let strippedLine = lineText;
        let asteriskCount = (lineText.match(/\*/g) || []).length;

        if (asteriskCount > 0 && asteriskCount % 2 !== 0) {
            // Very naive block comment toggling
            inBlockComment = !inBlockComment;
        }

        if (inBlockComment) {
            return; // Skip diagnostics in block comments
        }

        // Also check if line itself contains a full * comment *
        strippedLine = strippedLine.replace(/\*.*?\*/g, '');

        // 1. Unmatched quotes check
        const quoteCount = (strippedLine.match(/"/g) || []).length;
        if (quoteCount % 2 !== 0) {
            const range = new vscode.Range(lineIndex, 0, lineIndex, lineText.length);
            const diagnostic = new vscode.Diagnostic(range, 'Unmatched quote detected.', vscode.DiagnosticSeverity.Warning);
            diagnostics.push(diagnostic);
        }

        // 2. Keyword misuse as variable (e.g. `type equals 5`)
        const equalsMatch = strippedLine.match(/^\s*([a-zA-Z0-9_\-]+)\s+equals\b/);
        if (equalsMatch) {
            const varName = equalsMatch[1];
            if (reservedWords.includes(varName)) {
                const startIdx = lineText.indexOf(varName);
                if (startIdx !== -1) {
                    const range = new vscode.Range(lineIndex, startIdx, lineIndex, startIdx + varName.length);
                    const diagnostic = new vscode.Diagnostic(range, `'${varName}' is a reserved keyword and shouldn't be used as a variable name.`, vscode.DiagnosticSeverity.Error);
                    diagnostics.push(diagnostic);
                }
            }
        }
    });

    collection.set(document.uri, diagnostics);
}

export function deactivate() {
    if (terminal) {
        terminal.dispose();
    }
}
