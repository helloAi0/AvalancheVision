import React from 'react';
import { ProcessingJob } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { CheckCircle2, Clock, AlertCircle, Play, Terminal } from 'lucide-react';

interface JobPipelineTrackerProps {
  job: ProcessingJob | null;
}

export const JobPipelineTracker: React.FC<JobPipelineTrackerProps> = ({ job }) => {
  if (!job) {
    return (
      <div className="tech-panel">
        <div className="tech-panel-body" style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
          Select a processing job to inspect real-time execution progress and terminal logs.
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
      {/* Job Meta Summary */}
      <div className="tech-panel">
        <div className="tech-panel-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', fontWeight: 700, color: 'var(--text-cyan)' }}>
              {job.job_id}
            </span>
            <StatusBadge status={job.status} />
          </div>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)' }}>
            Submitted: {job.submitted_at}
          </span>
        </div>

        <div className="tech-panel-body">
          {/* Progress Bar */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
              <span style={{ color: 'var(--text-muted)' }}>PIPELINE EXECUTION PROGRESS</span>
              <span style={{ color: 'var(--cyan-primary)', fontWeight: 700 }}>{job.progress_percentage}%</span>
            </div>
            <div style={{ height: '6px', backgroundColor: 'var(--bg-surface)', borderRadius: '3px', overflow: 'hidden' }}>
              <div
                style={{
                  height: '100%',
                  width: `${job.progress_percentage}%`,
                  backgroundColor: job.status === 'FAILED' ? 'var(--hazard-crimson)' : 'var(--cyan-primary)',
                  transition: 'width 0.4s ease',
                }}
              />
            </div>
          </div>

          {/* Quick Metrics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
            <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '8px', borderRadius: '4px' }}>
              <span style={{ color: 'var(--text-muted)' }}>AOI Region:</span>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>{job.aoi_name}</div>
            </div>
            <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '8px', borderRadius: '4px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Model Checkpoint:</span>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>{job.model_version}</div>
            </div>
            <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '8px', borderRadius: '4px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Confidence Threshold:</span>
              <div style={{ fontWeight: 600, color: 'var(--cyan-primary)', marginTop: '2px' }}>&ge; {job.confidence_threshold}</div>
            </div>
            <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '8px', borderRadius: '4px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Mapped Polygons:</span>
              <div style={{ fontWeight: 700, color: 'var(--terrain-emerald)', marginTop: '2px' }}>
                {job.output_detections_count !== undefined ? `${job.output_detections_count} deposits (${job.output_area_ha} ha)` : 'Processing...'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stage Progression Flow */}
      <div className="tech-panel">
        <div className="tech-panel-header">
          <h3>Pipeline Execution Stages</h3>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)' }}>
            Duration: {job.execution_duration_sec ? `${job.execution_duration_sec}s` : 'Active'}
          </span>
        </div>

        <div className="tech-panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {job.stages.map((stage, idx) => {
            const isCompleted = stage.status === 'COMPLETED';
            const isRunning = stage.status === 'RUNNING';
            const isFailed = stage.status === 'FAILED';

            return (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  backgroundColor: isRunning ? 'rgba(6, 182, 212, 0.08)' : 'var(--bg-secondary)',
                  border: `1px solid ${isRunning ? 'var(--cyan-primary)' : isFailed ? 'var(--hazard-crimson)' : 'var(--border-dim)'}`,
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '22px', display: 'flex', justifyContent: 'center' }}>
                    {isCompleted && <CheckCircle2 size={16} style={{ color: 'var(--terrain-emerald)' }} />}
                    {isRunning && <Play size={16} style={{ color: 'var(--cyan-primary)' }} />}
                    {isFailed && <AlertCircle size={16} style={{ color: 'var(--hazard-crimson)' }} />}
                    {!isCompleted && !isRunning && !isFailed && (
                      <Clock size={16} style={{ color: 'var(--text-disabled)' }} />
                    )}
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {stage.display_title}
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                      STAGE {idx + 1}: {stage.stage_name}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {stage.duration_seconds && (
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)' }}>
                      {stage.duration_seconds}s
                    </span>
                  )}
                  <StatusBadge status={stage.status} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Raw Log Console */}
      <div className="tech-panel">
        <div className="tech-panel-header">
          <h3>
            <Terminal size={14} style={{ color: 'var(--cyan-primary)' }} />
            <span>Telemetry & Execution Log Output</span>
          </h3>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-muted)' }}>
            STDOUT / STDERR STREAM
          </span>
        </div>

        <div
          style={{
            backgroundColor: '#030712',
            padding: '12px',
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            lineHeight: 1.6,
            maxHeight: '220px',
            overflowY: 'auto',
            color: '#a5f3fc',
          }}
        >
          {job.raw_logs && job.raw_logs.length > 0 ? (
            job.raw_logs.map((log, idx) => (
              <div key={idx} style={{ color: log.includes('ERROR') ? '#f87171' : log.includes('WARNING') ? '#fbbf24' : '#a5f3fc' }}>
                {log}
              </div>
            ))
          ) : (
            <div style={{ color: 'var(--text-muted)' }}>No logs emitted yet.</div>
          )}
        </div>
      </div>
    </div>
  );
};
