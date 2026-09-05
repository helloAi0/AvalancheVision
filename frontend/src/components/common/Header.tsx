import React from 'react';
import { Mountain, Database, Layers, Radio } from 'lucide-react';
import { SystemHealthResponse } from '../../types';

interface HeaderProps {
  health: SystemHealthResponse | null;
  onNavigateLanding: () => void;
}

export const Header: React.FC<HeaderProps> = ({ health, onNavigateLanding }) => {
  return (
    <header className="global-header">
      <div className="brand-section" onClick={onNavigateLanding} title="Return to Overview">
        <div className="brand-logo-icon">
          <Mountain size={18} strokeWidth={2.2} />
        </div>
        <div className="brand-title-group">
          <h1>
            AvalancheVision
            <span style={{ fontSize: '10px', color: 'var(--cyan-primary)', border: '1px solid var(--border-accent)', padding: '1px 5px', borderRadius: '2px', fontWeight: 600 }}>
              SCIENTIFIC v1.0
            </span>
          </h1>
          <span className="subtitle">MULTIMODAL SATELLITE DEBRIS DETECTOR &bull; SWISS ALPS</span>
        </div>
      </div>

      <div className="header-status-group">
        <div className="header-telemetry-badge active-indicator" title="Active Region of Interest">
          <span style={{ color: 'var(--text-muted)' }}>ROI:</span>
          <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
            {health?.active_aoi?.name || 'Davos Flüela Pass (CH)'}
          </span>
        </div>

        <div className="header-telemetry-badge" title="Active Multimodal ML Model">
          <Layers size={13} style={{ color: 'var(--cyan-primary)' }} />
          <span>{health?.active_model || 'U-Net-10Band-v1.0'}</span>
        </div>

        <div className="header-telemetry-badge" title="Database Mode">
          <Database size={13} style={{ color: 'var(--terrain-emerald)' }} />
          <span>{health?.database_type || 'PostGIS / Standalone'}</span>
        </div>

        <div className="header-telemetry-badge" title="PyTorch Compute Device">
          <Radio size={13} style={{ color: health?.cuda_available ? 'var(--terrain-emerald)' : 'var(--hazard-amber)' }} />
          <span>{health?.device || 'CPU'}</span>
        </div>
      </div>
    </header>
  );
};
