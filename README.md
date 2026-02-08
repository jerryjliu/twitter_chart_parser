# Twitter Chart Parser

Convert chart-heavy X/Twitter post images into clean markdown and structured tables using LlamaParse.

## What This App Does
- Accepts an X/Twitter post URL.
- Pulls image attachments from the post.
- Parses each image into:
  - original markdown/HTML-style content
  - segmented table blocks for downstream analysis
- Returns per-image results so you can inspect and export data cleanly.

Built for chart threads, earnings snapshots, macro dashboards, and other data-dense tweet images.

## Quick Walkthrough
1. Paste a tweet URL.
2. Click **Parse Tweet**.
3. Review the per-image markdown and extracted table outputs.

### Input + Parse Flow
![Twitter Chart Parser input and parse flow](docs/images/twitter_chart_parser1.png)

### Rendered Output + Extracted Tables
![Twitter Chart Parser rendered output and table extraction](docs/images/twitter_chart_parser2.png)

## Getting Started (Local)

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1) Start Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.

### 2) Start Frontend
```bash
cd web
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

If needed, set the frontend API URL:

```bash
export NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Overview
- `POST /validate-llama-key`: Validate a LlamaCloud API key.
- `POST /extract-tweet-images`: Extract image URLs from a tweet/post.
- `POST /parse-tweet`: Extract and parse all tweet images to markdown/tables.
- `GET /health`: Health check.

## Tech Stack
- Frontend: Next.js + React + TypeScript
- Backend: FastAPI + Python

## Project Structure

```text
twitter_chart_parser/
├── backend/
│   ├── api/
│   ├── services/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── web/
│   ├── src/app/
│   ├── src/components/
│   ├── src/lib/
│   └── src/types/
├── docs/images/
├── plans/
└── research/
```

## Troubleshooting
- `NO_MEDIA_FOUND` during extraction:
  - The post may be private, deleted, rate-limited, or not image-based.
  - Add an X bearer token for more reliable extraction.
- Llama key validation fails:
  - Ensure the key starts with `llx-`.
  - Confirm network access to `api.cloud.llamaindex.ai`.
- Parse request is slow:
  - Use a lower parse tier (`cost_effective` or `fast`).
  - Try posts with fewer attached images.

## Reliability Notes
- Without X API credentials, media extraction is best-effort (syndication/meta fallbacks).
- Current scope is image attachments (not video/GIF extraction).
