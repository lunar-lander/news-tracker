import axios from 'axios';

// All API calls use relative paths (e.g. /api/v1/...) so they go through
// the Vite dev-server proxy, which forwards to the API container.
// No baseURL needed — the proxy handles routing.
export const apiClient = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
