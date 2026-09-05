import React, { useState, useEffect } from 'react';
import { TensorBandViewer } from '../components/models/TensorBandViewer';
import { UNetArchitectureDiagram } from '../components/models/UNetArchitectureDiagram';
import { ModelDetails } from '../types';
import { api } from '../services/api';
import { Layers, ShieldAlert, Cpu, CheckCircle2, FileCode } from 'lucide-react';
import { MetricCard } from '../components/common/MetricCard';

export const ModelPage: React.FC = () => {
  const [model, setModel] = useState<ModelDetails | null>(null);

  useEffect(() => {
    const loadModel = async () => {
      try {
        const res = await api.getCurrentModel();
        setModel(res);
      } catch (e) {
        console.error('Failed to load model specs:', e);
      }
    };
    loadModel();
  }, []);

  return (
    <div style={{ padding: 'var(--space-xl)', maxWidth: '1280px', margin: '0 auto', width: '100%' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '20px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Machine Learning Architecture & Model Registry
          </h1>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            10-Channel Multimodal U-Net configured for fused SAR backscatter, Digital Elevation Model gradients, and atmospheric reanalysis.
          </p>
        </div>

        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--cyan-primary)', backgroundColor: 'var(--cyan-subtle)', padding: '6px 12px', borderRadius: '4px', border: '1px solid var(--border-accent)' }}>
          Active Checkpoint: unet_avalanche.pth (7.5 MB)
        </div>
      </div>

      {/* Model Spec Overview */}
      <div className="metric-grid">
        <MetricCard
          label="Model Architecture"
          value="10-Band U-Net"
          subtext="Residual Convolution Blocks"
          icon={<Layers size={14} />}
          accentColor="var(--cyan-primary)"
        />
        <MetricCard
          label="Total Parameters"
          value="7,504,634"
          subtext="PyTorch Float32 Weights"
          icon={<Cpu size={14} />}
          accentColor="var(--blue-radar)"
        />
        <MetricCard
          label="Validation IoU"
          value={model?.benchmarks ? model.benchmarks.iou.toFixed(4) : 'N/A'}
          unit="Jaccard"
          subtext="Measured on Davos Reference"
          icon={<CheckCircle2 size={14} />}
          accentColor="var(--terrain-emerald)"
        />
        <MetricCard
          label="Validation F1 Score"
          value={model?.benchmarks ? model.benchmarks.f1_score.toFixed(4) : 'N/A'}
          unit="Dice"
          subtext="Spatial harmonic mean"
          icon={<FileCode size={14} />}
          accentColor="var(--hazard-amber)"
        />
      </div>

      {/* 10-Band Tensor Specification Table */}
      {model && (
        <div style={{ marginBottom: '32px' }}>
          <TensorBandViewer bands={model.input_bands} />
        </div>
      )}

      {/* U-Net Diagram & Hyperparameters */}
      <div style={{ marginBottom: '32px' }}>
        <UNetArchitectureDiagram />
      </div>

      {/* Explicit Scientific Limitations Statement */}
      <div className="tech-panel">
        <div className="tech-panel-header" style={{ borderBottomColor: 'rgba(245, 158, 11, 0.3)' }}>
          <h3 style={{ color: '#fbbf24' }}>
            <ShieldAlert size={14} />
            <span>Operational Limitations & Research Constraints</span>
          </h3>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)' }}>
            SCIENTIFIC HONESTY MANDATE
          </span>
        </div>

        <div className="tech-panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {model?.limitations ? (
            model.limitations.map((lim, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                <span style={{ color: '#fbbf24', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>[{idx + 1}]</span>
                <span>{lim}</span>
              </div>
            ))
          ) : (
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>No limitations loaded.</p>
          )}
        </div>
      </div>
    </div>
  );
};
