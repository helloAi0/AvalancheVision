/**
 * Typed API client for AvalancheVision backend services.
 */

import {
  DetectionGeoJSON,
  DetectionFeature,
  DetectionSummaryStats,
  ObservationListResponse,
  ModelDetails,
  ModelVersionRegistry,
  ScientificAnalyticsResponse,
  JobListResponse,
  ProcessingJob,
  SystemHealthResponse,
  RegionOfInterest,
  RasterMetadata,
  TerrainProfileResponse,
} from '../types';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error [${response.status}] ${response.statusText}: ${errorText}`);
    }

    return (await response.json()) as T;
  } catch (error) {
    console.error(`Fetch failure for ${url}:`, error);
    throw error;
  }
}

export const api = {
  // System Health
  async getHealth(): Promise<SystemHealthResponse> {
    return fetchJson<SystemHealthResponse>(`${API_BASE}/health`);
  },

  async getActiveAOI(): Promise<RegionOfInterest> {
    return fetchJson<RegionOfInterest>(`${API_BASE}/health/aoi`);
  },

  // Detections
  async getDetectionsGeoJSON(params?: {
    min_confidence?: number;
    min_area_ha?: number;
    min_slope_deg?: number;
    max_slope_deg?: number;
    aspect?: string;
    bbox?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<DetectionGeoJSON> {
    const query = new URLSearchParams();
    if (params?.min_confidence !== undefined) query.set('min_confidence', params.min_confidence.toString());
    if (params?.min_area_ha !== undefined) query.set('min_area_ha', params.min_area_ha.toString());
    if (params?.min_slope_deg !== undefined) query.set('min_slope_deg', params.min_slope_deg.toString());
    if (params?.max_slope_deg !== undefined) query.set('max_slope_deg', params.max_slope_deg.toString());
    if (params?.aspect) query.set('aspect', params.aspect);
    if (params?.bbox) query.set('bbox', params.bbox);
    if (params?.start_date) query.set('start_date', params.start_date);
    if (params?.end_date) query.set('end_date', params.end_date);

    const qs = query.toString();
    return fetchJson<DetectionGeoJSON>(`${API_BASE}/detections/geojson${qs ? `?${qs}` : ''}`);
  },

  async getDetectionDetail(detectionId: string): Promise<DetectionFeature> {
    return fetchJson<DetectionFeature>(`${API_BASE}/detections/${encodeURIComponent(detectionId)}`);
  },

  async getDetectionStats(): Promise<DetectionSummaryStats> {
    return fetchJson<DetectionSummaryStats>(`${API_BASE}/detections/stats`);
  },

  // Observations
  async getObservations(filters?: {
    satellite?: string;
    orbit_direction?: string;
    status?: string;
    live?: boolean;
    bbox?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<ObservationListResponse> {
    const query = new URLSearchParams();
    if (filters?.satellite) query.set('satellite', filters.satellite);
    if (filters?.orbit_direction) query.set('orbit_direction', filters.orbit_direction);
    if (filters?.status) query.set('status', filters.status);
    if (filters?.live) query.set('live', 'true');
    if (filters?.bbox) query.set('bbox', filters.bbox);
    if (filters?.start_date) query.set('start_date', filters.start_date);
    if (filters?.end_date) query.set('end_date', filters.end_date);

    const qs = query.toString();
    return fetchJson<ObservationListResponse>(`${API_BASE}/observations${qs ? `?${qs}` : ''}`);
  },

  // Models
  async getCurrentModel(): Promise<ModelDetails> {
    return fetchJson<ModelDetails>(`${API_BASE}/models/current`);
  },

  async getModelRegistry(): Promise<ModelVersionRegistry> {
    return fetchJson<ModelVersionRegistry>(`${API_BASE}/models/registry`);
  },

  // Analytics
  async getScientificAnalytics(): Promise<ScientificAnalyticsResponse> {
    return fetchJson<ScientificAnalyticsResponse>(`${API_BASE}/analytics/distributions`);
  },

  // Raster metadata
  async listRasters(): Promise<RasterMetadata[]> {
    return fetchJson<RasterMetadata[]>(`${API_BASE}/rasters`);
  },

  async getRasterMetadata(rasterId: string): Promise<RasterMetadata> {
    return fetchJson<RasterMetadata>(`${API_BASE}/rasters/${encodeURIComponent(rasterId)}`);
  },

  getRasterWindowUrl(rasterId: string, bbox: [number, number, number, number], width = 512, height = 512): string {
    const params = new URLSearchParams({ bbox: bbox.join(','), width: width.toString(), height: height.toString() });
    return `${API_BASE}/rasters/window/${encodeURIComponent(rasterId)}?${params.toString()}`;
  },

  async sampleProfile(payload: { raster_id: string; start: [number, number]; end: [number, number]; samples?: number }): Promise<TerrainProfileResponse> {
    return fetchJson<TerrainProfileResponse>(`${API_BASE}/analysis/profile`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Jobs
  async listJobs(): Promise<JobListResponse> {
    return fetchJson<JobListResponse>(`${API_BASE}/jobs`);
  },

  async getJobDetail(jobId: string): Promise<ProcessingJob> {
    return fetchJson<ProcessingJob>(`${API_BASE}/jobs/${encodeURIComponent(jobId)}`);
  },

  async submitJob(payload: {
    aoi_id: string;
    pre_event_date: string;
    post_event_date: string;
    model_version: string;
    confidence_threshold: number;
    min_cluster_area_m2: number;
    apply_physics_filter: boolean;
  }): Promise<ProcessingJob> {
    return fetchJson<ProcessingJob>(`${API_BASE}/jobs/submit`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  getJobWebSocketUrl(jobId: string): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}${API_BASE}/jobs/ws/${encodeURIComponent(jobId)}`;
  },

  // Exports
  getGeoJSONExportUrl(): string {
    return `${API_BASE}/export/geojson`;
  },

  getCSVExportUrl(): string {
    return `${API_BASE}/export/csv`;
  },
};
