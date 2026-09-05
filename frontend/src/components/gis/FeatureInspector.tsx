import React from 'react';
import { 
  X, 
  Mountain, 
  Radio, 
  CloudSnow, 
  Clock, 
  Maximize2, 
  Download
} from 'lucide-react';
import { DetectionFeature } from '../../types';
import { StatusBadge } from '../common/StatusBadge';

interface FeatureInspectorProps {
  feature: DetectionFeature | null;
  onClose: () => void;
}

export const FeatureInspector: React.FC<FeatureInspectorProps> = ({ feature, onClose }) => {
  if (!feature) {
    return (
      <aside className="inspector-drawer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '32px', textAlign: 'center' }}>
        <div>
          <Mountain size={36} style={{ color: 'var(--text-disabled)', margin: '0 auto 12px' }} />
          <h4 style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
            NO DETECTION SELECTED
          </h4>
          <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            Click on any avalanche deposit polygon in the GIS map or detection table to inspect multi-parameter telemetry.
          </p>
        </div>
      </aside>
    );
  }

  const props = feature.properties;
  const confPct = Math.round((props.confidence_score || 0.5) * 100);

  const downloadFeatureGeoJSON = () => {
    const blob = new Blob([JSON.stringify(feature, null, 2)], { type: 'application/geo+json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${props.detection_id || 'detection'}_wgs84.geojson`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <aside className="inspector-drawer" id="detection-inspector-panel">
      {/* Drawer Header */}
      <div className="inspector-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', fontWeight: 700, color: 'var(--text-cyan)' }}>
              {props.detection_id}
            </span>
            <StatusBadge status={props.risk_level || 'High'} />
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            AVALANCHE DEPOSIT MAPPING PROVENANCE
          </span>
        </div>
        <button
          onClick={onClose}
          style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex' }}
          title="Close Inspector"
        >
          <X size={18} />
        </button>
      </div>

      <div className="inspector-body">
        {/* Model Confidence Metric */}
        <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', borderRadius: 'var(--radius-sm)', padding: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '11px' }}>
            <span style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
              Model Confidence Score
            </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-primary)' }}>
              {confPct}% ({props.confidence_score?.toFixed(3)})
            </span>
          </div>
          <div style={{ height: '6px', backgroundColor: 'var(--bg-surface)', borderRadius: '3px', overflow: 'hidden' }}>
            <div
              style={{
                height: '100%',
                width: `${confPct}%`,
                backgroundColor: confPct >= 80 ? 'var(--hazard-crimson)' : 'var(--hazard-amber)',
                transition: 'width 0.3s ease',
              }}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            <span>Min: {(props.confidence_min * 100).toFixed(1)}%</span>
            <span>Peak: {(props.confidence_max * 100).toFixed(1)}%</span>
          </div>
        </div>

        {/* Spatial Footprint & Dimensions */}
        <div>
          <div className="inspector-section-title">
            <Maximize2 size={13} style={{ color: 'var(--cyan-primary)' }} />
            <span>Spatial Dimensions</span>
          </div>
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', borderRadius: 'var(--radius-sm)', padding: '6px 12px' }}>
            <div className="telemetry-row">
              <span className="label">Deposit Surface Area</span>
              <span className="val">{props.area_ha} ha ({props.area_m2.toLocaleString()} m²)</span>
            </div>
            <div className="telemetry-row">
              <span className="label">Perimeter Length</span>
              <span className="val">{props.perimeter_m.toLocaleString()} m</span>
            </div>
            <div className="telemetry-row">
              <span className="label">Geographic Region</span>
              <span className="val" style={{ fontSize: '11px' }}>{props.region}</span>
            </div>
          </div>
        </div>

        {/* Terrain Topography */}
        <div>
          <div className="inspector-section-title">
            <Mountain size={13} style={{ color: 'var(--terrain-emerald)' }} />
            <span>Copernicus DEM Terrain Topography</span>
          </div>
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', borderRadius: 'var(--radius-sm)', padding: '6px 12px' }}>
            <div className="telemetry-row">
              <span className="label">Mean Elevation</span>
              <span className="val">{props.elevation_mean_m} m a.s.l.</span>
            </div>
            <div className="telemetry-row">
              <span className="label">Elevation Extents</span>
              <span className="val">{props.elevation_min_m}m &ndash; {props.elevation_max_m}m</span>
            </div>
            <div className="telemetry-row">
              <span className="label">Mean Terrain Slope</span>
              <span className="val">{props.slope_mean_deg}°</span>
            </div>
            <div className="telemetry-row">
              <span className="label">Dominant Aspect Orientation</span>
              <span className="val">{props.aspect_cardinal} ({props.aspect_mean_deg}°)</span>
            </div>
          </div>
        </div>

        {/* Sentinel-1 SAR Radar Physics */}
        <div>
          <div className="inspector-section-title">
            <Radio size={13} style={{ color: 'var(--blue-radar)' }} />
            <span>Sentinel-1 SAR Backscatter Physics</span>
          </div>
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', borderRadius: 'var(--radius-sm)', padding: '6px 12px' }}>
            <div className="telemetry-row">
              <span className="label">VH Cross-Pol Log-Ratio (Δσ°)</span>
              <span className="val" style={{ color: '#f87171' }}>{props.delta_vh_db} dB</span>
            </div>
            <div className="telemetry-row">
              <span className="label">VV Co-Pol Log-Ratio (Δσ°)</span>
              <span className="val">{props.delta_vv_db} dB</span>
            </div>
            <div className="telemetry-row">
              <span className="label">Satellite Sensor Mode</span>
              <span className="val">{props.sensor}</span>
            </div>
          </div>
        </div>

        {/* ERA5 Meteorological Context */}
        <div>
          <div className="inspector-section-title">
            <CloudSnow size={13} style={{ color: 'var(--topo-violet)' }} />
            <span>ERA5-Land Weather Context at Acquisition</span>
          </div>
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', borderRadius: 'var(--radius-sm)', padding: '6px 12px' }}>
            <div className="telemetry-row">
              <span className="label">2-Meter Air Temperature</span>
              <span className="val">{props.era5_temperature_c}°C</span>
            </div>
            <div className="telemetry-row">
              <span className="label">Surface Snow Depth</span>
              <span className="val">{props.era5_snow_depth_m} m</span>
            </div>
            <div className="telemetry-row">
              <span className="label">Total Accumulated Precip</span>
              <span className="val">{props.era5_precip_mm} mm</span>
            </div>
          </div>
        </div>

        {/* Temporal Baseline */}
        <div>
          <div className="inspector-section-title">
            <Clock size={13} style={{ color: 'var(--text-muted)' }} />
            <span>Observation Temporal Pair</span>
          </div>
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', borderRadius: 'var(--radius-sm)', padding: '6px 12px' }}>
            <div className="telemetry-row">
              <span className="label">T1 Pre-Event SAR</span>
              <span className="val" style={{ fontSize: '11px' }}>{props.acquisition_t1}</span>
            </div>
            <div className="telemetry-row">
              <span className="label">T2 Post-Event SAR</span>
              <span className="val" style={{ fontSize: '11px' }}>{props.acquisition_t2}</span>
            </div>
            <div className="telemetry-row">
              <span className="label">Model Architecture</span>
              <span className="val" style={{ fontSize: '11px' }}>{props.model_version}</span>
            </div>
          </div>
        </div>

        {/* Export Button */}
        <button
          className="btn-secondary"
          onClick={downloadFeatureGeoJSON}
          style={{ width: '100%', justifyContent: 'center', marginTop: '8px' }}
        >
          <Download size={14} />
          <span>Export Detection GeoJSON</span>
        </button>
      </div>
    </aside>
  );
};
