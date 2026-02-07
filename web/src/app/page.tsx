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
      <div className="app-shell">
        <header className="app-header">
          <div>
            <p className="eyebrow">LlamaIndex</p>
            <h1>Twitter Chart Parser</h1>
            <p>Convert tweet chart images into clean markdown and table blocks.</p>
          </div>
          <button
            type="button"
            className="ghost-button"
            onClick={() => {
              clearStoredApiKey();
              window.location.reload();
            }}
          >
            Sign Out
          </button>
        </header>

        {apiKey ? <TweetParseForm apiKey={apiKey} loading={loading} onSubmit={handleParse} /> : null}

        {loading ? <p className="status">Parsing in progress...</p> : null}
        {error ? <p className="error-box">{error}</p> : null}

        {result ? (
          <>
            <CombinedMarkdown markdown={result.combined_markdown} />
            <ParseResults response={result} />
          </>
        ) : null}
      </div>
    </ApiKeyGate>
  );
}
