import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  icon?: React.ReactNode;
  accentColor?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  subtext,
  icon,
  accentColor,
}) => {
  return (
    <div className="metric-card" style={accentColor ? { borderTop: `2px solid ${accentColor}` } : {}}>
      <div className="metric-header">
        <span className="metric-label">{label}</span>
        {icon && <span className="metric-icon">{icon}</span>}
      </div>
      <div className="metric-value-row">
        <span className="metric-value">{value}</span>
        {unit && <span className="metric-unit">{unit}</span>}
      </div>
      {subtext && <div className="metric-subtext">{subtext}</div>}
    </div>
  );
};
