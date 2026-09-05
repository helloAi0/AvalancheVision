/**
 * API Client for interacting with the FastAPI backend endpoints.
 * Proxied via vite.config.ts so we can use relative paths.
 */

export interface TransectPoint {
  distance_m: number;
  longitude: number;
  latitude: number;
  elevation_m: number;
  slope_degrees: number;
  delta_vh_db: number;
}

export interface TransectResponse {
  total_distance_m: number;
  sample_count: number;
  profile: TransectPoint[];
}

export const fetchTerrainProfile = async (coordinates: number[][], samples = 100): Promise<TransectResponse> => {
  const response = await fetch('/api/v1/terrain/profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ coordinates, samples }),
  });

  if (!response.ok) {
    throw new Error(`Profile generation failed: ${response.statusText}`);
  }
  return response.json();
};