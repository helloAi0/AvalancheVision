import React, { useState, useEffect } from 'react';
import { JobPipelineTracker } from '../components/jobs/JobPipelineTracker';
import { NewJobModal } from '../components/jobs/NewJobModal';
import { JobListResponse, ProcessingJob } from '../types';
import { api } from '../services/api';
import { Play, RefreshCw } from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';

export const JobsPage: React.FC = () => {
  const [data, setData] = useState<JobListResponse | null>(null);
  const [selectedJob, setSelectedJob] = useState<ProcessingJob | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [telemetryMode, setTelemetryMode] = useState<'LIVE' | 'POLLING'>('LIVE');

  const loadJobs = async () => {
    try {
      const res = await api.listJobs();
      setData(res);
      if (res.jobs.length > 0) {
        if (!selectedJob) {
          setSelectedJob(res.jobs[0]);
        } else {
          const updated = res.jobs.find((j) => j.job_id === selectedJob.job_id);
          if (updated) setSelectedJob(updated);
        }
      }
    } catch (e) {
      console.error('Failed to list jobs:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  useEffect(() => {
    if (!selectedJob || ['COMPLETED', 'FAILED', 'CANCELLED'].includes(selectedJob.status)) {
      return;
    }

    const socket = new WebSocket(api.getJobWebSocketUrl(selectedJob.job_id));
    let fallbackInterval: number | undefined;
    socket.onopen = () => setTelemetryMode('LIVE');
    socket.onmessage = (event) => {
      const updatedJob = JSON.parse(event.data) as ProcessingJob;
      setSelectedJob(updatedJob);
      setData((current) => current ? {
        ...current,
        jobs: current.jobs.map((job) => job.job_id === updatedJob.job_id ? updatedJob : job),
      } : current);
    };
    socket.onerror = () => {
      setTelemetryMode('POLLING');
      fallbackInterval = window.setInterval(loadJobs, 4000);
    };
    return () => {
      socket.close();
      if (fallbackInterval !== undefined) window.clearInterval(fallbackInterval);
    };
  }, [selectedJob?.job_id, selectedJob?.status]);

  const handleLaunchJob = async (payload: any) => {
    try {
      const newJob = await api.submitJob(payload);
      setSelectedJob(newJob);
      loadJobs();
    } catch (e: any) {
      alert(`Failed to launch job: ${e.message}`);
    }
  };

  return (
    <div style={{ padding: 'var(--space-xl)', maxWidth: '1280px', margin: '0 auto', width: '100%' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '20px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Asynchronous Processing Job Console
          </h1>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Monitor automated satellite data ingestion, DEM terrain extraction, U-Net inference, and PostGIS vectorization tasks.
          </p>
          <div style={{ marginTop: '8px', fontFamily: 'var(--font-mono)', fontSize: '10px', color: telemetryMode === 'LIVE' ? 'var(--terrain-emerald)' : 'var(--hazard-amber)' }}>
            TELEMETRY: {telemetryMode === 'LIVE' ? 'WEBSOCKET STREAM' : 'POLLING FALLBACK'}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn-secondary" onClick={loadJobs} style={{ padding: '6px 12px', fontSize: '11px' }}>
            <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} />
            <span>Refresh Queue</span>
          </button>
          <button className="btn-primary" onClick={() => setIsModalOpen(true)} style={{ padding: '6px 14px', fontSize: '12px' }}>
            <Play size={13} />
            <span>Launch Pipeline Run</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Job History Sidebar + Active Tracker */}
      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: 'var(--space-lg)', alignItems: 'start' }}>
        {/* Job Queue List */}
        <div className="tech-panel">
          <div className="tech-panel-header">
            <h3>Pipeline Job Queue</h3>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)' }}>
              {data?.total_jobs || 0} Runs
            </span>
          </div>

          <div className="tech-panel-body" style={{ padding: 0, maxHeight: '600px', overflowY: 'auto' }}>
            {data?.jobs && data.jobs.length > 0 ? (
              data.jobs.map((job) => {
                const isSelected = selectedJob?.job_id === job.job_id;
                return (
                  <div
                    key={job.job_id}
                    onClick={() => setSelectedJob(job)}
                    style={{
                      padding: '12px 16px',
                      borderBottom: '1px solid var(--border-dim)',
                      cursor: 'pointer',
                      backgroundColor: isSelected ? 'rgba(6, 182, 212, 0.08)' : 'var(--bg-primary)',
                      borderLeft: isSelected ? '3px solid var(--cyan-primary)' : '3px solid transparent',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)' }}>
                        {job.job_id}
                      </span>
                      <StatusBadge status={job.status} />
                    </div>

                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      AOI: {job.aoi_name}
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px', fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                      <span>Stage: {job.current_stage}</span>
                      <span>{job.progress_percentage}%</span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px' }}>
                No processing jobs found in queue.
              </div>
            )}
          </div>
        </div>

        {/* Real-time Execution Tracker & Logs */}
        <JobPipelineTracker job={selectedJob} />
      </div>

      {/* New Job Modal */}
      <NewJobModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleLaunchJob}
      />
    </div>
  );
};
