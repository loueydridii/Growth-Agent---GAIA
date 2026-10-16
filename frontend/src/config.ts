// frontend/src/config.ts
// API base URL is configured via VITE_API_URL environment variable.
// Add VITE_API_URL=http://your-server:8001 to frontend/.env for production.
export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';
