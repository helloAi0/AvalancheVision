import React from 'react';
import { ModelBenchmarkMetrics } from '../../types';

interface ConfusionMatrixCardProps {
  benchmarks: ModelBenchmarkMetrics;
}

export const ConfusionMatrixCard: React.FC<ConfusionMatrixCardProps> = ({ benchmarks }) => {
  const cm = benchmarks.confusion_matrix;
  const total = (cm.tp || 0) + (cm.fp || 0) + (cm.tn || 0) + (cm.fn || 0) || 1;

  return (
    <div className="tech-panel">
      <div className="tech-panel-header">
        <h3>Spatial Confusion Matrix (Pixel-Level)</h3>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)' }}>
          Threshold &tau; = {benchmarks.optimal_threshold}
        </span>
      </div>

      <div className="tech-panel-body">
        <div style={{ display: 'grid', gridTemplateColumns: '100px 1fr 1fr', gap: '8px', textAlign: 'center', fontSize: '12px' }}>
          {/* Header Row */}
          <div />
          <div style={{ fontWeight: 600, color: 'var(--cyan-primary)', padding: '6px' }}>Predicted Avalanche</div>
          <div style={{ fontWeight: 600, color: 'var(--text-muted)', padding: '6px' }}>Predicted Background</div>

          {/* True Positive Row */}
          <div style={{ fontWeight: 600, color: 'var(--cyan-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            Actual Avalanche
          </div>
          <div style={{ backgroundColor: 'rgba(6, 182, 212, 0.15)', border: '1px solid var(--cyan-primary)', borderRadius: '4px', padding: '12px' }}>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>True Positive (TP)</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '16px', fontWeight: 700, color: 'var(--cyan-primary)', marginTop: '4px' }}>
              {(cm.tp || 0).toLocaleString()}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {(((cm.tp || 0) / total) * 100).toFixed(2)}%
            </div>
          </div>
          <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: '4px', padding: '12px' }}>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>False Negative (FN)</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '16px', fontWeight: 700, color: '#f87171', marginTop: '4px' }}>
              {(cm.fn || 0).toLocaleString()}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {(((cm.fn || 0) / total) * 100).toFixed(2)}%
            </div>
          </div>

          {/* True Negative Row */}
          <div style={{ fontWeight: 600, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            Actual Background
          </div>
          <div style={{ backgroundColor: 'rgba(245, 158, 11, 0.12)', border: '1px solid rgba(245, 158, 11, 0.4)', borderRadius: '4px', padding: '12px' }}>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>False Positive (FP)</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '16px', fontWeight: 700, color: '#fbbf24', marginTop: '4px' }}>
              {(cm.fp || 0).toLocaleString()}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {(((cm.fp || 0) / total) * 100).toFixed(2)}%
            </div>
          </div>
          <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.4)', borderRadius: '4px', padding: '12px' }}>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>True Negative (TN)</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '16px', fontWeight: 700, color: '#6ee7b7', marginTop: '4px' }}>
              {(cm.tn || 0).toLocaleString()}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {(((cm.tn || 0) / total) * 100).toFixed(2)}%
            </div>
          </div>
        </div>

        {/* Metric Summary Bar */}
        <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', fontFamily: 'var(--font-mono)', fontSize: '11px', textAlign: 'center' }}>
          <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '8px', borderRadius: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>IoU / Jaccard:</span>
            <div style={{ fontWeight: 700, color: 'var(--cyan-primary)', fontSize: '13px' }}>{benchmarks.iou}</div>
          </div>
          <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '8px', borderRadius: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>F1 / Dice:</span>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '13px' }}>{benchmarks.f1_score}</div>
          </div>
          <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '8px', borderRadius: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Precision:</span>
            <div style={{ fontWeight: 700, color: 'var(--terrain-emerald)', fontSize: '13px' }}>{benchmarks.precision}</div>
          </div>
          <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '8px', borderRadius: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Recall (POD):</span>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '13px' }}>{benchmarks.recall}</div>
          </div>
        </div>
      </div>
    </div>
  );
};
