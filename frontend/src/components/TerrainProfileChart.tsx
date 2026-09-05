import React from 'react';
import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { TransectPoint } from '../api/terrainClient';

interface Props {
  data: TransectPoint[];
}

export const TerrainProfileChart: React.FC<Props> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="p-4 text-gray-500 border border-dashed rounded text-center">
        Draw a transect line on the map canvas to generate your terrain profile views.
      </div>
    );
  }

  return (
    <div className="w-full h-64 bg-white p-2 rounded shadow-sm">
      <h3 className="text-sm font-semibold mb-2">Terrain & SAR Profile</h3>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          
          <XAxis 
            dataKey="distance_m" 
            type="number" 
            domain={['dataMin', 'dataMax']} 
            tickFormatter={(val) => `${val.toFixed(0)}m`} 
            fontSize={12}
          />
          
          {/* Left Y-Axis for Elevation */}
          <YAxis 
            yAxisId="elevation" 
            domain={([dataMin, dataMax]) => [dataMin - 50, dataMax + 50]} 
            tickFormatter={(val) => `${val}m`}
            fontSize={12}
          />
          
          {/* Right Y-Axis for SAR Backscatter Anomaly */}
          <YAxis 
            yAxisId="sar" 
            orientation="right" 
            domain={([dataMin, dataMax]) => [dataMin - 5, dataMax + 5]} 
            tickFormatter={(val) => `${val} dB`}
            fontSize={12}
          />

          {/* 🚨 Updated tooltip formatter structure using 'any' to bypass strict Recharts definition collisions */}
          <Tooltip 
            formatter={(value: any, name: any) => [
              name === 'elevation_m' ? `${Number(value).toFixed(1)} m` : `${Number(value).toFixed(2)} dB`, 
              name === 'elevation_m' ? 'Elevation' : 'ΔVH'
            ]}
            labelFormatter={(label: any) => `Distance: ${Number(label).toFixed(1)} m`}
          />
          <Legend />

          <Area 
            yAxisId="elevation" 
            type="monotone" 
            dataKey="elevation_m" 
            name="elevation_m" 
            fill="#8884d8" 
            stroke="#8884d8" 
            fillOpacity={0.3} 
          />
          <Line 
            yAxisId="sar" 
            type="monotone" 
            dataKey="delta_vh_db" 
            name="delta_vh_db" 
            stroke="#ff7300" 
            dot={false} 
            strokeWidth={2}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
