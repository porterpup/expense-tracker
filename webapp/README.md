Expense PWA (client-side)

This is a frontend-only MVP that runs entirely in the browser using tesseract.js (WASM) for OCR and IndexedDB for storage.

## Local development

```bash
cd webapp
npm install
npm run dev
# → http://localhost:5173
```

## Deploying to Vercel

The app is a standard Vite/React project — Vercel detects it automatically with zero config.

1. **Create a Vercel project:**
   - Vercel dashboard → New Project → Import GitHub repo
   - Root directory: `webapp`
   - Framework preset: Vite (auto-detected)
   - No environment variables needed

2. **Deploy** — Vercel builds and deploys on every push to `main`.

After deploy, set `CORS_ORIGINS=https://your-app.vercel.app` in your **backend** Vercel project's environment variables to lock down cross-origin access.

## Features

- **Receipt OCR** — upload a photo; tesseract.js extracts merchant, date, and amount automatically
- **IndexedDB storage** — expenses saved locally in the browser (works offline)
- **Sync from server** — pull expenses from the backend API into local storage
- **Export CSV** — download all saved expenses as a CSV file
- **PWA-ready** — installable on mobile (service worker registered, manifest included)

## Notes

- OCR runs entirely in-browser via WebAssembly — no server required for the core capture flow
- The backend (ingestion service) is only needed for webhook ingestion and server-side sync

