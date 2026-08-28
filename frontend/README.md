# Research Frontend

Vite + React + TypeScript frontend scaffold for the Research workspace.

The frontend uses the FastAPI service configured with `VITE_API_URL`. Set it to
the backend origin in production (for example, `https://your-backend.onrender.com`);
the app appends `/api/v1` automatically. Local Docker development can continue
using the legacy `VITE_API_BASE_URL` fallback. Axios attaches the access token
and refreshes it through `/auth/refresh` when needed.

## Development

```bash
npm install
npm run dev
```

The application modules are organized by API, components, pages, layouts, routes, services, stores, types, and utilities as described in the project structure.

Sign in at `/login`, then create or select a project from the Projects workspace.
The AI copilot uses the selected project for Gemini-backed calls. PDF/TXT files
are uploaded to that project's document endpoint and can be indexed for RAG.

For a production build:

```bash
npm run build
```

For a Render Static Site, set:

```text
Root directory: frontend
Build command: npm ci && npm run build
Publish directory: dist
Environment variable: VITE_API_URL=https://falcon-ai-57te.onrender.com
Environment variable: VITE_DEMO_MODE=false
```

The backend Compose file can build and serve this frontend with the API:

```bash
cd ../backend
docker compose up --build
```

Open the UI at `http://localhost:5173` and the API docs at
`http://localhost:8000/docs`.
