import React, { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { Sliders } from 'lucide-react';

export const SwipeSARViewer: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const leftMapContainer = useRef<HTMLDivElement>(null);
  const rightMapContainer = useRef<HTMLDivElement>(null);

  const leftMap = useRef<maplibregl.Map | null>(null);
  const rightMap = useRef<maplibregl.Map | null>(null);

  const [sliderPosition, setSliderPosition] = useState<number>(50);
  const isDragging = useRef<boolean>(false);

  useEffect(() => {
    if (!leftMapContainer.current || !rightMapContainer.current) return;

    const mapL = new maplibregl.Map({
      container: leftMapContainer.current,
      style: {
        version: 8,
        sources: {
          'esri-satellite': {
            type: 'raster',
            tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
            tileSize: 256,
          },
        },
        layers: [{ id: 'sat', type: 'raster', source: 'esri-satellite' }],
      },
      center: [9.83, 46.81],
      zoom: 13,
      interactive: true,
    });

    const mapR = new maplibregl.Map({
      container: rightMapContainer.current,
      style: {
        version: 8,
        sources: {
          'opentopo': {
            type: 'raster',
            tiles: ['https://tile.opentopomap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
          },
        },
        layers: [{ id: 'topo', type: 'raster', source: 'opentopo' }],
      },
      center: [9.83, 46.81],
      zoom: 13,
      interactive: true,
    });

    const syncMaps = (source: maplibregl.Map, target: maplibregl.Map) => {
      source.on('move', () => {
        target.jumpTo({
          center: source.getCenter(),
          zoom: source.getZoom(),
          bearing: source.getBearing(),
          pitch: source.getPitch(),
        });
      });
    };

    syncMaps(mapL, mapR);
    syncMaps(mapR, mapL);

    leftMap.current = mapL;
    rightMap.current = mapR;

    return () => {
      mapL.remove();
      mapR.remove();
    };
  }, []);

  const handleMouseDown = () => {
    isDragging.current = true;
  };

  const handleMouseUp = () => {
    isDragging.current = false;
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging.current || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const percent = (x / rect.width) * 100;
    setSliderPosition(percent);
  };

  return (
    <div style={{ height: '80vh', minHeight: '700px', width: '100%', position: 'relative' }}>
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        className="relative w-full h-full bg-slate-950 rounded-lg overflow-hidden border border-slate-800 select-none"
      >
        <div
          className="absolute top-0 left-0 bottom-0 h-full"
          style={{ width: `${sliderPosition}%` }}
        >
          <div
            ref={leftMapContainer}
            style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}
          />
        </div>
        <div
          className="absolute top-0 right-0 bottom-0 h-full"
          style={{ width: `${100 - sliderPosition}%` }}
        >
          <div
            ref={rightMapContainer}
            style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}
          />
        </div>
      <div
        onMouseDown={handleMouseDown}
        className="absolute top-0 bottom-0 w-1 bg-cyan-400 cursor-ew-resize z-20 flex items-center justify-center shadow-lg shadow-cyan-500/50"
        style={{ left: `${sliderPosition}%` }}
      >
        <div className="w-7 h-7 bg-slate-900 border-2 border-cyan-400 rounded-full flex items-center justify-center shadow-md">
          <Sliders className="w-3.5 h-3.5 text-cyan-400" />
        </div>
      </div>
      <div className="absolute top-3 left-3 bg-slate-900/90 border border-slate-700/60 px-2.5 py-1 rounded text-xs font-mono text-cyan-300 z-10">
        Pre-Event SAR (T1)
      </div>
      <div className="absolute top-3 right-3 bg-slate-900/90 border border-slate-700/60 px-2.5 py-1 rounded text-xs font-mono text-amber-300 z-10">
        Post-Event SAR + Hazard Mask (T2)
      </div>
      </div>
    </div>
  );
};