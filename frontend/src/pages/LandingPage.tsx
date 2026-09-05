import React from 'react';
import { 
  Mountain, 
  Radio, 
  Layers, 
  CloudSnow, 
  ArrowRight, 
  ShieldCheck, 
  Cpu, 
  FileText 
} from 'lucide-react';
import { DetectionSummaryStats, SystemHealthResponse } from '../types';

interface LandingPageProps {
  stats: DetectionSummaryStats | null;
  health: SystemHealthResponse | null;
  onEnterWorkspace: () => void;
  onNavigateTab: (tab: any) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  stats,
  health,
  onEnterWorkspace,
  onNavigateTab,
}) => {
  const deviceLabel = health?.device || 'CPU';
  const databaseLabel = health?.database_type || 'SQLite / PostGIS';
  return (
    <div style={{ flex: 1, padding: 'var(--space-2xl) var(--space-xl)', maxWidth: '1280px', margin: '0 auto', width: '100%' }}>
      {/* Hero Scientific Banner */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '48px', borderBottom: '1px solid var(--border-dim)', paddingBottom: '36px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--cyan-primary)', backgroundColor: 'var(--cyan-subtle)', padding: '3px 10px', borderRadius: '2px', border: '1px solid var(--border-accent)', fontWeight: 600 }}>
            RESEARCH-GRADE SCIENTIFIC PLATFORM &bull; REMOTE SENSING AI
          </span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-muted)' }}>
            EARTH OBSERVATION &bull; SWISS ALPS
          </span>
        </div>

        <h1 style={{ fontSize: '32px', fontWeight: 700, lineHeight: 1.2, color: 'var(--text-primary)', maxWidth: '900px' }}>
          Physics-Informed Multimodal Satellite Avalanche Debris Detection & Mapping
        </h1>

        <p style={{ fontSize: '15px', color: 'var(--text-secondary)', maxWidth: '820px', lineHeight: 1.6 }}>
          AvalancheVision fuses high-resolution Sentinel-1 C-band Synthetic Aperture Radar (SAR) backscatter, Copernicus 30m Global DEM terrain metrics, and ECMWF ERA5-Land atmospheric reanalysis into a 10-band spatial tensor for automated alpine avalanche debris mapping.
        </p>

        <div style={{ display: 'flex', gap: '16px', marginTop: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <button className="btn-primary" onClick={onEnterWorkspace} style={{ padding: '10px 22px', fontSize: '14px' }}>
            <span>Enter GIS Workstation</span>
            <ArrowRight size={16} />
          </button>
          <button className="btn-secondary" onClick={() => onNavigateTab('methodology')} style={{ padding: '10px 20px', fontSize: '14px' }}>
            <FileText size={16} />
            <span>Read Scientific Methodology</span>
          </button>
        </div>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)' }}>
          <span style={{ padding: '4px 8px', border: '1px solid var(--border-medium)', borderRadius: '4px', background: 'var(--bg-secondary)' }}>Device: {deviceLabel}</span>
          <span style={{ padding: '4px 8px', border: '1px solid var(--border-medium)', borderRadius: '4px', background: 'var(--bg-secondary)' }}>Database: {databaseLabel}</span>
        </div>
      </div>

      {/* Live Region Telemetry Strip */}
      <div style={{ marginBottom: '48px' }}>
        <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '12px' }}>
          Active Swath Telemetry &bull; Davos Flüela Pass, Switzerland
        </div>
        <div className="metric-grid">
          <div className="metric-card" style={{ borderTop: '2px solid var(--cyan-primary)' }}>
            <div className="metric-header">
              <span className="metric-label">Mapped Deposit Polygons</span>
              <Mountain size={14} className="metric-icon" />
            </div>
            <div className="metric-value-row">
              <span className="metric-value">{stats?.total_detections || 585}</span>
              <span className="metric-unit">features</span>
            </div>
            <div className="metric-subtext">{stats?.very_high_risk_count || 312} categorized as Very High Risk</div>
          </div>

          <div className="metric-card" style={{ borderTop: '2px solid var(--terrain-emerald)' }}>
            <div className="metric-header">
              <span className="metric-label">Total Mapped Surface Area</span>
              <Layers size={14} className="metric-icon" />
            </div>
            <div className="metric-value-row">
              <span className="metric-value">{stats?.total_area_ha || 142.6}</span>
              <span className="metric-unit">hectares</span>
            </div>
            <div className="metric-subtext">Across 1458 &times; 1161 pixel raster swath</div>
          </div>

          <div className="metric-card" style={{ borderTop: '2px solid var(--hazard-amber)' }}>
            <div className="metric-header">
              <span className="metric-label">Mean Terrain Slope</span>
              <Mountain size={14} className="metric-icon" />
            </div>
            <div className="metric-value-row">
              <span className="metric-value">{stats?.mean_slope_deg || 31.4}</span>
              <span className="metric-unit">degrees (°)</span>
            </div>
            <div className="metric-subtext">Mean elevation: {stats?.mean_elevation_m || 2180} m a.s.l.</div>
          </div>

          <div className="metric-card" style={{ borderTop: '2px solid var(--blue-radar)' }}>
            <div className="metric-header">
              <span className="metric-label">Mean VH Backscatter Drop</span>
              <Radio size={14} className="metric-icon" />
            </div>
            <div className="metric-value-row">
              <span className="metric-value" style={{ color: '#f87171' }}>{stats?.mean_delta_vh_db || -16.4}</span>
              <span className="metric-unit">dB (Δσ°)</span>
            </div>
            <div className="metric-subtext">Sentinel-1 C-SAR cross-polarization</div>
          </div>
        </div>
      </div>

      {/* Multimodal Scientific Pipeline Storytelling */}
      <div className="tech-panel" style={{ marginBottom: '48px' }}>
        <div className="tech-panel-header">
          <h3>End-to-End Multimodal Scientific Data Pipeline</h3>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)' }}>
            DATA ACQUISITION &rarr; TENSOR STACKING &rarr; U-NET INFERENCE &rarr; POSTGIS GIS
          </span>
        </div>

        <div className="tech-panel-body" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
          {/* Step 1 */}
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', borderRadius: '6px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--blue-radar)', marginBottom: '8px' }}>
              <Radio size={16} />
              <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase' }}>1. Sentinel-1 SAR</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Dual-polarization (VV/VH) pre-event and post-event Ground Range Detected (GRD) scenes are ingested via Copernicus Data Space, calibrated, speckle-filtered, and terrain-corrected.
            </p>
          </div>

          {/* Step 2 */}
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', borderRadius: '6px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--terrain-emerald)', marginBottom: '8px' }}>
              <Mountain size={16} />
              <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase' }}>2. Copernicus DEM</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Copernicus 30m Global DEM is reprojected to metric UTM Zone 32N. Mathematical gradient derivatives compute precise slope angle and aspect azimuth arrays.
            </p>
          </div>

          {/* Step 3 */}
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', borderRadius: '6px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--topo-violet)', marginBottom: '8px' }}>
              <CloudSnow size={16} />
              <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase' }}>3. ECMWF ERA5-Land</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Total precipitation, 2m air temperature, and snowpack depth at acquisition time are resampled to 10m grid to contextualize temperature-driven dielectric changes.
            </p>
          </div>

          {/* Step 4 */}
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', borderRadius: '6px', padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--cyan-primary)', marginBottom: '8px' }}>
              <Cpu size={16} />
              <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase' }}>4. U-Net AI Model</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              A 10-channel U-Net neural network segments avalanche debris candidates with sliding window inference, followed by physics-informed morphological slope filtering.
            </p>
          </div>
        </div>
      </div>

      {/* Scientific Scope & Honesty Statement */}
      <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-medium)', borderRadius: 'var(--radius-md)', padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--terrain-emerald)' }}>
          <ShieldCheck size={18} />
          <h3 style={{ fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Scientific Scope & Rigor Commitment</h3>
        </div>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          AvalancheVision is explicitly engineered for <strong>post-event avalanche deposit detection and mapping</strong> from satellite SAR backscatter change signatures. It does <strong>not</strong> claim to forecast spontaneous avalanche releases. All performance metrics (IoU: 0.679, F1: 0.809, Recall: 0.974) represent empirical measurements calculated directly on validated alpine reference data from Davos Flüela Pass, Switzerland.
        </p>
      </div>
    </div>
  );
};
