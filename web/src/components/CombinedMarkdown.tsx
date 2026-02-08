"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import type { OutputViewMode } from "@/types";

interface CombinedMarkdownProps {
  markdown: string;
  outputMode: OutputViewMode;
  onOutputModeChange: (mode: OutputViewMode) => void;
}

export default function CombinedMarkdown({
  markdown,
  outputMode,
  onOutputModeChange,
}: CombinedMarkdownProps) {
  const handleCopy = async () => {
    await navigator.clipboard.writeText(markdown);
  };

  const handleDownload = () => {
    const blob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "tweet-chart-parse.md";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="rounded-xl border border-border bg-background-secondary p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-foreground">Combined Output</h2>
        <div className="flex items-center gap-2">
          <div className="inline-flex rounded-lg border border-border bg-background p-0.5">
            <button
              type="button"
              onClick={() => onOutputModeChange("rendered")}
              className={`rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors ${
                outputMode === "rendered"
                  ? "bg-accent text-white"
                  : "text-foreground-secondary hover:bg-background-tertiary"
              }`}
            >
              Rendered
            </button>
            <button
              type="button"
              onClick={() => onOutputModeChange("raw")}
              className={`rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors ${
                outputMode === "raw"
                  ? "bg-accent text-white"
                  : "text-foreground-secondary hover:bg-background-tertiary"
              }`}
            >
              Raw
            </button>
          </div>
          <button
            type="button"
            onClick={handleCopy}
            className="rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-foreground-secondary transition-colors hover:bg-background-tertiary"
          >
            Copy
          </button>
          <button
            type="button"
            onClick={handleDownload}
            className="rounded-lg bg-accent px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
          >
            Download
          </button>
        </div>
      </div>
      {!markdown ? (
        <div className="rounded-lg border border-border bg-background p-3 text-sm text-foreground-muted">
          No markdown output generated yet.
        </div>
      ) : outputMode === "raw" ? (
        <pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-background p-3 font-mono text-sm text-foreground-secondary">
          {markdown}
        </pre>
      ) : (
        <div className="max-h-[28rem] overflow-auto rounded-lg border border-border bg-background p-3">
          <div className="markdown-rendered text-sm text-foreground-secondary">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
          </div>
        </div>
      )}
    </section>
  );
}
