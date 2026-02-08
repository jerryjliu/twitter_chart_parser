"use client";

import { useEffect, useState } from "react";

import ParseResults from "@/components/ParseResults";
import TweetParseForm from "@/components/TweetParseForm";
import { parseTweet, validateLlamaKey } from "@/lib/api";
import { clearStoredApiKey, getStoredApiKey, setStoredApiKey } from "@/lib/apiKeyStorage";
import type {
  ApiKeyValidationStatus,
  OutputViewMode,
  ParseTweetRequest,
  ParseTweetResponse,
} from "@/types";

export default function HomePage() {
  const [apiKey, setApiKey] = useState("");
  const [validatedApiKey, setValidatedApiKey] = useState<string | null>(null);
  const [apiKeyStatus, setApiKeyStatus] = useState<ApiKeyValidationStatus>("idle");
  const [apiKeyError, setApiKeyError] = useState<string | null>(null);
  const [result, setResult] = useState<ParseTweetResponse | null>(null);
  const [outputMode, setOutputMode] = useState<OutputViewMode>("rendered");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const storedApiKey = getStoredApiKey();
    if (!storedApiKey) {
      return;
    }

    const trimmedApiKey = storedApiKey.trim();
    if (!trimmedApiKey) {
      clearStoredApiKey();
      return;
    }

    setApiKey(trimmedApiKey);
    setApiKeyStatus("checking");
    validateLlamaKey(trimmedApiKey)
      .then(() => {
        setValidatedApiKey(trimmedApiKey);
        setApiKeyStatus("valid");
        setApiKeyError(null);
      })
      .catch(() => {
        clearStoredApiKey();
        setValidatedApiKey(null);
        setApiKeyStatus("invalid");
        setApiKeyError("Stored API key is no longer valid. Enter a new key to continue.");
      });
  }, []);

  const handleApiKeyChange = (nextApiKey: string) => {
    setApiKey(nextApiKey);
    setApiKeyError(null);

    if (validatedApiKey && nextApiKey.trim() === validatedApiKey) {
      setApiKeyStatus("valid");
      return;
    }

    setApiKeyStatus("idle");
  };

  const handleParse = async (payload: Omit<ParseTweetRequest, "api_key">) => {
    const trimmedApiKey = apiKey.trim();
    setLoading(true);
    setError(null);
    setApiKeyError(null);

    if (!trimmedApiKey) {
      setApiKeyStatus("invalid");
      setApiKeyError("Please enter your LlamaCloud API key.");
      setLoading(false);
      return;
    }

    if (validatedApiKey !== trimmedApiKey) {
      setApiKeyStatus("checking");
      try {
        await validateLlamaKey(trimmedApiKey);
        setValidatedApiKey(trimmedApiKey);
        setApiKeyStatus("valid");
        setStoredApiKey(trimmedApiKey);
      } catch (validationError) {
        setApiKeyStatus("invalid");
        setApiKeyError(
          validationError instanceof Error ? validationError.message : "API key validation failed.",
        );
        setLoading(false);
        return;
      }
    } else {
      setApiKeyStatus("valid");
    }

    try {
      const response = await parseTweet({
        ...payload,
        api_key: trimmedApiKey,
      });
      setResult(response);
    } catch (parseError) {
      setError(parseError instanceof Error ? parseError.message : "Failed to parse tweet.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-4 py-6 sm:px-6">
        <header className="flex flex-col gap-4 rounded-xl border border-border bg-background px-5 py-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <img src="/llamaindex-logo.png" alt="LlamaIndex" className="mt-0.5 h-9 w-9 rounded-lg" />
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.14em] text-foreground-muted">
                LlamaIndex
              </p>
              <h1 className="mt-1 text-xl font-semibold text-foreground sm:text-2xl">
                Twitter Chart Parser
              </h1>
              <p className="mt-1 text-sm text-foreground-muted">
                Convert tweet chart images into clean markdown and structured table blocks.
              </p>
              <p className="mt-2 max-w-2xl text-sm text-foreground-muted">
                Paste an X/Twitter post URL and the app will pull attached images, parse chart-heavy screenshots,
                and return original per-image markdown/HTML alongside segmented table extractions you can use in
                docs, notes, or analysis workflows.
              </p>
              <p className="mt-2 text-xs text-foreground-muted">
                Built for chart threads, earnings graphics, market snapshots, and other data-dense tweet images.
              </p>
            </div>
          </div>
          <div className="flex items-center justify-end">
            {apiKey.trim() ? (
              <button
                type="button"
                className="rounded-lg border border-border px-3 py-2 text-xs font-medium text-foreground-muted transition-colors hover:border-error/40 hover:text-error"
                onClick={() => {
                  clearStoredApiKey();
                  setApiKey("");
                  setValidatedApiKey(null);
                  setApiKeyStatus("idle");
                  setApiKeyError(null);
                  setError(null);
                  setResult(null);
                }}
              >
                Sign Out
              </button>
            ) : null}
          </div>
        </header>

        <TweetParseForm
          apiKey={apiKey}
          onApiKeyChange={handleApiKeyChange}
          apiKeyStatus={apiKeyStatus}
          apiKeyError={apiKeyError}
          loading={loading}
          onSubmit={handleParse}
        />

        {loading ? (
          <div className="flex items-center gap-2 rounded-lg border border-border bg-background-secondary px-4 py-3 text-sm text-foreground-muted">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-foreground-muted border-t-transparent" />
            {apiKeyStatus === "checking" ? "Validating API key..." : "Parsing in progress..."}
          </div>
        ) : null}

        {error ? (
          <div className="rounded-lg border border-error/20 bg-error/10 px-4 py-3 text-sm text-error">
            {error}
          </div>
        ) : null}

        {result ? (
          <div className="grid gap-4">
            <ParseResults
              response={result}
              outputMode={outputMode}
              onOutputModeChange={setOutputMode}
            />
          </div>
        ) : null}
      </div>
    </div>
  );
}
