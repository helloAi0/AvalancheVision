import React, { useState, useEffect } from 'react';
import { ObservationsTable } from '../components/observations/ObservationsTable';
import { ObservationListResponse, SARObservation } from '../types';
import { api } from '../services/api';
import { Satellite, Calendar, RefreshCw, Radio, Layers } from 'lucide-react';
import { MetricCard } from '../components/common/MetricCard';

export const ObservationsPage: React.FC = () => {
  const [data, setData] = useState<ObservationListResponse | null>(null);
  const [selectedObs, setSelectedObs] = useState<SARObservation | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [filterSatellite, setFilterSatellite] = useState<string>('');
  const [filterOrbit, setFilterOrbit] = useState<string>('');
  const [catalogSource, setCatalogSource] = useState<'LOCAL' | 'COPERNICUS STAC'>('LOCAL');

  const loadObservations = async (live = false) => {
    setIsLoading(true);
    try {
      const res = await api.getObservations({
        satellite: filterSatellite || undefined,
        orbit_direction: filterOrbit || undefined,
        live,
      });
      setData(res);
      setCatalogSource(live ? 'COPERNICUS STAC' : 'LOCAL');
      if (res.observations.length > 0 && !selectedObs) {
        setSelectedObs(res.observations[0]);
      }
    } catch (e) {
      console.error('Failed to load observations:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadObservations();
  }, [filterSatellite, filterOrbit]);

  return (
    <div style={{ padding: 'var(--space-xl)', maxWidth: '1280px', margin: '0 auto', width: '100%' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '20px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Sentinel-1 SAR Observation Catalogue
          </h1>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            C-SAR satellite radar acquisitions covering Davos Flüela Pass AOI with orbit parameters and polarization modes.
          </p>
        </div>

        <button className="btn-secondary" onClick={() => loadObservations(true)} style={{ padding: '6px 12px', fontSize: '11px' }}>
          <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} />
          <span>Sync STAC Catalog</span>
        </button>
      </div>

      {/* Observation Summary Metrics */}
      <div className="metric-grid">
        <MetricCard
          label="Catalogued Granules"
          value={data?.total_count ?? 0}
          unit="scenes"
          subtext="Covering Swiss Alps Davos AOI"
          icon={<Satellite size={14} />}
          accentColor="var(--cyan-primary)"
        />
        <MetricCard
          label="Active Polarizations"
          value="VV + VH"
          subtext="Dual-pol amplitude & cross-pol"
          icon={<Radio size={14} />}
          accentColor="var(--blue-radar)"
        />
        <MetricCard
          label="Repeat Baseline"
          value="6 &ndash; 12"
          unit="days"
          subtext="Exact repeat orbit pass geometry"
          icon={<Calendar size={14} />}
          accentColor="var(--terrain-emerald)"
        />
        <MetricCard
          label="Ground Resolution"
          value="10.0 &times; 10.0"
          unit="meters"
          subtext="Interferometric Wide (IW) GRD"
          icon={<Layers size={14} />}
          accentColor="var(--topo-violet)"
        />
      </div>

      {/* Filter Row */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '16px', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Satellite:
          </span>
          <select
            value={filterSatellite}
            onChange={(e) => setFilterSatellite(e.target.value)}
            style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', color: 'var(--text-primary)', padding: '4px 8px', borderRadius: '4px', fontSize: '11px' }}
          >
            <option value="">All Satellites</option>
            <option value="Sentinel-1A">Sentinel-1A</option>
            <option value="Sentinel-1B">Sentinel-1B</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Orbit Pass:
          </span>
          <select
            value={filterOrbit}
            onChange={(e) => setFilterOrbit(e.target.value)}
            style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-dim)', color: 'var(--text-primary)', padding: '4px 8px', borderRadius: '4px', fontSize: '11px' }}
          >
            <option value="">All Passes</option>
            <option value="DESCENDING">Descending Pass</option>
            <option value="ASCENDING">Ascending Pass</option>
          </select>
        </div>
      </div>

      {/* Observations Table */}
      <ObservationsTable
        observations={data?.observations || []}
        onSelectObservation={setSelectedObs}
      />

      {/* Granule Detail Section */}
      {selectedObs && (
        <div className="tech-panel" style={{ marginTop: '24px' }}>
          <div className="tech-panel-header">
            <h3>Selected Scene Telemetry: {selectedObs.scene_name}</h3>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: catalogSource === 'COPERNICUS STAC' ? 'var(--terrain-emerald)' : 'var(--text-muted)' }}>
              SOURCE: {catalogSource}
            </span>
          </div>
          <div className="tech-panel-body" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Acquisition Epoch:</span>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedObs.acquisition_date}</div>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Orbit Pass Direction:</span>
              <div style={{ fontWeight: 600, color: 'var(--blue-radar)', marginTop: '2px' }}>{selectedObs.orbit_direction}</div>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Relative Orbit Track:</span>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>Track {selectedObs.relative_orbit}</div>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Polarization Channels:</span>
              <div style={{ fontWeight: 600, color: 'var(--cyan-primary)', marginTop: '2px' }}>{selectedObs.polarization.join(', ')}</div>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Spatial Extents (WGS84):</span>
              <div style={{ fontWeight: 600, color: 'var(--text-secondary)', marginTop: '2px' }}>[{selectedObs.bbox.join(', ')}]</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
