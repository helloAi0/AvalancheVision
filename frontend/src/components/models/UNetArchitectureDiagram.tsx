import React from 'react';

export const UNetArchitectureDiagram: React.FC = () => {
  return (
    <div className="tech-panel">
      <div className="tech-panel-header">
        <h3>U-Net Neural Network Architecture Layout</h3>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)' }}>
          10 Input Channels &rarr; 1 Binary Hazard Channel
        </span>
      </div>

      <div className="tech-panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
          The AvalancheVision architecture is a modified U-Net encoder-decoder network with double convolution blocks, batch normalization, ReLU activations, and skip connections designed to retain high-frequency alpine ridge spatial features while extracting abstract cross-modal backscatter representations.
        </p>

        {/* Visual Pipeline Flow */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px', textAlign: 'center' }}>
          {/* Level 1: Input & Down 1 */}
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-medium)', borderRadius: '4px', padding: '12px' }}>
            <div style={{ fontSize: '10px', color: 'var(--cyan-primary)', fontWeight: 700, textTransform: 'uppercase' }}>Input Stage</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 600, marginTop: '4px' }}>10 &times; 256 &times; 256</div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>DoubleConv(10 &rarr; 64)</div>
          </div>

          {/* Level 2: Down 2 */}
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-medium)', borderRadius: '4px', padding: '12px' }}>
            <div style={{ fontSize: '10px', color: 'var(--blue-radar)', fontWeight: 700, textTransform: 'uppercase' }}>Down 1</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 600, marginTop: '4px' }}>64 &times; 128 &times; 128</div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>MaxPool + DoubleConv(64 &rarr; 128)</div>
          </div>

          {/* Level 3: Bottleneck */}
          <div style={{ backgroundColor: 'rgba(6, 182, 212, 0.12)', border: '1px solid var(--cyan-primary)', borderRadius: '4px', padding: '12px' }}>
            <div style={{ fontSize: '10px', color: 'var(--cyan-primary)', fontWeight: 700, textTransform: 'uppercase' }}>Bottleneck</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 600, marginTop: '4px' }}>256 &times; 64 &times; 64</div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>MaxPool + DoubleConv(128 &rarr; 256)</div>
          </div>

          {/* Level 4: Up 1 */}
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-medium)', borderRadius: '4px', padding: '12px' }}>
            <div style={{ fontSize: '10px', color: 'var(--terrain-emerald)', fontWeight: 700, textTransform: 'uppercase' }}>Up 1 + Skip</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 600, marginTop: '4px' }}>128 &times; 128 &times; 128</div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>ConvTranspose2d + Cat(Down2)</div>
          </div>

          {/* Level 5: Output */}
          <div style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-medium)', borderRadius: '4px', padding: '12px' }}>
            <div style={{ fontSize: '10px', color: 'var(--hazard-crimson)', fontWeight: 700, textTransform: 'uppercase' }}>Output Stage</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 600, marginTop: '4px' }}>1 &times; 256 &times; 256</div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>Conv2d(64 &rarr; 1) + Sigmoid</div>
          </div>
        </div>

        {/* Hyperparameter Table */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginTop: '8px', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
          <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '10px', borderRadius: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Learning Rate:</span>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>2.0e-4 (Cosine Decay)</div>
          </div>
          <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '10px', borderRadius: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Optimizer:</span>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>AdamW (weight_decay=1e-4)</div>
          </div>
          <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '10px', borderRadius: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Loss Objective:</span>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>Weighted BCE + Soft Dice</div>
          </div>
          <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '10px', borderRadius: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Parameter Count:</span>
            <div style={{ fontWeight: 700, color: 'var(--cyan-primary)', marginTop: '2px' }}>7,504,634 weights</div>
          </div>
        </div>
      </div>
    </div>
  );
};
