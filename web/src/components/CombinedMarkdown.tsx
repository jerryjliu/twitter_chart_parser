"use client";

interface CombinedMarkdownProps {
  markdown: string;
}

export default function CombinedMarkdown({ markdown }: CombinedMarkdownProps) {
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
        <h2 className="text-lg font-semibold text-foreground">Combined Markdown</h2>
        <div className="flex items-center gap-2">
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
      <pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-background p-3 font-mono text-sm text-foreground-secondary">
        {markdown || "No markdown output generated yet."}
      </pre>
    </section>
  );
}
