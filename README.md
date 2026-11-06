# Local LM Studio chat for VS Code

This project adds locally served LM Studio models to VS Code's built-in chat
model picker. In Agent Mode, VS Code handles workspace context, file tools,
and its usual approval flow; this extension only connects the chat model to
LM Studio.

## Requirements

- Visual Studio Code 1.104 or newer, with Copilot Chat available.
- The Copilot **Bring Your Own Language Model Key** policy must be enabled.
- [LM Studio](https://lmstudio.ai/) with a model downloaded and loaded.
- A model that supports tool/function calling for Agent Mode.

## Build and install

1. Start the LM Studio local server. Its default OpenAI-compatible API URL is
   `http://localhost:1234/v1`.
2. From the repository root, build a VS Code extension package:

   ```bash
   python3 scripts/package_extension.py
   ```

3. Install `dist/lm-studio-chat.vsix` from VS Code's Extensions view using
   **Install from VSIX...**, or run:

   ```bash
   code --install-extension dist/lm-studio-chat.vsix
   ```

4. Reload VS Code. In a new Chat conversation, select a model under
   **LM Studio**, then select **Agent** mode to enable VS Code's workspace
   tools.

The extension reads and writes files only when VS Code's agent tools do so.
Review tool requests and edits in VS Code as usual. The extension itself does
not access workspace files or run shell commands.

## Configuration

Open Settings and search for `LM Studio Chat` to configure the server URL,
request timeout, temperature, and the model context/output token limits. The
default URL is `http://localhost:1234/v1`.

If LM Studio's server authentication is enabled, run **LM Studio: Set API
Key** from the Command Palette. The key is stored in VS Code Secret Storage;
it is not written to the repository.

Use **LM Studio: Check Server Connection** from the Command Palette to test
the server and list loaded models.

The local model is available in VS Code's chat UI; it does not replace the
model used by this already-running assistant session. Start a new VS Code
chat and select an LM Studio model to use it.
