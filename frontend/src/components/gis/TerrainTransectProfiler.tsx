import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { Mountain, Activity } from 'lucide-react';

interface TransectPoint {
  distance_m: number;
  longitude: number;
  latitude: number;
  elevation_m: number;
  slope_degrees: number;
  delta_vh_db: number;
}

interface TerrainTransectProfilerProps {
  profileData: TransectPoint[];
  onHoverPoint?: (coord: { lat: number; lon: number } | null) => void;
}

export const TerrainTransectProfiler: React.FC<TerrainTransectProfilerProps> = ({
  profileData,
  onHoverPoint,
}) => {
  if (!profileData || profileData.length === 0) {
    return (
      <div className="w-full h-48 bg-slate-900/80 border border-slate-800 rounded-lg p-6 flex flex-col items-center justify-center text-slate-500 text-xs font-mono">
        <Activity className="w-6 h-6 mb-2 text-slate-600 animate-pulse" />
        <span>No active terrain transect profile selected.</span>
        <span className="text-slate-600 mt-1">Activate 'Draw Transect' in the 3D Workstation to sample mountain cross-sections.</span>
      </div>
    );
  }

  return (
    <div className="w-full bg-slate-900/90 border border-slate-800 rounded-lg p-4 font-mono">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Mountain className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-200 tracking-wider uppercase">
            2D Cross-Sectional Terrain Profile
          </h3>
        </div>
        <div className="flex items-center gap-4 text-[11px] text-slate-400">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 bg-emerald-500/40 border border-emerald-500 rounded-sm" />
            Elevation (m)
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 bg-amber-500 rounded-sm" />
            Slope (deg)
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 bg-cyan-400 rounded-sm" />
            Δσ⁰ VH (dB)
          </span>
        </div>
      </div>

      <div className="h-52 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={profileData}
            onMouseMove={(e: any) => {
              if (e && e.activePayload && e.activePayload.length > 0) {
                const pt = e.activePayload[0].payload;
                onHoverPoint?.({ lat: pt.latitude, lon: pt.longitude });
              }
            }}
            onMouseLeave={() => onHoverPoint?.(null)}
          >
            <defs>
              <linearGradient id="elevationGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="2 2" stroke="#1e293b" />
            <XAxis
              dataKey="distance_m"
              stroke="#64748b"
              fontSize={10}
              tickFormatter={(val) => `${val}m`}
            />
            <YAxis
              yAxisId="elev"
              orientation="left"
              stroke="#10b981"
              fontSize={10}
              domain={['dataMin - 50', 'dataMax + 50']}
              tickFormatter={(val) => `${val}m`}
            />
            <YAxis
              yAxisId="slope"
              orientation="right"
              stroke="#f59e0b"
              fontSize={10}
              domain={[0, 60]}
              tickFormatter={(val) => `${val}°`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                fontSize: '11px',
                color: '#f8fafc',
              }}
              formatter={(value: any, name: any) => {
                if (name === 'elevation_m') return [`${value} m`, 'Elevation'];
                if (name === 'slope_degrees') return [`${value}°`, 'Slope Angle'];
                if (name === 'delta_vh_db') return [`${value} dB`, 'Radar Backscatter Drop'];
                return [value, name as string];
              }}
            />
            <Area
              yAxisId="elev"
              type="monotone"
              dataKey="elevation_m"
              stroke="#10b981"
              fill="url(#elevationGrad)"
              strokeWidth={2}
            />
            <Line
              yAxisId="slope"
              type="monotone"
              dataKey="slope_degrees"
              stroke="#f59e0b"
              dot={false}
              strokeWidth={1.5}
            />
            <Line
              yAxisId="slope"
              type="monotone"
              dataKey="delta_vh_db"
              stroke="#06b6d4"
              dot={false}
              strokeDasharray="3 3"
              strokeWidth={1.5}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};