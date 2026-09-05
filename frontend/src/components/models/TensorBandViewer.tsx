import React from 'react';
import { InputBandConfig } from '../../types';
import { Radio, Mountain, CloudSnow } from 'lucide-react';

interface TensorBandViewerProps {
  bands: InputBandConfig[];
}

export const TensorBandViewer: React.FC<TensorBandViewerProps> = ({ bands }) => {
  const getModalityBadge = (modality: string) => {
    switch (modality) {
      case 'SAR':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--blue-radar)', backgroundColor: 'rgba(56, 189, 248, 0.1)', padding: '2px 6px', borderRadius: '2px', fontSize: '10px', fontWeight: 600 }}>
            <Radio size={10} /> SAR (Sentinel-1)
          </span>
        );
      case 'DEM':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--terrain-emerald)', backgroundColor: 'rgba(16, 185, 129, 0.1)', padding: '2px 6px', borderRadius: '2px', fontSize: '10px', fontWeight: 600 }}>
            <Mountain size={10} /> DEM (Copernicus)
          </span>
        );
      case 'ERA5':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--topo-violet)', backgroundColor: 'rgba(139, 92, 246, 0.1)', padding: '2px 6px', borderRadius: '2px', fontSize: '10px', fontWeight: 600 }}>
            <CloudSnow size={10} /> ERA5 (ECMWF)
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="tech-panel">
      <div className="tech-panel-header">
        <h3>10-Band Multimodal Input Tensor Specification</h3>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--cyan-primary)' }}>
          Shape: [Batch, 10, 256, 256] @ 10m Ground Resolution
        </span>
      </div>

      <div className="tech-panel-body" style={{ padding: 0 }}>
        <div className="data-table-container" style={{ border: 'none' }}>
          <table className="tech-table">
            <thead>
              <tr>
                <th>Band #</th>
                <th>Channel Name</th>
                <th>Modality / Sensor</th>
                <th>Physical Parameter Description</th>
                <th>Units</th>
                <th>Resolution</th>
              </tr>
            </thead>
            <tbody>
              {bands.map((band) => (
                <tr key={band.index}>
                  <td className="mono-cell" style={{ fontWeight: 700, color: 'var(--cyan-primary)' }}>
                    Band {band.index}
                  </td>
                  <td className="mono-cell" style={{ fontWeight: 600 }}>
                    {band.name}
                  </td>
                  <td>{getModalityBadge(band.modality)}</td>
                  <td>{band.description}</td>
                  <td className="mono-cell" style={{ color: 'var(--text-muted)' }}>
                    {band.units}
                  </td>
                  <td className="mono-cell">{band.resolution_m}m</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
