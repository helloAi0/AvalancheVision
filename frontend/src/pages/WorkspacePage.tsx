import React, { useState, useEffect } from 'react';

// 2D Components
import { ScientificMap } from '../components/gis/ScientificMap';
import { FeatureInspector } from '../components/gis/FeatureInspector';
import { FilterBar } from '../components/gis/FilterBar';

// 3D Components
import { Map3DWorkspace } from '../components/gis/Map3DWorkspace';
import { TerrainTransectProfiler } from '../components/gis/TerrainTransectProfiler';
import { SwipeSARViewer } from '../components/gis/SwipeSARViewer';
import { TimeSeriesScrubber } from '../components/gis/TimeSeriesScrubber';

// Types & Services
import { DetectionFeature, DetectionGeoJSON, RasterMetadata, TerrainProfileResponse } from '../types';
import { api } from '../services/api';

// Icons
import { Layers, RefreshCw, Database, Eye, EyeOff, Activity, SlidersHorizontal, Map as MapIcon } from 'lucide-react';

interface WorkspacePageProps {
  onSelectFeature?: (feat: DetectionFeature | null) => void;
}

export const WorkspacePage: React.FC<WorkspacePageProps> = ({ onSelectFeature }) => {
  // --- WORKSPACE MODE STATE ---
  const [activeMode, setActiveMode] = useState<'2d' | '3d' | 'swipe'>('2d');

  // --- GLOBAL DATA STATES ---
  const [geoJsonData, setGeoJsonData] = useState<DetectionGeoJSON | null>(null);
  const [selectedFeature, setSelectedFeature] = useState<DetectionFeature | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // --- FILTER STATES (Applies to both 2D and 3D maps) ---
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(0.45);
  const [minAreaHa, setMinAreaHa] = useState<number>(0.0);
  const [minSlopeDeg, setMinSlopeDeg] = useState<number | null>(null);
  const [selectedAspect, setSelectedAspect] = useState<string>('ALL');
  const [sarDateRange, setSarDateRange] = useState({ startDate: '2024-01-03', endDate: '2024-01-10' });

  // --- 2D MAP LAYER STATES ---
  const [activeBasemap, setActiveBasemap] = useState<'satellite' | 'topo'>('satellite');
  const [showFootprint, setShowFootprint] = useState<boolean>(true);
  const [showAOI, setShowAOI] = useState<boolean>(true);
  const [polygonOpacity, setPolygonOpacity] = useState<number>(0.65);
  const [showLayerPanel, setShowLayerPanel] = useState<boolean>(false);
  
  // --- RASTER & 2D PROFILE STATES ---
  const [rasters, setRasters] = useState<RasterMetadata[]>([]);
  const [selectedRasterId, setSelectedRasterId] = useState<string>('');
  const [showRaster, setShowRaster] = useState<boolean>(false);
  const [rasterOpacity, setRasterOpacity] = useState<number>(0.65);
  const [profile2D, setProfile2D] = useState<TerrainProfileResponse | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);

  // --- 3D PROFILE STATES ---
  const [profileData3D, setProfileData3D] = useState<any[]>([]);
  const [hoveredCoord, setHoveredCoord] = useState<{ lat: number; lon: number } | null>(null);

  // Load available rasters
  useEffect(() => {
    api.listRasters().then((availableRasters) => {
      setRasters(availableRasters);
      if (availableRasters.length > 0) setSelectedRasterId(availableRasters[0].raster_id);
    }).catch(() => setRasters([]));
  }, []);

  const selectedRaster = rasters.find((raster) => raster.raster_id === selectedRasterId);
  const rasterBounds = selectedRaster && selectedRaster.bounds_wgs84
    ? [[selectedRaster.bounds_wgs84[1], selectedRaster.bounds_wgs84[0]], [selectedRaster.bounds_wgs84[3], selectedRaster.bounds_wgs84[2]]] as [[number, number], [number, number]]
    : undefined;
  const rasterUrl = selectedRaster && rasterBounds
    ? api.getRasterWindowUrl(selectedRaster.raster_id, selectedRaster.bounds as [number, number, number, number])
    : undefined;

  // Global Detections Fetcher
  const loadDetections = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getDetectionsGeoJSON({
        min_confidence: confidenceThreshold,
        min_area_ha: minAreaHa > 0 ? minAreaHa : undefined,
        min_slope_deg: minSlopeDeg ?? undefined,
        aspect: selectedAspect !== 'ALL' ? selectedAspect : undefined,
        start_date: sarDateRange.startDate,
        end_date: sarDateRange.endDate,
      });
      setGeoJsonData(data);
      
      if (selectedFeature) {
        const stillExists = data.features.some((f) => f.id === selectedFeature.id);
        if (!stillExists) handleFeatureSelect(null);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load detection GeoJSON data.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDetections();
  }, [confidenceThreshold, minAreaHa, minSlopeDeg, selectedAspect, sarDateRange]);

  const handleResetFilters = () => {
    setConfidenceThreshold(0.45);
    setMinAreaHa(0.0);
    setMinSlopeDeg(null);
    setSelectedAspect('ALL');
  };

  const handleFeatureSelect = (feat: DetectionFeature | null) => {
    setSelectedFeature(feat);
    if (onSelectFeature) {
      onSelectFeature(feat);
    }
  };

  // 2D Raster Sampling
  const sampleActiveRaster = async () => {
    if (!selectedRaster?.bounds_wgs84) return;
    setProfileLoading(true);
    try {
      const bounds = selectedRaster.bounds_wgs84;
      setProfile2D(await api.sampleProfile({
        raster_id: selectedRaster.raster_id,
        start: [bounds[0], bounds[1]],
        end: [bounds[2], bounds[3]],
        samples: 64,
      }));
    } finally {
      setProfileLoading(false);
    }
  };

  // 3D Transect Calculation
  const handleTransectCreated = async (coords: number[][]) => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/terrain/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ coordinates: coords, samples: 100 }),
      });
      const data = await res.json();
      setProfileData3D(data.profile || []);
    } catch (err) {
      console.error('Transect calculation failed:', err);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, height: 'calc(100vh - 96px)', overflow: 'hidden', backgroundColor: '#020617' }}>
      
      {/* Top Header Mode Switcher */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', backgroundColor: 'var(--bg-overlay, rgba(15, 23, 42, 0.9))', borderBottom: '1px solid var(--border-medium, #1e293b)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Layers size={20} style={{ color: 'var(--cyan-primary, #22d3ee)' }} />
          <h1 style={{ fontSize: '14px', fontWeight: 700, fontFamily: 'var(--font-mono, monospace)', letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--text-primary, #f8fafc)', margin: 0 }}>
            GIS Workstation & Geospatial Analysis Terminal
          </h1>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: '#020617', padding: '4px', borderRadius: '6px', border: '1px solid var(--border-medium, #1e293b)' }}>
          <button
            onClick={() => setActiveMode('2d')}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', fontSize: '12px', fontFamily: 'var(--font-mono, monospace)', borderRadius: '4px', transition: 'all 0.2s', ...(activeMode === '2d' ? { backgroundColor: 'rgba(34, 211, 238, 0.15)', color: '#22d3ee', border: '1px solid rgba(34, 211, 238, 0.4)' } : { color: '#94a3b8', border: '1px solid transparent', backgroundColor: 'transparent' }) }}
          >
            <MapIcon size={14} /> 2D Analysis
          </button>
          <button
            onClick={() => setActiveMode('3d')}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', fontSize: '12px', fontFamily: 'var(--font-mono, monospace)', borderRadius: '4px', transition: 'all 0.2s', ...(activeMode === '3d' ? { backgroundColor: 'rgba(34, 211, 238, 0.15)', color: '#22d3ee', border: '1px solid rgba(34, 211, 238, 0.4)' } : { color: '#94a3b8', border: '1px solid transparent', backgroundColor: 'transparent' }) }}
          >
            <Layers size={14} /> 3D Elevation
          </button>
          <button
            onClick={() => setActiveMode('swipe')}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', fontSize: '12px', fontFamily: 'var(--font-mono, monospace)', borderRadius: '4px', transition: 'all 0.2s', ...(activeMode === 'swipe' ? { backgroundColor: 'rgba(34, 211, 238, 0.15)', color: '#22d3ee', border: '1px solid rgba(34, 211, 238, 0.4)' } : { color: '#94a3b8', border: '1px solid transparent', backgroundColor: 'transparent' }) }}
          >
            <SlidersHorizontal size={14} /> SAR Swipe
          </button>
        </div>
      </div>

      {/* Dynamic Workspace Container */}
      <div style={{ display: 'flex', flexDirection: 'column', flex: 1, position: 'relative', overflow: 'hidden' }}>
        
        {/* --- 2D MODE --- */}
        {activeMode === '2d' && (
          <div style={{ display: 'flex', flexDirection: 'column', flex: 1, position: 'relative' }}>
            <FilterBar
              confidenceThreshold={confidenceThreshold}
              onConfidenceChange={setConfidenceThreshold}
              minAreaHa={minAreaHa}
              onMinAreaChange={setMinAreaHa}
              minSlopeDeg={minSlopeDeg}
              onMinSlopeChange={setMinSlopeDeg}
              selectedAspect={selectedAspect}
              onAspectChange={setSelectedAspect}
              totalMatched={geoJsonData?.features?.length || 0}
              totalSwath={geoJsonData?.metadata?.total_in_swath || geoJsonData?.features?.length || 0}
              onReset={handleResetFilters}
            />
            <div style={{ padding: '8px 16px', backgroundColor: 'var(--bg-primary)', borderBottom: '1px solid var(--border-dim)' }}>
              <TimeSeriesScrubber
                startDate={sarDateRange.startDate}
                endDate={sarDateRange.endDate}
                minDate="2023-01-01"
                maxDate="2026-12-31"
                onChange={setSarDateRange}
              />
            </div>

            {error && (
              <div style={{ margin: '12px 16px 0', padding: '8px 12px', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#fecaca', borderRadius: '6px', fontSize: '12px' }}>
                {error}
              </div>
            )}

            <div className="gis-workspace-layout" style={{ display: 'flex', flex: 1, position: 'relative' }}>
              
              {/* Layer Controls Floating Toggle Button */}
              <div style={{ position: 'absolute', top: '16px', left: '16px', zIndex: 1000, display: 'flex', gap: '8px' }}>
                <button
                  className="btn-secondary"
                  onClick={() => setShowLayerPanel(!showLayerPanel)}
                  style={{ backgroundColor: 'var(--bg-overlay)', backdropFilter: 'blur(8px)', padding: '6px 12px', fontSize: '11px', border: '1px solid var(--border-medium)' }}
                >
                  <Layers size={13} style={{ color: 'var(--cyan-primary)' }} />
                  <span>Map Layers & Basemaps</span>
                </button>

                <button
                  className="btn-secondary"
                  onClick={loadDetections}
                  style={{ backgroundColor: 'var(--bg-overlay)', backdropFilter: 'blur(8px)', padding: '6px 10px', fontSize: '11px' }}
                  title="Refresh Map Layers"
                >
                  <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} />
                </button>
              </div>

              {/* Floating Layer Settings Drawer */}
              {showLayerPanel && (
                <div style={{ position: 'absolute', top: '56px', left: '16px', zIndex: 1000, backgroundColor: 'var(--bg-overlay)', backdropFilter: 'blur(10px)', border: '1px solid var(--border-medium)', borderRadius: 'var(--radius-sm)', padding: '16px', width: '260px', boxShadow: 'var(--shadow-elevation)' }}>
                  <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '12px' }}>
                    GIS Layer Configuration
                  </div>

                  {/* Basemap Selection */}
                  <div style={{ marginBottom: '16px' }}>
                    <span style={{ fontSize: '11px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
                      Active Satellite / Terrain Basemap:
                    </span>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <button
                        className={activeBasemap === 'satellite' ? 'btn-primary' : 'btn-secondary'}
                        style={{ flex: 1, padding: '4px 8px', fontSize: '11px', justifyContent: 'center' }}
                        onClick={() => setActiveBasemap('satellite')}
                      >
                        Satellite (Esri)
                      </button>
                      <button
                        className={activeBasemap === 'topo' ? 'btn-primary' : 'btn-secondary'}
                        style={{ flex: 1, padding: '4px 8px', fontSize: '11px', justifyContent: 'center' }}
                        onClick={() => setActiveBasemap('topo')}
                      >
                        Topography
                      </button>
                    </div>
                  </div>

                  {/* Vector Layers Toggles */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px', fontSize: '12px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                      <input type="checkbox" checked={showAOI} onChange={(e) => setShowAOI(e.target.checked)} style={{ accentColor: 'var(--cyan-primary)' }} />
                      <span>AOI Bounding Box (Davos)</span>
                    </label>

                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                      <input type="checkbox" checked={showFootprint} onChange={(e) => setShowFootprint(e.target.checked)} style={{ accentColor: 'var(--cyan-primary)' }} />
                      <span>Sentinel-1 SAR Swath Footprint</span>
                    </label>
                  </div>

                  {/* Polygon Opacity Slider */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
                      <span>Polygon Opacity</span>
                      <span style={{ fontFamily: 'var(--font-mono)' }}>{Math.round(polygonOpacity * 100)}%</span>
                    </div>
                    <input type="range" min="0.2" max="1.0" step="0.05" value={polygonOpacity} onChange={(e) => setPolygonOpacity(parseFloat(e.target.value))} style={{ width: '100%', accentColor: 'var(--cyan-primary)' }} />
                  </div>

                  <div style={{ borderTop: '1px solid var(--border-dim)', marginTop: '16px', paddingTop: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}><Database size={12} /> Raster data layer</span>
                      <button className="btn-secondary" onClick={() => setShowRaster(!showRaster)} style={{ padding: '3px 6px' }} title={showRaster ? 'Hide raster' : 'Show raster'}>
                        {showRaster ? <EyeOff size={12} /> : <Eye size={12} />}
                      </button>
                    </div>
                    <select value={selectedRasterId} onChange={(event) => setSelectedRasterId(event.target.value)} style={{ width: '100%', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', color: 'var(--text-primary)', padding: '5px', fontSize: '11px' }}>
                      {rasters.length === 0 && <option value="">No raster artifacts available</option>}
                      {rasters.map((raster) => <option key={raster.raster_id} value={raster.raster_id}>{raster.raster_id} ({raster.band_count} band)</option>)}
                    </select>
                    {selectedRaster && (
                      <div style={{ marginTop: '8px', fontSize: '10px', lineHeight: 1.5, color: 'var(--text-muted)' }}>
                        <div>{selectedRaster.source}</div>
                        <div>{selectedRaster.crs || 'CRS unavailable'} | {selectedRaster.width} x {selectedRaster.height}</div>
                        <div>{selectedRaster.resolution_m.map((value) => value.toFixed(2)).join(' x ')} m | COG: {selectedRaster.cog_status}</div>
                      </div>
                    )}
                    <input type="range" min="0.1" max="1" step="0.05" value={rasterOpacity} onChange={(event) => setRasterOpacity(parseFloat(event.target.value))} style={{ width: '100%', marginTop: '8px', accentColor: 'var(--blue-radar)' }} aria-label="Raster opacity" />
                    <button className="btn-secondary" onClick={sampleActiveRaster} disabled={!selectedRaster || profileLoading} style={{ width: '100%', justifyContent: 'center', marginTop: '10px', padding: '5px', fontSize: '10px' }}>
                      <Activity size={12} /> {profileLoading ? 'Sampling raster...' : 'Sample extent profile'}
                    </button>
                  </div>
                </div>
              )}

              {/* 2D Map Viewport */}
              <ScientificMap
                geoJsonData={geoJsonData}
                selectedFeature={selectedFeature}
                onSelectFeature={handleFeatureSelect}
                activeBasemap={activeBasemap}
                showObservationFootprint={showFootprint}
                showAOIBoundary={showAOI}
                opacity={polygonOpacity}
                rasterLayerUrl={showRaster ? rasterUrl : undefined}
                rasterBounds={showRaster ? rasterBounds : undefined}
                rasterOpacity={rasterOpacity}
              />

              {/* Feature Inspector Panel */}
              <FeatureInspector
                feature={selectedFeature}
                onClose={() => handleFeatureSelect(null)}
              />

              {/* 2D Raster Profile Overlay */}
              {profile2D && (
                <div style={{ position: 'absolute', left: '16px', right: '16px', bottom: '16px', zIndex: 900, background: 'var(--bg-overlay)', backdropFilter: 'blur(8px)', border: '1px solid var(--border-medium)', padding: '10px 14px', maxHeight: '150px', overflow: 'auto' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '6px' }}>
                    <strong>RASTER PROFILE: {profile2D.raster_id}</strong>
                    <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{profile2D.sample_count} samples | {profile2D.source_crs}</span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '6px', fontFamily: 'var(--font-mono)', fontSize: '10px' }}>
                    {profile2D.points.filter((_, index) => index % 16 === 0).map((point) => (
                      <div key={point.distance_m} style={{ borderLeft: '2px solid var(--blue-radar)', paddingLeft: '6px' }}>
                        <div>{point.distance_m.toFixed(0)} m</div>
                        <div style={{ color: 'var(--text-muted)' }}>{Object.values(point.values).find((value) => value !== null)?.toFixed(4) ?? 'nodata'}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* --- 3D MODE --- */}
        {activeMode === '3d' && (
          <div style={{ display: 'flex', flexDirection: 'column', flex: 1, padding: '24px', gap: '24px', overflowY: 'auto' }}>
            <Map3DWorkspace
              geojson={geoJsonData}
              onSelectFeature={handleFeatureSelect}
              onTransectCreated={handleTransectCreated}
              hoveredProfileCoord={hoveredCoord}
            />
            <TerrainTransectProfiler
              profileData={profileData3D}
              onHoverPoint={setHoveredCoord}
            />
          </div>
        )}

        {/* --- SAR SWIPE MODE --- */}
        {activeMode === 'swipe' && (
          <div style={{ flex: 1, padding: '24px' }}>
            <SwipeSARViewer />
          </div>
        )}
      </div>
    </div>
  );
};