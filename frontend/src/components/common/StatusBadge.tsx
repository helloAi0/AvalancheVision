import React from 'react';

interface StatusBadgeProps {
  status: string;
  variant?: 'very-high' | 'high' | 'moderate' | 'completed' | 'running' | 'queued';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, variant }) => {
  let finalVariant = variant;
  if (!finalVariant) {
    const s = status.toUpperCase();
    if (s.includes('VERY HIGH')) finalVariant = 'very-high';
    else if (s.includes('HIGH')) finalVariant = 'high';
    else if (s.includes('MODERATE')) finalVariant = 'moderate';
    else if (s.includes('COMPLETED') || s.includes('PROCESSED') || s.includes('HEALTHY')) finalVariant = 'completed';
    else if (s.includes('RUNNING') || s.includes('INITIALIZING')) finalVariant = 'running';
    else finalVariant = 'queued';
  }

  return <span className={`status-badge ${finalVariant}`}>{status}</span>;
};
