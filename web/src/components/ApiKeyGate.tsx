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
      <div className="min-h-screen bg-background p-4">
        <div className="flex min-h-[calc(100vh-2rem)] items-center justify-center">
          <div className="flex items-center gap-2 rounded-lg border border-border bg-background-secondary px-4 py-3 text-sm text-foreground-muted">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-foreground-muted border-t-transparent" />
            Checking stored API key...
          </div>
        </div>
      </div>
    );
  }

  if (ready) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="mx-auto flex min-h-[calc(100vh-2rem)] w-full max-w-md items-center">
        <div className="w-full">
          <div className="mb-8 text-center">
            <img
              src="/llamaindex-logo.png"
              alt="LlamaIndex"
              className="mx-auto mb-4 h-16 w-16 rounded-xl"
            />
            <h1 className="text-2xl font-bold text-foreground">Twitter Chart Parser</h1>
            <p className="mt-2 text-sm text-foreground-muted">
              Parse tweet chart images into clean markdown and table output.
            </p>
          </div>

          <div className="rounded-xl border border-border bg-background-secondary p-6">
            <h2 className="mb-2 text-lg font-semibold text-foreground">Enter Your API Key</h2>
            <p className="mb-6 text-sm text-foreground-muted">
              Your key is stored locally in this browser and used for validation and parsing requests.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="apiKey" className="mb-2 block text-sm font-medium text-foreground-secondary">
                  LlamaCloud API key
                </label>
                <input
                  id="apiKey"
                  type="password"
                  placeholder="llx-..."
                  value={apiKey}
                  onChange={(event) => setApiKey(event.target.value)}
                  disabled={loading}
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 text-foreground placeholder:text-foreground-muted focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30 disabled:opacity-60"
                />
              </div>

              {error ? (
                <div className="rounded-lg border border-error/20 bg-error/10 px-3 py-2 text-sm text-error">
                  {error}
                </div>
              ) : null}

              <button
                type="submit"
                disabled={loading || !apiKey.trim()}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-accent px-4 py-3 font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Validating...
                  </>
                ) : (
                  "Continue"
                )}
              </button>
            </form>
          </div>

          <p className="mt-6 text-center text-xs text-foreground-muted">
            Built by LlamaIndex
          </p>
        </div>
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
