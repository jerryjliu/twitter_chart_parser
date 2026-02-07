# Twitter Chart Parser

Parse chart-heavy tweet images into markdown and table outputs using LlamaCloud/LlamaParse.

## Stack
- Frontend: Next.js + React + TypeScript
- Backend: FastAPI + Python

## Project Structure

```
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
├── plans/
└── research.md
```

## Prerequisites
- Python 3.11+
- Node.js 18+

## Backend Quick Start

```bash
cd /Users/jerryliu/Programming/other/jerry-exp/twitter_chart_parser/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.

## Frontend Quick Start

```bash
cd /Users/jerryliu/Programming/other/jerry-exp/twitter_chart_parser/web
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

Set API base URL if needed:

```bash
export NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Overview
- `POST /validate-llama-key`: Validate LlamaCloud API key.
- `POST /extract-tweet-images`: Extract tweet-attached image URLs.
- `POST /parse-tweet`: Extract and parse all tweet images to markdown/tables.
- `GET /health`: Health check.

## Troubleshooting
- Tweet extraction returns `NO_MEDIA_FOUND`:
  - The tweet may be private, deleted, rate-limited, or not image-based.
  - Add an X bearer token for higher extraction reliability.
- Llama key validation fails:
  - Ensure key starts with `llx-`.
  - Confirm network access to `api.cloud.llamaindex.ai`.
- Parse request is slow:
  - Lower parse tier (`cost_effective`/`fast`) or parse tweets with fewer images.

## Reliability Notes
- Without X API credentials, media extraction is best-effort (syndication/meta fallbacks).
- The parser currently targets tweet image attachments (not video/GIF extraction).
