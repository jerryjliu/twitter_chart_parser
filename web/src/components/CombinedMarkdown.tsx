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
    <section className="result-block">
      <div className="result-header">
        <h2>Combined Markdown</h2>
        <div className="result-actions">
          <button type="button" onClick={handleCopy}>
            Copy
          </button>
          <button type="button" onClick={handleDownload}>
            Download
          </button>
        </div>
      </div>
      <pre>{markdown || "No markdown output generated yet."}</pre>
    </section>
  );
}
