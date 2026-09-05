import React, { useState } from 'react';
import { Modal } from '../common/Modal';
import { Play } from 'lucide-react';

interface NewJobModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: {
    aoi_id: string;
    pre_event_date: string;
    post_event_date: string;
    model_version: string;
    confidence_threshold: number;
    min_cluster_area_m2: number;
    apply_physics_filter: boolean;
  }) => void;
}

export const NewJobModal: React.FC<NewJobModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [aoiId, setAoiId] = useState('davos-fluela');
  const [preDate, setPreDate] = useState('2024-01-03');
  const [postDate, setPostDate] = useState('2024-01-10');
  const [threshold, setThreshold] = useState(0.45);
  const [minArea, setMinArea] = useState(200);
  const [applyPhysics, setApplyPhysics] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      aoi_id: aoiId,
      pre_event_date: preDate,
      post_event_date: postDate,
      model_version: 'U-Net-10Band-v1.0',
      confidence_threshold: threshold,
      min_cluster_area_m2: minArea,
      apply_physics_filter: applyPhysics,
    });
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Launch Multimodal Avalanche Detection Pipeline"
      footer={
        <>
          <button className="btn-secondary" onClick={onClose} type="button">
            Cancel
          </button>
          <button className="btn-primary" onClick={handleSubmit} type="button">
            <Play size={14} />
            <span>Submit Processing Run</span>
          </button>
        </>
      }
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
            Target Region of Interest (AOI)
          </label>
          <select
            value={aoiId}
            onChange={(e) => setAoiId(e.target.value)}
            style={{ width: '100%', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-medium)', color: 'var(--text-primary)', padding: '8px 12px', borderRadius: '4px', fontSize: '12px' }}
          >
            <option value="davos-fluela">Davos Flüela Pass &ndash; Swiss Alps (Sentinel-1 ARD Ready)</option>
            <option value="zermatt-matterhorn" disabled>Zermatt Matterhorn &ndash; Pending SAR Ingest</option>
            <option value="mont-blanc" disabled>Mont Blanc Massif &ndash; Pending SAR Ingest</option>
          </select>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
              T1 Pre-Event Sentinel-1 SAR
            </label>
            <input
              type="date"
              value={preDate}
              onChange={(e) => setPreDate(e.target.value)}
              style={{ width: '100%', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-medium)', color: 'var(--text-primary)', padding: '8px 12px', borderRadius: '4px', fontSize: '12px', fontFamily: 'var(--font-mono)' }}
            />
          </div>
          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
              T2 Post-Event Sentinel-1 SAR
            </label>
            <input
              type="date"
              value={postDate}
              onChange={(e) => setPostDate(e.target.value)}
              style={{ width: '100%', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-medium)', color: 'var(--text-primary)', padding: '8px 12px', borderRadius: '4px', fontSize: '12px', fontFamily: 'var(--font-mono)' }}
            />
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            <span>Model Probability Threshold</span>
            <span style={{ color: 'var(--cyan-primary)', fontFamily: 'var(--font-mono)' }}>{Math.round(threshold * 100)}%</span>
          </div>
          <input
            type="range"
            min="0.20"
            max="0.85"
            step="0.05"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            style={{ width: '100%', accentColor: 'var(--cyan-primary)' }}
          />
        </div>

        <div>
          <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
            Min Cluster Surface Area (m²)
          </label>
          <input
            type="number"
            min="50"
            max="2000"
            step="50"
            value={minArea}
            onChange={(e) => setMinArea(parseInt(e.target.value))}
            style={{ width: '100%', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-medium)', color: 'var(--text-primary)', padding: '8px 12px', borderRadius: '4px', fontSize: '12px', fontFamily: 'var(--font-mono)' }}
          />
          <span style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
            Filters isolated single-pixel radar speckle artifacts below {minArea} m² (~{(minArea / 100).toFixed(0)} pixels).
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px', backgroundColor: 'var(--bg-secondary)', borderRadius: '4px', border: '1px solid var(--border-dim)' }}>
          <input
            type="checkbox"
            id="chk-physics"
            checked={applyPhysics}
            onChange={(e) => setApplyPhysics(e.target.checked)}
            style={{ accentColor: 'var(--cyan-primary)', cursor: 'pointer' }}
          />
          <label htmlFor="chk-physics" style={{ fontSize: '12px', color: 'var(--text-primary)', cursor: 'pointer' }}>
            Enforce Copernicus DEM Slope Constraints ($15^\circ \le \theta \le 55^\circ$)
          </label>
        </div>
      </form>
    </Modal>
  );
};
