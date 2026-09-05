import React, { useState } from 'react';
import { DistributionSeries, HistogramBin } from '../../types';

interface DistributionChartProps {
  data: DistributionSeries;
  barColor?: string;
}

export const DistributionChart: React.FC<DistributionChartProps> = ({
  data,
  barColor = 'var(--cyan-primary)',
}) => {
  const [hoveredBin, setHoveredBin] = useState<HistogramBin | null>(null);

  if (!data || !data.bins || data.bins.length === 0) {
    return (
      <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
        No measured distribution data available.
      </div>
    );
  }

  const maxCount = Math.max(...data.bins.map((b) => b.count), 1);
  const chartHeight = 160;

  return (
    <div className="tech-panel">
      <div className="tech-panel-header">
        <h3>{data.metric_name}</h3>
        <div style={{ display: 'flex', gap: '16px', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
          <span>Mean: <b style={{ color: 'var(--cyan-primary)' }}>{data.mean} {data.unit}</b></span>
          <span>Std: <b style={{ color: 'var(--text-secondary)' }}>&plusmn;{data.std_dev}</b></span>
          <span>Range: <b style={{ color: 'var(--text-secondary)' }}>{data.min_value} &ndash; {data.max_value}</b></span>
        </div>
      </div>

      <div className="tech-panel-body">
        <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          {data.description}
        </p>

        {/* SVG Histogram */}
        <div style={{ position: 'relative', height: `${chartHeight + 40}px`, width: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'flex-end', height: `${chartHeight}px`, gap: '8px', paddingBottom: '4px', borderBottom: '1px solid var(--border-medium)' }}>
            {data.bins.map((bin, idx) => {
              const heightPct = (bin.count / maxCount) * 100;
              const isHovered = hoveredBin?.bin_label === bin.bin_label;

              return (
                <div
                  key={idx}
                  style={{
                    flex: 1,
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'flex-end',
                    position: 'relative',
                    cursor: 'pointer',
                  }}
                  onMouseEnter={() => setHoveredBin(bin)}
                  onMouseLeave={() => setHoveredBin(null)}
                >
                  <div
                    style={{
                      height: `${Math.max(4, heightPct)}%`,
                      backgroundColor: isHovered ? '#22d3ee' : barColor,
                      borderRadius: '2px 2px 0 0',
                      transition: 'all 0.15s ease',
                      border: isHovered ? '1px solid #a5f3fc' : 'none',
                    }}
                  />
                </div>
              );
            })}
          </div>

          {/* X Axis Labels */}
          <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
            {data.bins.map((bin, idx) => (
              <div
                key={idx}
                style={{
                  flex: 1,
                  textAlign: 'center',
                  fontSize: '9px',
                  fontFamily: 'var(--font-mono)',
                  color: hoveredBin?.bin_label === bin.bin_label ? 'var(--cyan-primary)' : 'var(--text-muted)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
                title={bin.bin_label}
              >
                {bin.bin_start}
              </div>
            ))}
          </div>

          {/* Hover Tooltip Overlay */}
          {hoveredBin && (
            <div
              style={{
                position: 'absolute',
                top: 0,
                right: 0,
                backgroundColor: 'var(--bg-overlay)',
                border: '1px solid var(--border-bright)',
                borderRadius: 'var(--radius-sm)',
                padding: '6px 10px',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                zIndex: 10,
                backdropFilter: 'blur(4px)',
              }}
            >
              <div style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{hoveredBin.bin_label}</div>
              <div style={{ color: 'var(--cyan-primary)' }}>
                Count: <b>{hoveredBin.count} deposits</b> ({hoveredBin.percentage}%)
              </div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '10px' }}>
                Cumulative Area: <b>{hoveredBin.area_ha} ha</b>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
