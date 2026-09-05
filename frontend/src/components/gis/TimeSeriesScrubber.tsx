import React from 'react';

interface TimeSeriesScrubberProps {
  startDate: string;
  endDate: string;
  minDate: string;
  maxDate: string;
  onChange: (range: { startDate: string; endDate: string }) => void;
}

export const TimeSeriesScrubber: React.FC<TimeSeriesScrubberProps> = ({
  startDate,
  endDate,
  minDate,
  maxDate,
  onChange,
}) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
    <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
      SAR window T1 to T2
    </span>
    <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px' }}>
      T1
      <input
        type="date"
        min={minDate}
        max={endDate || maxDate}
        value={startDate}
        onChange={(event) => onChange({ startDate: event.target.value, endDate })}
      />
    </label>
    <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px' }}>
      T2
      <input
        type="date"
        min={startDate || minDate}
        max={maxDate}
        value={endDate}
        onChange={(event) => onChange({ startDate, endDate: event.target.value })}
      />
    </label>
  </div>
);