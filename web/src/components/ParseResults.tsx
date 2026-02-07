"use client";

import type { ParseTweetResponse } from "@/types";

interface ParseResultsProps {
  response: ParseTweetResponse;
}

export default function ParseResults({ response }: ParseResultsProps) {
  const copy = async (text: string) => {
    await navigator.clipboard.writeText(text);
  };

  return (
    <section className="grid gap-4">
      <div className="rounded-xl border border-border bg-background-secondary p-4">
        <h2 className="text-lg font-semibold text-foreground">Per-image Results</h2>
        <p className="mt-1 text-sm text-foreground-muted">
          Tweet <code className="rounded bg-background px-1.5 py-0.5 font-mono text-xs">{response.tweet_id}</code>{" "}
          parsed via <strong>{response.source}</strong>
        </p>
      </div>

      {response.warnings.length > 0 ? (
        <div className="rounded-lg border border-warning/30 bg-warning/10 p-3 text-sm text-warning">
          {response.warnings.map((warning) => (
            <p key={warning} className="mt-1 first:mt-0">
              {warning}
            </p>
          ))}
        </div>
      ) : null}

      {response.results.map((result) => (
        <article className="grid gap-3 rounded-xl border border-border bg-background-secondary p-4" key={result.image_url}>
          <header className="flex items-center justify-between gap-3">
            <h3 className="text-base font-semibold text-foreground">{result.filename}</h3>
            <p
              className={
                result.success
                  ? "rounded-full bg-success/15 px-2 py-0.5 text-xs font-medium text-success"
                  : "rounded-full bg-error/15 px-2 py-0.5 text-xs font-medium text-error"
              }
            >
              {result.success ? "Parsed" : "Failed"}
            </p>
          </header>

          <img
            src={result.image_url}
            alt={result.filename}
            className="w-full rounded-lg border border-border bg-background object-contain"
          />

          {result.success ? (
            <>
              <div className="rounded-lg border border-border bg-background p-3">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <h4 className="text-sm font-semibold text-foreground">Markdown</h4>
                  <button
                    type="button"
                    onClick={() => copy(result.markdown)}
                    className="rounded-lg border border-border px-2.5 py-1.5 text-xs font-medium text-foreground-secondary transition-colors hover:bg-background-tertiary"
                  >
                    Copy
                  </button>
                </div>
                <pre className="max-h-72 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-background-secondary p-3 font-mono text-sm text-foreground-secondary">
                  {result.markdown || "No markdown content."}
                </pre>
              </div>

              <div className="rounded-lg border border-border bg-background p-3">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <h4 className="text-sm font-semibold text-foreground">Tables ({result.tables.length})</h4>
                </div>
                {result.tables.length === 0 ? (
                  <p className="text-sm text-foreground-muted">No table structures detected.</p>
                ) : (
                  result.tables.map((table, index) => (
                    <div key={`${result.image_url}-table-${index}`} className="mb-3 last:mb-0">
                      <p className="mb-2 text-xs text-foreground-muted">
                        Page {table.page_number}, {table.row_count} row(s), {table.column_count} column(s)
                      </p>
                      <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-background-secondary p-3 font-mono text-sm text-foreground-secondary">
                        {table.markdown}
                      </pre>
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            <div className="rounded-lg border border-error/20 bg-error/10 p-3 text-sm text-error">
              {result.error || "Parsing failed."}
            </div>
          )}
        </article>
      ))}
    </section>
  );
}
