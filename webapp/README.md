Expense PWA (client-side)

This is a frontend-only MVP that runs entirely in the browser using tesseract.js (WASM) for OCR and IndexedDB for storage.

Quickstart (requires Node.js + npm/yarn locally):

1. cd webapp
2. npm install
3. npm run dev

Notes:
- The app uses tesseract.js in the browser to recognize text from uploaded images. For small-scale offline use this keeps costs at zero.
- To connect the PWA to the ingestion backend, implement a sync endpoint in the server and add a sync button in the UI to pull server records.
- Export: click "Export CSV" in the UI to download a CSV of saved expenses.
