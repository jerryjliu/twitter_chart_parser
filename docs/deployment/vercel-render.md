# Vercel + Render Deployment Runbook

## Deployment Topology
- Frontend: Vercel, project root `web/`
- Backend: Render web service, project root `backend/`

## Prerequisites
- Access to a Render account and a Vercel account.
- Repository connected to both platforms.
- A production frontend domain available for CORS allowlisting.

## 1) Deploy Backend on Render

### Option A: Blueprint from `render.yaml` (recommended)
1. In Render, create a new Blueprint and point it to this repository.
2. Confirm Render detects `/Users/jerryliu/Programming/other/jerry-exp/twitter_chart_parser/render.yaml`.
3. Apply the service with these expected settings from the blueprint:
   - Runtime: Python
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Health check path: `/health`
4. Set environment variables:
   - `CORS_ORIGINS=https://<your-vercel-domain>`
   - For multiple domains, use comma-separated values.

### Option B: Manual service setup
Use the same runtime, root directory, commands, health check path, and environment variables listed above.

### Backend verification
After deploy, verify:
```bash
curl -sSf https://<your-render-backend>/health
```
Expected response shape:
```json
{"status":"healthy","timestamp":"..."}
```

## 2) Deploy Frontend on Vercel
1. In Vercel, import this repository.
2. Set the project root directory to `web`.
3. Set environment variable:
   - `NEXT_PUBLIC_API_URL=https://<your-render-backend>`
4. Use default Next.js build settings (`npm install`, `next build`).
5. Deploy.

### Frontend verification
- Open the deployed frontend URL.
- Confirm network requests target your `NEXT_PUBLIC_API_URL` value.

## 3) Post-Deploy Smoke Tests

### API checks
1. Health endpoint:
```bash
curl -sSf https://<your-render-backend>/health
```

2. Validation endpoint contract (invalid format example):
```bash
curl -sS -X POST https://<your-render-backend>/validate-llama-key \
  -H 'Content-Type: application/json' \
  -d '{"api_key":"invalid"}'
```
Expected: HTTP 400 with validation error payload.

3. Image extraction endpoint contract:
```bash
curl -sS -X POST https://<your-render-backend>/extract-tweet-images \
  -H 'Content-Type: application/json' \
  -d '{"tweet_url":"https://x.com/<user>/status/<tweet_id>"}'
```
Expected: Either extracted images or a handled domain error payload (not an unhandled 500).

### End-to-end UI check
1. Open deployed frontend.
2. Enter a valid LlamaCloud key.
3. Enter a tweet URL with image media.
4. Run Parse.
5. Confirm results render and API calls succeed.

## Troubleshooting

### CORS errors in browser
- Ensure `CORS_ORIGINS` includes the exact Vercel domain(s) making requests.
- If using previews, include preview domain patterns as explicit comma-separated origins.

### Frontend calling localhost in production
- `NEXT_PUBLIC_API_URL` is missing or incorrect in Vercel.
- Redeploy after updating env vars.

### Backend fails health check on Render
- Confirm root directory is `backend`.
- Confirm start command is `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- Check Render logs for import/runtime failures.

### Local `npm run build` fails with Node version error
- Next.js in this repo requires Node `^18.18.0 || ^19.8.0 || >=20.0.0`.
- Upgrade local Node to at least `18.18.0` (or use Node 20).

## Repo Files Used for Deployment
- `/Users/jerryliu/Programming/other/jerry-exp/twitter_chart_parser/render.yaml`
- `/Users/jerryliu/Programming/other/jerry-exp/twitter_chart_parser/backend/.env.example`
- `/Users/jerryliu/Programming/other/jerry-exp/twitter_chart_parser/web/.env.example`
