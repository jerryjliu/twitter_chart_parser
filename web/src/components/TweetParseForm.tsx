"use client";

import { useState } from "react";

import type { ParseTier, ParseTweetRequest } from "@/types";

interface TweetParseFormProps {
  apiKey: string;
  loading: boolean;
  onSubmit: (payload: ParseTweetRequest) => Promise<void>;
}

const TIERS: Array<{ value: ParseTier; label: string }> = [
  { value: "agentic", label: "Agentic (recommended)" },
  { value: "agentic_plus", label: "Agentic Plus (higher quality, slower)" },
];

export default function TweetParseForm({ apiKey, loading, onSubmit }: TweetParseFormProps) {
  const [tweetUrl, setTweetUrl] = useState("");
  const [xBearerToken, setXBearerToken] = useState("");
  const [tier, setTier] = useState<ParseTier>("agentic");

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onSubmit({
      api_key: apiKey,
      tweet_url: tweetUrl.trim(),
      tier,
      enable_chart_parsing: true,
      x_bearer_token: xBearerToken.trim() || undefined,
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="grid gap-4 rounded-xl border border-border bg-background-secondary p-5"
    >
      <div>
        <label htmlFor="tweet-url" className="mb-2 block text-sm font-medium text-foreground-secondary">
          Tweet URL
        </label>
        <input
          id="tweet-url"
          type="url"
          required
          value={tweetUrl}
          placeholder="https://x.com/.../status/..."
          onChange={(event) => setTweetUrl(event.target.value)}
          disabled={loading}
          className="w-full rounded-lg border border-border bg-background px-4 py-3 text-foreground placeholder:text-foreground-muted focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30 disabled:opacity-60"
        />
      </div>

      <details className="rounded-lg border border-border bg-background px-4 py-3">
        <summary className="cursor-pointer text-sm font-medium text-foreground-secondary">
          Advanced settings
        </summary>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="tier" className="mb-2 block text-sm font-medium text-foreground-secondary">
              Parse tier
            </label>
            <select
              id="tier"
              value={tier}
              onChange={(event) => setTier(event.target.value as ParseTier)}
              disabled={loading}
              className="w-full rounded-lg border border-border bg-background px-4 py-3 text-foreground focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30 disabled:opacity-60"
            >
              {TIERS.map((candidate) => (
                <option value={candidate.value} key={candidate.value}>
                  {candidate.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="x-token" className="mb-2 block text-sm font-medium text-foreground-secondary">
              X bearer token (optional)
            </label>
            <input
              id="x-token"
              type="password"
              value={xBearerToken}
              placeholder="Improves media extraction reliability"
              onChange={(event) => setXBearerToken(event.target.value)}
              disabled={loading}
              className="w-full rounded-lg border border-border bg-background px-4 py-3 text-foreground placeholder:text-foreground-muted focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30 disabled:opacity-60"
            />
          </div>
        </div>
        <p className="mt-3 text-xs text-foreground-muted">
          Specialized chart parsing is always enabled to improve chart-heavy extraction.
        </p>
      </details>

      <button
        type="submit"
        disabled={loading || !tweetUrl.trim()}
        className="flex items-center justify-center gap-2 rounded-lg bg-accent px-4 py-3 font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Parsing tweet..." : "Parse Tweet"}
      </button>
    </form>
  );
}
