"use strict";

const vscode = require("vscode");

const SETTINGS_SECTION = "lmStudioChat";
const API_KEY_SECRET = "lmStudioChat.apiKey";
const DEFAULT_BASE_URL = "http://localhost:1234/v1";

function getErrorMessage(error) {
  return error instanceof Error ? error.message : String(error);
}

function readSettings() {
  const config = vscode.workspace.getConfiguration(SETTINGS_SECTION);
  const baseUrl = config.get("baseUrl", DEFAULT_BASE_URL).replace(/\/+$/, "");
  const parsedUrl = new URL(baseUrl);
  if (!["http:", "https:"].includes(parsedUrl.protocol) || parsedUrl.username || parsedUrl.password) {
    throw new Error("LM Studio URL must be an http(s) URL without embedded credentials.");
  }

  const timeoutSeconds = config.get("requestTimeout", 120);
  const temperature = config.get("temperature", 0.7);
  const maxInputTokens = config.get("maxInputTokens", 32768);
  const maxOutputTokens = config.get("maxOutputTokens", 8192);
  if (!Number.isFinite(timeoutSeconds) || timeoutSeconds <= 0) {
    throw new Error("LM Studio request timeout must be greater than zero.");
  }
  if (!Number.isFinite(temperature) || temperature < 0 || temperature > 2) {
    throw new Error("LM Studio temperature must be between 0 and 2.");
  }
  if (!Number.isInteger(maxInputTokens) || maxInputTokens < 1) {
    throw new Error("LM Studio maximum input tokens must be a positive integer.");
  }
  if (!Number.isInteger(maxOutputTokens) || maxOutputTokens < 1) {
    throw new Error("LM Studio maximum output tokens must be a positive integer.");
  }

  return {
    baseUrl,
    timeoutSeconds,
    temperature,
    maxInputTokens,
    maxOutputTokens,
  };
}

function extractText(parts) {
  return parts
    .filter((part) => part instanceof vscode.LanguageModelTextPart)
    .map((part) => part.value)
    .join("");
}

function convertMessages(messages) {
  const converted = [];

  for (const message of messages) {
    const isUser = message.role === vscode.LanguageModelChatMessageRole.User;
    const role = isUser ? "user" : "assistant";
    const text = extractText(message.content);
    const toolCalls = message.content.filter(
      (part) => part instanceof vscode.LanguageModelToolCallPart,
    );
    const toolResults = message.content.filter(
      (part) => part instanceof vscode.LanguageModelToolResultPart,
    );

    if (role === "assistant") {
      const assistantMessage = { role, content: text || null };
      if (toolCalls.length > 0) {
        assistantMessage.tool_calls = toolCalls.map((part) => ({
          id: part.callId,
          type: "function",
          function: {
            name: part.name,
            arguments: JSON.stringify(part.input),
          },
        }));
      }
      if (text || toolCalls.length > 0) {
        converted.push(assistantMessage);
      }
    } else {
      if (text) {
        converted.push({ role, content: text });
      }
      for (const result of toolResults) {
        converted.push({
          role: "tool",
          tool_call_id: result.callId,
          content: extractText(result.content),
        });
      }
    }
  }

  return converted;
}

function parseToolInput(value) {
  let input = value;
  if (typeof input === "string") {
    try {
      input = JSON.parse(input);
    } catch (error) {
      throw new Error(`LM Studio returned invalid tool-call JSON: ${getErrorMessage(error)}`);
    }
  }
  if (input === null || typeof input !== "object" || Array.isArray(input)) {
    throw new Error("LM Studio returned tool-call arguments that are not an object.");
  }
  return input;
}

class LMStudioChatProvider {
  constructor(context) {
    this.context = context;
  }

  async requestJson(method, endpoint, body, token) {
    const settings = readSettings();
    const apiKey = await this.context.secrets.get(API_KEY_SECRET);
    const controller = new AbortController();
    let timedOut = false;
    const timeout = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, settings.timeoutSeconds * 1000);
    const cancellation = token?.onCancellationRequested(() => controller.abort());
    const headers = { Accept: "application/json" };
    if (apiKey) {
      headers.Authorization = `Bearer ${apiKey}`;
    }
    let response;
    let responseText;
    try {
      response = await fetch(`${settings.baseUrl}${endpoint}`, {
        method,
        headers: body === undefined ? headers : { ...headers, "Content-Type": "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller.signal,
      });
      responseText = await response.text();
    } catch (error) {
      if (token?.isCancellationRequested) {
        throw new Error("LM Studio request cancelled.");
      }
      if (timedOut) {
        throw new Error(`LM Studio did not respond within ${settings.timeoutSeconds} seconds.`);
      }
      throw new Error(`Could not connect to LM Studio at ${settings.baseUrl}: ${getErrorMessage(error)}`);
    } finally {
      clearTimeout(timeout);
      cancellation?.dispose();
    }

    if (!response.ok) {
      throw new Error(
        `LM Studio returned HTTP ${response.status}: ${responseText.slice(0, 500) || response.statusText}`,
      );
    }
    try {
      return JSON.parse(responseText);
    } catch (error) {
      throw new Error(`LM Studio returned invalid JSON: ${getErrorMessage(error)}`);
    }
  }

