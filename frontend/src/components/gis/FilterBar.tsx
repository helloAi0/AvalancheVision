import React from 'react';
import { Download, RotateCcw } from 'lucide-react';
import { api } from '../../services/api';

interface FilterBarProps {
  confidenceThreshold: number;
  onConfidenceChange: (val: number) => void;
  minAreaHa: number;
  onMinAreaChange: (val: number) => void;
  minSlopeDeg: number | null;
  onMinSlopeChange: (val: number | null) => void;
  selectedAspect: string;
  onAspectChange: (val: string) => void;
  totalMatched: number;
  totalSwath: number;
  onReset: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  confidenceThreshold,
  onConfidenceChange,
  minAreaHa,
  onMinAreaChange,
  minSlopeDeg,
  onMinSlopeChange,
  selectedAspect,
  onAspectChange,
  totalMatched,
  totalSwath,
  onReset,
}) => {
  const aspects = ['ALL', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];

  return (
    <div
      style={{
        backgroundColor: 'var(--bg-primary)',
        borderBottom: '1px solid var(--border-dim)',
        padding: '10px var(--space-lg)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        flexWrap: 'wrap',
        zIndex: 30,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
        {/* Confidence Threshold Slider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
            Confidence &ge;
          </span>
          <input
            type="range"
            min="0.10"
            max="0.90"
            step="0.05"
            value={confidenceThreshold}
            onChange={(e) => onConfidenceChange(parseFloat(e.target.value))}
            style={{ width: '110px', accentColor: 'var(--cyan-primary)', cursor: 'pointer' }}
          />
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--cyan-primary)', fontWeight: 700, width: '42px' }}>
            {Math.round(confidenceThreshold * 100)}%
          </span>
        </div>

        {/* Min Area Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
            Min Area:
          </span>
          <select
            value={minAreaHa}
            onChange={(e) => onMinAreaChange(parseFloat(e.target.value))}
            style={{
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border-dim)',
              color: 'var(--text-primary)',
              borderRadius: 'var(--radius-xs)',
              padding: '4px 8px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
            }}
          >
            <option value="0">All Sizes</option>
            <option value="0.1">&ge; 0.1 ha (1,000 m²)</option>
            <option value="0.25">&ge; 0.25 ha (2,500 m²)</option>
            <option value="0.5">&ge; 0.5 ha (5,000 m²)</option>
            <option value="1.0">&ge; 1.0 ha (10,000 m²)</option>
          </select>
        </div>

        {/* Min Slope Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
            Slope:
          </span>
          <select
            value={minSlopeDeg ?? ''}
            onChange={(e) => onMinSlopeChange(e.target.value ? parseFloat(e.target.value) : null)}
            style={{
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border-dim)',
              color: 'var(--text-primary)',
              borderRadius: 'var(--radius-xs)',
              padding: '4px 8px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
            }}
          >
            <option value="">All Slopes</option>
            <option value="20">&ge; 20° (Mountain Runout)</option>
            <option value="25">&ge; 25° (Track Zone)</option>
            <option value="30">&ge; 30° (Starting/Steep)</option>
            <option value="35">&ge; 35° (Severe Incline)</option>
          </select>
        </div>

        {/* Aspect Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
            Aspect:
          </span>
          <select
            value={selectedAspect}
            onChange={(e) => onAspectChange(e.target.value)}
            style={{
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border-dim)',
              color: 'var(--text-primary)',
              borderRadius: 'var(--radius-xs)',
              padding: '4px 8px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
            }}
          >
            {aspects.map((a) => (
              <option key={a} value={a}>
                {a === 'ALL' ? 'All Aspects' : `${a}-Facing`}
              </option>
            ))}
          </select>
        </div>

        {/* Reset */}
        <button
          onClick={onReset}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            fontSize: '11px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}
          title="Reset Filters"
        >
          <RotateCcw size={12} />
          <span>Reset</span>
        </button>
      </div>

      {/* Right Side: Matched Count & Exports */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
          <span style={{ color: 'var(--text-muted)' }}>Displaying: </span>
          <span style={{ color: 'var(--cyan-primary)', fontWeight: 700 }}>{totalMatched}</span>
          <span style={{ color: 'var(--text-muted)' }}> / {totalSwath} deposits</span>
        </div>

        <div style={{ display: 'flex', gap: '6px' }}>
          <a
            href={api.getGeoJSONExportUrl()}
            download="avalanche_deposit_detections_wgs84.geojson"
            className="btn-secondary"
            style={{ padding: '4px 10px', fontSize: '11px' }}
          >
            <Download size={12} />
            <span>GeoJSON</span>
          </a>
          <a
            href={api.getCSVExportUrl()}
            download="avalanche_deposit_telemetry.csv"
            className="btn-secondary"
            style={{ padding: '4px 10px', fontSize: '11px' }}
          >
            <Download size={12} />
            <span>CSV</span>
          </a>
        </div>
      </div>
    </div>
  );
};
