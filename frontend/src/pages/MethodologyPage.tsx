import React from 'react';
import { BookOpen, ShieldCheck, Radar, Mountain, CloudSnow } from 'lucide-react';

export const MethodologyPage: React.FC = () => {
  return (
    <div style={{ padding: 'var(--space-xl)', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Scientific Methodology & Provenance
        </h1>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
          Physics-informed remote sensing workflow for post-event avalanche deposit detection and mapping.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 'var(--space-lg)', marginBottom: '24px' }}>
        <div className="tech-panel">
          <div className="tech-panel-header">
            <h3><Radar size={14} /> SAR Change Detection</h3>
          </div>
          <div className="tech-panel-body" style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Avalanche deposits are identified through the change in Sentinel-1 cross-polarized radar backscatter, where post-event surfaces exhibit a strong drop in VH and VV response relative to their stable pre-event state.
          </div>
        </div>

        <div className="tech-panel">
          <div className="tech-panel-header">
            <h3><Mountain size={14} /> Terrain Conditioning</h3>
          </div>
          <div className="tech-panel-body" style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Copernicus DEM-derived slope, aspect, and elevation are used to retain physically plausible avalanche tracks and runout zones while filtering out flat terrain and persistently stable ground surfaces.
          </div>
        </div>

        <div className="tech-panel">
          <div className="tech-panel-header">
            <h3><CloudSnow size={14} /> Atmospheric Context</h3>
          </div>
          <div className="tech-panel-body" style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            ERA5-Land precipitation, snow depth, and near-surface temperature help distinguish snowpack-triggered depositional signatures from persistent seasonal radar variations or unrelated terrain changes.
          </div>
        </div>
      </div>

      <div className="tech-panel" style={{ marginBottom: '24px' }}>
        <div className="tech-panel-header">
          <h3><BookOpen size={14} /> Core Detection Logic</h3>
        </div>
        <div className="tech-panel-body" style={{ display: 'grid', gap: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
          <p>
            The system estimates a probability map over a multimodal 10-band stack, where each pixel combines SAR change metrics, DEM morphology, and atmospheric context.
          </p>
          <div style={{ fontFamily: 'var(--font-mono)', background: 'var(--bg-secondary)', border: '1px solid var(--border-medium)', borderRadius: '4px', padding: '12px', color: 'var(--text-primary)' }}>
            P(Deposit) = f(Δσ°VV, Δσ°VH, slope, aspect, elevation, precipitation, temperature, snow depth)
          </div>
          <p>
            Final polygons are retained when confidence exceeds the configured threshold, terrain slope satisfies the physical plausibility window, and the contiguous cluster size is above the noise-suppression minimum.
          </p>
        </div>
      </div>

      <div className="tech-panel">
        <div className="tech-panel-header">
          <h3><ShieldCheck size={14} /> Scientific Scope Integrity</h3>
        </div>
        <div className="tech-panel-body" style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
          AvalancheVision is designed for post-event avalanche deposit detection and mapping using Sentinel-1 SAR change signatures and terrain context. It does not claim to provide avalanche forecasting or hazard warnings for real-time operational decision making.
        </div>
      </div>
    </div>
  );
};