  async discoverModels(token) {
    const result = await this.requestJson("GET", "/models", undefined, token);
    if (!Array.isArray(result.data)) {
      throw new Error("LM Studio returned an invalid model list.");
    }
    return result.data.filter(
      (model) => model && typeof model.id === "string" && model.id.trim().length > 0,
    );
  }

  async provideLanguageModelChatInformation(_options, token) {
    const settings = readSettings();
    const models = await this.discoverModels(token);
    return models.map((model) => ({
      id: model.id,
      name: model.id,
      family: model.id,
      version: "1.0.0",
      tooltip: `Served locally by LM Studio at ${settings.baseUrl}`,
      maxInputTokens: settings.maxInputTokens,
      maxOutputTokens: settings.maxOutputTokens,
      capabilities: {
        toolCalling: true,
        imageInput: false,
      },
    }));
  }

  async provideLanguageModelChatResponse(model, messages, options, progress, token) {
    const settings = readSettings();
    const tools = (options.tools ?? []).map((tool) => ({
      type: "function",
      function: {
        name: tool.name,
        description: tool.description,
        parameters: tool.inputSchema ?? { type: "object", properties: {} },
      },
    }));
    const request = {
      model: model.id,
      messages: convertMessages(messages),
      temperature: settings.temperature,
      max_tokens: settings.maxOutputTokens,
      stream: false,
    };
    if (tools.length > 0) {
      request.tools = tools;
      request.tool_choice = "auto";
    }

    const result = await this.requestJson(
      "POST",
      "/chat/completions",
      request,
      token,
    );
    const choice = result.choices?.[0];
    const responseMessage = choice?.message;
    if (!responseMessage) {
      throw new Error("LM Studio returned no chat completion.");
    }

    if (typeof responseMessage.content === "string" && responseMessage.content.length > 0) {
      progress.report(new vscode.LanguageModelTextPart(responseMessage.content));
    }

    let hasOutput =
      typeof responseMessage.content === "string" &&
      responseMessage.content.length > 0;
    if (Array.isArray(responseMessage.tool_calls)) {
      for (const call of responseMessage.tool_calls) {
        if (
          typeof call.id !== "string" ||
          typeof call.function?.name !== "string"
        ) {
          throw new Error("LM Studio returned an invalid tool call.");
        }
        progress.report(
          new vscode.LanguageModelToolCallPart(
            call.id,
            call.function.name,
            parseToolInput(call.function.arguments),
          ),
        );
        hasOutput = true;
      }
    } else if (typeof responseMessage.content !== "string") {
      throw new Error("LM Studio returned an unsupported chat response.");
    }
    if (!hasOutput) {
      throw new Error("LM Studio returned an empty chat response.");
    }
  }

  async provideTokenCount(_model, value) {
    const text =
      typeof value === "string"
        ? value
        : extractText(value.content ?? []);
    return Math.ceil(text.length / 4);
  }
}

async function checkConnection(provider) {
  try {
    const models = await provider.discoverModels();
    if (models.length === 0) {
      await vscode.window.showWarningMessage(
        "LM Studio is reachable, but no models are loaded.",
      );
      return;
    }
    const names = models.map((model) => model.id).join(", ");
    await vscode.window.showInformationMessage(
      `LM Studio is ready. Loaded models: ${names}`,
    );
  } catch (error) {
    await vscode.window.showErrorMessage(
      `LM Studio connection failed: ${getErrorMessage(error)}`,
    );
  }
}

async function setApiKey(context) {
  const value = await vscode.window.showInputBox({
    prompt: "Enter the API key configured in LM Studio. Leave blank to remove it.",
    password: true,
    ignoreFocusOut: true,
  });
  if (value === undefined) {
    return;
  }
  if (value.trim()) {
    await context.secrets.store(API_KEY_SECRET, value.trim());
    await vscode.window.showInformationMessage("LM Studio API key saved securely.");
  } else {
    await context.secrets.delete(API_KEY_SECRET);
    await vscode.window.showInformationMessage("LM Studio API key removed.");
  }
}

function activate(context) {
  const provider = new LMStudioChatProvider(context);
  context.subscriptions.push(
    vscode.lm.registerLanguageModelChatProvider("lmstudio", provider),
    vscode.commands.registerCommand("lmStudioChat.checkConnection", () =>
      checkConnection(provider),
    ),
    vscode.commands.registerCommand("lmStudioChat.setApiKey", () =>
      setApiKey(context),
    ),
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
