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
    <section className="result-list">
      <div className="result-meta">
        <h2>Per-image Results</h2>
        <p>
          Tweet <code>{response.tweet_id}</code> parsed via <strong>{response.source}</strong>
        </p>
      </div>

      {response.warnings.length > 0 ? (
        <div className="warning-list">
          {response.warnings.map((warning) => (
            <p key={warning}>{warning}</p>
          ))}
        </div>
      ) : null}

      {response.results.map((result) => (
        <article className="result-card" key={result.image_url}>
          <header>
            <h3>{result.filename}</h3>
            <p>{result.success ? "Parsed" : "Failed"}</p>
          </header>

          <img src={result.image_url} alt={result.filename} className="result-image" />

          {result.success ? (
            <>
              <div className="result-block">
                <div className="result-header">
                  <h4>Markdown</h4>
                  <button type="button" onClick={() => copy(result.markdown)}>
                    Copy
                  </button>
                </div>
                <pre>{result.markdown || "No markdown content."}</pre>
              </div>

              <div className="result-block">
                <div className="result-header">
                  <h4>Tables ({result.tables.length})</h4>
                </div>
                {result.tables.length === 0 ? (
                  <p className="empty-text">No table structures detected.</p>
                ) : (
                  result.tables.map((table, index) => (
                    <div key={`${result.image_url}-table-${index}`} className="table-block">
                      <p>
                        Page {table.page_number}, {table.row_count} row(s), {table.column_count} column(s)
                      </p>
                      <pre>{table.markdown}</pre>
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            <div className="error-box">{result.error || "Parsing failed."}</div>
          )}
        </article>
      ))}
    </section>
  );
}
