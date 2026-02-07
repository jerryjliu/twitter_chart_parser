"use client";

import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { validateLlamaKey } from "@/lib/api";

const STORAGE_KEY = "llama-cloud-api-key";

interface ApiKeyGateProps {
  onValidated: (apiKey: string) => void;
  children: ReactNode;
}

export default function ApiKeyGate({ onValidated, children }: ApiKeyGateProps) {
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [ready, setReady] = useState(false);
  const [checkingStored, setCheckingStored] = useState(true);

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      setCheckingStored(false);
      return;
    }

    setLoading(true);
    validateLlamaKey(stored)
      .then(() => {
        setReady(true);
        onValidated(stored);
      })
      .catch(() => {
        window.localStorage.removeItem(STORAGE_KEY);
      })
      .finally(() => {
        setLoading(false);
        setCheckingStored(false);
      });
  }, [onValidated]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (!apiKey.trim()) {
      setError("Please enter your LlamaCloud API key.");
      return;
    }

    setLoading(true);
    try {
      await validateLlamaKey(apiKey.trim());
      window.localStorage.setItem(STORAGE_KEY, apiKey.trim());
      onValidated(apiKey.trim());
      setReady(true);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Validation failed");
    } finally {
      setLoading(false);
    }
  };

  if (checkingStored) {
    return (
      <div className="page-center">
        <div className="loading-indicator">Checking stored API key...</div>
      </div>
    );
  }

  if (ready) {
    return <>{children}</>;
  }

  return (
    <div className="page-center">
      <div className="gate-card">
        <p className="eyebrow">LlamaIndex</p>
        <h1>Twitter Chart Parser</h1>
        <p className="subtitle">
          Enter your LlamaCloud API key to parse tweet charts into clean markdown tables.
        </p>

        <form onSubmit={handleSubmit} className="gate-form">
          <label htmlFor="apiKey">LlamaCloud API key</label>
          <input
            id="apiKey"
            type="password"
            placeholder="llx-..."
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
            disabled={loading}
          />

          {error ? <p className="error-text">{error}</p> : null}

          <button type="submit" disabled={loading || !apiKey.trim()}>
            {loading ? "Validating..." : "Continue"}
          </button>
        </form>

        <p className="footnote">
          Key is stored only in your browser local storage and sent to your backend for validation/parsing.
        </p>
      </div>
    </div>
  );
}

export function clearStoredApiKey(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(STORAGE_KEY);
}
