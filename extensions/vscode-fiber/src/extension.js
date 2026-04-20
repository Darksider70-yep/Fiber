const vscode = require('vscode');
const path = require('path');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Fiber Extension is now active.');

    // Command: Build to EXE
    let buildCmd = vscode.commands.registerCommand('fiber.buildToExe', async function (uri) {
        // Use the URI from context menu, or active editor if none
        let targetUri = uri;
        if (!targetUri && vscode.window.activeTextEditor) {
            targetUri = vscode.window.activeTextEditor.document.uri;
        }

        if (!targetUri) {
            vscode.window.showErrorMessage('Please open a Fiber (.fib) file to build.');
            return;
        }

        const filePath = targetUri.fsPath;
        const fileName = path.basename(filePath);

        // Notify user
        vscode.window.showInformationMessage(`🏗️ Initializing Fiber Build for ${fileName}...`);

        // Create or find a terminal to run the build
        let terminal = vscode.window.terminals.find(t => t.name === "Fiber Build");
        if (!terminal) {
            terminal = vscode.window.createTerminal("Fiber Build");
        }
        
        terminal.show();
        
        // Get the configured path to the fiber executable
        const config = vscode.workspace.getConfiguration('fiber');
        const fiberPath = config.get('path') || 'fiber';

        // Run the builder command
        terminal.sendText(`"${fiberPath}" -b "${filePath}"`);
    });

    context.subscriptions.push(buildCmd);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
