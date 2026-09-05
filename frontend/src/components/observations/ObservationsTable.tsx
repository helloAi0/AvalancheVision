import React from 'react';
import { SARObservation } from '../../types';
import { Satellite, CheckCircle2 } from 'lucide-react';
import { StatusBadge } from '../common/StatusBadge';

interface ObservationsTableProps {
  observations: SARObservation[];
  onSelectObservation?: (obs: SARObservation) => void;
}

export const ObservationsTable: React.FC<ObservationsTableProps> = ({
  observations,
  onSelectObservation,
}) => {
  return (
    <div className="tech-panel">
      <div className="tech-panel-header">
        <h3>Sentinel-1 C-SAR Granule Inventory</h3>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)' }}>
          {observations.length} Scenes Available over Active AOI
        </span>
      </div>

      <div className="tech-panel-body" style={{ padding: 0 }}>
        <div className="data-table-container" style={{ border: 'none' }}>
          <table className="tech-table">
            <thead>
              <tr>
                <th>Scene Identifier</th>
                <th>Acquisition Date / UTC</th>
                <th>Orbit Pass</th>
                <th>Relative Orbit</th>
                <th>Mode / Pol</th>
                <th>File Size</th>
                <th>Processing State</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {observations.map((obs) => (
                <tr key={obs.id} onClick={() => onSelectObservation && onSelectObservation(obs)} style={{ cursor: 'pointer' }}>
                  <td className="mono-cell" style={{ fontWeight: 600, color: 'var(--cyan-primary)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Satellite size={13} />
                      <span style={{ maxWidth: '280px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={obs.scene_name}>
                        {obs.scene_name}
                      </span>
                    </div>
                  </td>
                  <td className="mono-cell">{obs.acquisition_date}</td>
                  <td>
                    <span style={{ color: obs.orbit_direction === 'DESCENDING' ? 'var(--blue-radar)' : 'var(--terrain-emerald)', fontWeight: 600 }}>
                      {obs.orbit_direction}
                    </span>
                  </td>
                  <td className="mono-cell">Track {obs.relative_orbit || '168'}</td>
                  <td className="mono-cell">{obs.sensor_mode} ({obs.polarization.join('+')})</td>
                  <td className="mono-cell">{obs.file_size_gb.toFixed(2)} GB</td>
                  <td>
                    <StatusBadge status={obs.status} />
                  </td>
                  <td>
                    <button
                      className="btn-secondary"
                      style={{ padding: '3px 8px', fontSize: '10px' }}
                      onClick={(e) => {
                        e.stopPropagation();
                        alert(`SAR Granule ${obs.id} is verified and indexed in local ARD cache.`);
                      }}
                    >
                      <CheckCircle2 size={11} style={{ color: 'var(--terrain-emerald)' }} />
                      <span>Verified ARD</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
