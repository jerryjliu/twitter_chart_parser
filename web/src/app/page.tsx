"use client";

import { useState } from "react";

import ApiKeyGate, { clearStoredApiKey } from "@/components/ApiKeyGate";
import CombinedMarkdown from "@/components/CombinedMarkdown";
import ParseResults from "@/components/ParseResults";
import TweetParseForm from "@/components/TweetParseForm";
import { parseTweet } from "@/lib/api";
import type { ParseTweetRequest, ParseTweetResponse } from "@/types";

export default function HomePage() {
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [result, setResult] = useState<ParseTweetResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleParse = async (payload: ParseTweetRequest) => {
    setLoading(true);
    setError(null);
    try {
      const response = await parseTweet(payload);
      setResult(response);
    } catch (parseError) {
      setError(parseError instanceof Error ? parseError.message : "Failed to parse tweet.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ApiKeyGate onValidated={setApiKey}>
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
              </div>
            </div>
            <div className="flex items-center justify-end">
              <button
                type="button"
                className="rounded-lg border border-border px-3 py-2 text-xs font-medium text-foreground-muted transition-colors hover:border-error/40 hover:text-error"
                onClick={() => {
                  clearStoredApiKey();
                  window.location.reload();
                }}
              >
                Sign Out
              </button>
            </div>
          </header>

          {apiKey ? <TweetParseForm apiKey={apiKey} loading={loading} onSubmit={handleParse} /> : null}

          {loading ? (
            <div className="flex items-center gap-2 rounded-lg border border-border bg-background-secondary px-4 py-3 text-sm text-foreground-muted">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-foreground-muted border-t-transparent" />
              Parsing in progress...
            </div>
          ) : null}

          {error ? (
            <div className="rounded-lg border border-error/20 bg-error/10 px-4 py-3 text-sm text-error">
              {error}
            </div>
          ) : null}

          {result ? (
            <div className="grid gap-4">
              <CombinedMarkdown markdown={result.combined_markdown} />
              <ParseResults response={result} />
            </div>
          ) : null}
        </div>
      </div>
    </ApiKeyGate>
  );
}
