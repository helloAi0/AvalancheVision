/**
 * TypeScript domain models for AvalancheVision Scientific Platform.
 */

export interface DetectionProperties {
  detection_id: string;
  risk_level: 'Moderate' | 'High' | 'Very High';
  confidence_score: number;
  confidence_max: number;
  confidence_min: number;
  area_ha: number;
  area_m2: number;
  perimeter_m: number;
  elevation_mean_m: number;
  elevation_min_m: number;
  elevation_max_m: number;
  slope_mean_deg: number;
  aspect_cardinal: string;
  aspect_mean_deg: number;
  delta_vv_db: number;
  delta_vh_db: number;
  era5_temperature_c: number;
  era5_precip_mm: number;
  era5_snow_depth_m: number;
  acquisition_t1: string;
  acquisition_t2: string;
  model_version: string;
  sensor: string;
  region: string;
}

export interface GeoJSONPolygonGeometry {
  type: 'Polygon' | 'MultiPolygon';
  coordinates: any[];
}

export interface DetectionFeature {
  type: 'Feature';
  id: string;
  properties: DetectionProperties;
  geometry: GeoJSONPolygonGeometry;
}

export interface DetectionGeoJSON {
  type: 'FeatureCollection';
  name: string;
  crs: {
    type: string;
    properties: { name: string };
  };
  metadata: {
    region?: string;
    total_matched?: number;
    total_in_swath?: number;
    filters_applied?: Record<string, any>;
    threshold_applied?: number;
    validation_metrics?: Record<string, any>;
  };
  features: DetectionFeature[];
}

export interface DetectionSummaryStats {
  total_detections: number;
  total_area_ha: number;
  mean_confidence: number;
  mean_slope_deg: number;
  mean_elevation_m: number;
  mean_delta_vh_db: number;
  high_risk_count: number;
  very_high_risk_count: number;
  region: string;
  acquisition_window: {
    t1: string;
    t2: string;
  };
  model_version: string;
}

export interface SARObservation {
  id: string;
  scene_name: string;
  satellite: string;
  instrument: string;
  sensor_mode: string;
  product_type: string;
  polarization: string[];
  acquisition_date: string;
  orbit_direction: 'ASCENDING' | 'DESCENDING';
  relative_orbit: number | null;
  absolute_orbit: number | null;
  pixel_spacing_m: number;
  status: 'AVAILABLE' | 'PROCESSED';
  file_size_gb: number;
  bbox: [number, number, number, number];
  footprint_geojson?: any;
}

export interface ObservationListResponse {
  total_count: number;
  observations: SARObservation[];
  active_aoi: string;
  last_catalog_sync: string;
}

export interface InputBandConfig {
  index: number;
  name: string;
  modality: 'SAR' | 'DEM' | 'ERA5';
  description: string;
  units: string;
  resolution_m: number;
}

export interface ModelBenchmarkMetrics {
  iou: number;
  f1_score: number;
  precision: number;
  recall: number;
  false_alarm_rate: number;
  optimal_threshold: number;
  confusion_matrix: {
    tp: number;
    fp: number;
    tn: number;
    fn: number;
  };
}

export interface ModelVersionRegistry {
  active_model_version: string;
  available_models: ModelDetails[];
}

export interface ModelDetails {
  model_version: string;
  architecture: string;
  framework: string;
  input_channels: number;
  output_classes: number;
  parameters_count: number;
  checkpoint_file: string;
  checkpoint_size_mb: number;
  training_dataset: string;
  training_epochs: number;
  patch_size: number;
  loss_function: string;
  optimizer: string;
  input_bands: InputBandConfig[];
  benchmarks?: ModelBenchmarkMetrics;
  scientific_status: string;
  limitations: string[];
}

export interface JobStageLog {
  stage_name: string;
  display_title: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'SKIPPED';
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  details?: string;
}

export interface ProcessingJob {
  job_id: string;
  job_type: string;
  aoi_id: string;
  aoi_name: string;
  status: 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  current_stage: string;
  progress_percentage: number;
  submitted_at: string;
  started_at?: string;
  completed_at?: string;
  execution_duration_sec?: number;
  model_version: string;
  confidence_threshold: number;
  output_detections_count?: number;
  output_area_ha?: number;
  error_message?: string;
  stages: JobStageLog[];
  raw_logs: string[];
}

export interface JobListResponse {
  total_jobs: number;
  jobs: ProcessingJob[];
}

export interface HistogramBin {
  bin_start: number;
  bin_end: number;
  bin_label: string;
  count: number;
  percentage: number;
  area_ha: number;
}

export interface DistributionSeries {
  metric_name: string;
  unit: string;
  description: string;
  bins: HistogramBin[];
  mean: number;
  std_dev: number;
  min_value: number;
  max_value: number;
  total_samples: number;
}

export interface ROCPoint {
  threshold: number;
  false_positive_rate: number;
  true_positive_rate: number;
  precision: number;
  recall: number;
  f1_score: number;
}

export interface ScientificAnalyticsResponse {
  region: string;
  dataset_date_range: string;
  total_detections_analyzed: number;
  total_area_mapped_ha: number;
  slope_distribution: DistributionSeries;
  elevation_distribution: DistributionSeries;
  backscatter_vh_change_distribution: DistributionSeries;
  confidence_distribution: DistributionSeries;
  aspect_distribution: Record<string, number>;
  roc_curve: ROCPoint[];
  validation_summary: Record<string, any>;
}

export interface RegionOfInterest {
  id: string;
  name: string;
  country: string;
  mountain_range: string;
  center_lon: number;
  center_lat: number;
  default_zoom: number;
  bbox_wgs84: [number, number, number, number];
  utm_epsg: number;
  dem_coverage: boolean;
  sar_coverage: boolean;
  era5_coverage: boolean;
}

export interface SystemHealthResponse {
  status: string;
  version: string;
  pytorch_version: string;
  device: string;
  cuda_available: boolean;
  database_status: string;
  database_type: string;
  active_aoi: RegionOfInterest;
  storage_status: Record<string, boolean>;
  active_model: string;
}

export interface RasterBandMetadata {
  index: number;
  name: string;
  units?: string;
  dtype: string;
  nodata?: number;
}

export interface RasterMetadata {
  raster_id: string;
  source: string;
  acquisition_date?: string;
  crs?: string;
  bounds: number[];
  bounds_wgs84?: number[];
  width: number;
  height: number;
  resolution_m: number[];
  band_count: number;
  bands: RasterBandMetadata[];
  driver: string;
  cog_status: string;
}

export interface ProfilePoint {
  distance_m: number;
  longitude: number;
  latitude: number;
  values: Record<string, number | null>;
}

export interface TerrainProfileResponse {
  raster_id: string;
  source_crs?: string;
  sample_count: number;
  start: number[];
  end: number[];
  points: ProfilePoint[];
}
