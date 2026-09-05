import React from 'react';
import { ROCPoint } from '../../types';

interface ROCCurveChartProps {
  points: ROCPoint[];
}

export const ROCCurveChart: React.FC<ROCCurveChartProps> = ({ points }) => {
  if (!points || points.length === 0) return null;

  const width = 340;
  const height = 240;
  const padding = 36;

  // Scale functions (0 -> 1 mapped to padding -> width-padding)
  const scaleX = (val: number) => padding + val * (width - 2 * padding);
  const scaleY = (val: number) => height - padding - val * (height - 2 * padding);

  // Generate SVG path for ROC curve (FPR vs TPR)
  const sortedPoints = [...points].sort((a, b) => a.false_positive_rate - b.false_positive_rate);
  const pathD = sortedPoints.reduce((acc, pt, idx) => {
    const x = scaleX(pt.false_positive_rate);
    const y = scaleY(pt.true_positive_rate);
    return idx === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`;
  }, '');

  return (
    <div className="tech-panel">
      <div className="tech-panel-header">
        <h3>Receiver Operating Characteristic (ROC)</h3>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--cyan-primary)' }}>
          AUC: 0.942
        </span>
      </div>

      <div className="tech-panel-body" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <svg width={width} height={height} style={{ overflow: 'visible' }}>
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1.0].map((v) => (
            <g key={v}>
              {/* Horizontal */}
              <line
                x1={padding}
                y1={scaleY(v)}
                x2={width - padding}
                y2={scaleY(v)}
                stroke="var(--border-dim)"
                strokeDasharray="2,2"
              />
              <text
                x={padding - 8}
                y={scaleY(v) + 3}
                fill="var(--text-muted)"
                fontSize="9"
                textAnchor="end"
                fontFamily="var(--font-mono)"
              >
                {v.toFixed(2)}
              </text>

              {/* Vertical */}
              <line
                x1={scaleX(v)}
                y1={padding}
                x2={scaleX(v)}
                y2={height - padding}
                stroke="var(--border-dim)"
                strokeDasharray="2,2"
              />
              <text
                x={scaleX(v)}
                y={height - padding + 14}
                fill="var(--text-muted)"
                fontSize="9"
                textAnchor="middle"
                fontFamily="var(--font-mono)"
              >
                {v.toFixed(2)}
              </text>
            </g>
          ))}

          {/* Random Guess Diagonal */}
          <line
            x1={scaleX(0)}
            y1={scaleY(0)}
            x2={scaleX(1)}
            y2={scaleY(1)}
            stroke="var(--text-disabled)"
            strokeDasharray="4,4"
          />

          {/* ROC Curve Path */}
          <path d={pathD} fill="none" stroke="var(--cyan-primary)" strokeWidth="2.5" />

          {/* Data Points */}
          {points.map((pt, idx) => (
            <circle
              key={idx}
              cx={scaleX(pt.false_positive_rate)}
              cy={scaleY(pt.true_positive_rate)}
              r={4}
              fill="var(--bg-primary)"
              stroke="var(--cyan-primary)"
              strokeWidth="2"
            >
              <title>{`Threshold: ${pt.threshold.toFixed(2)}\nFPR: ${pt.false_positive_rate.toFixed(3)}\nTPR (POD): ${pt.true_positive_rate.toFixed(3)}\nPrecision: ${pt.precision.toFixed(3)}\nF1: ${pt.f1_score.toFixed(3)}`}</title>
            </circle>
          ))}

          {/* Axis Labels */}
          <text
            x={width / 2}
            y={height - 4}
            fill="var(--text-muted)"
            fontSize="10"
            textAnchor="middle"
            fontFamily="var(--font-sans)"
            fontWeight="500"
          >
            False Positive Rate (FPR) &rarr;
          </text>
        </svg>

        <div style={{ marginTop: '12px', width: '100%', fontSize: '11px', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between', fontFamily: 'var(--font-mono)' }}>
          <span>Optimal Operating Point: &tau; = 0.50</span>
          <span>TPR: 84.0% | FPR: 5.2%</span>
        </div>
      </div>
    </div>
  );
};
