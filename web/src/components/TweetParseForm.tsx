"use client";

import { useState } from "react";

import type { ParseTier, ParseTweetRequest } from "@/types";

interface TweetParseFormProps {
  apiKey: string;
  loading: boolean;
  onSubmit: (payload: ParseTweetRequest) => Promise<void>;
}

const TIERS: ParseTier[] = ["fast", "cost_effective", "agentic", "agentic_plus"];

export default function TweetParseForm({ apiKey, loading, onSubmit }: TweetParseFormProps) {
  const [tweetUrl, setTweetUrl] = useState("");
  const [xBearerToken, setXBearerToken] = useState("");
  const [tier, setTier] = useState<ParseTier>("agentic");
  const [enableChartParsing, setEnableChartParsing] = useState(true);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onSubmit({
      api_key: apiKey,
      tweet_url: tweetUrl.trim(),
      tier,
      enable_chart_parsing: enableChartParsing,
      x_bearer_token: xBearerToken.trim() || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="parser-card">
      <div className="form-row">
        <label htmlFor="tweet-url">Tweet URL</label>
        <input
          id="tweet-url"
          type="url"
          required
          value={tweetUrl}
          placeholder="https://x.com/.../status/..."
          onChange={(event) => setTweetUrl(event.target.value)}
          disabled={loading}
        />
      </div>

      <div className="form-row">
        <label htmlFor="x-token">X bearer token (optional)</label>
        <input
          id="x-token"
          type="password"
          value={xBearerToken}
          placeholder="Improves media extraction reliability"
          onChange={(event) => setXBearerToken(event.target.value)}
          disabled={loading}
        />
      </div>

      <div className="form-grid">
        <div className="form-row">
          <label htmlFor="tier">Parse tier</label>
          <select
            id="tier"
            value={tier}
            onChange={(event) => setTier(event.target.value as ParseTier)}
            disabled={loading}
          >
            {TIERS.map((candidate) => (
              <option value={candidate} key={candidate}>
                {candidate}
              </option>
            ))}
          </select>
        </div>

        <div className="form-row checkbox-row">
          <label htmlFor="chart-parsing">Enable specialized chart parsing</label>
          <input
            id="chart-parsing"
            type="checkbox"
            checked={enableChartParsing}
            onChange={(event) => setEnableChartParsing(event.target.checked)}
            disabled={loading}
          />
        </div>
      </div>

      <button type="submit" disabled={loading || !tweetUrl.trim()}>
        {loading ? "Parsing tweet..." : "Parse Tweet"}
      </button>
    </form>
  );
}
