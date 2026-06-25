// Client for the oceandrift backend API.
// Override the base URL with VITE_API_BASE in a .env file if the API runs
// somewhere other than the default.
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

/**
 * Fetch the surface-current field on a regular lon/lat grid.
 *
 * @param {{resolution?: number, timeDays?: number}} opts
 * @returns {Promise<object>} the /field payload (width, height, bbox, u, v, ...)
 */
export async function fetchField({ resolution = 1.5, timeDays = 0 } = {}) {
  const url = new URL(`${API_BASE}/field`);
  url.searchParams.set("resolution", String(resolution));
  url.searchParams.set("time_days", String(timeDays));

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`GET /field failed: ${response.status}`);
  }
  return response.json();
}

export { API_BASE };
