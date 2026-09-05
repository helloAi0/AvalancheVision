import React, { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { Compass, Mountain, Activity } from 'lucide-react';

interface Map3DWorkspaceProps {
  geojson: any;
  onSelectFeature: (feature: any) => void;
  onTransectCreated: (coords: number[][]) => void;
  hoveredProfileCoord?: { lat: number; lon: number } | null;
}

export const Map3DWorkspace: React.FC<Map3DWorkspaceProps> = ({
  geojson,
  onSelectFeature,
  onTransectCreated,
  hoveredProfileCoord,
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const hoverMarkerRef = useRef<maplibregl.Marker | null>(null);

  const [pitch, setPitch] = useState<number>(60);
  const [bearing, setBearing] = useState<number>(-20);
  const [isDrawingTransect, setIsDrawingTransect] = useState<boolean>(false);
  const [transectPoints, setTransectPoints] = useState<number[][]>([]);

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'esri-satellite': {
            type: 'raster',
            tiles: [
              'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            ],
            tileSize: 256,
            attribution: 'Esri World Imagery',
          },
          'terrarium-dem': {
            type: 'raster-dem',
            tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],
            tileSize: 256,
            encoding: 'terrarium',
            maxzoom: 15,
          },
        },
        layers: [
          {
            id: 'satellite-layer',
            type: 'raster',
            source: 'esri-satellite',
            minzoom: 0,
            maxzoom: 20,
          },
        ],
        terrain: {
          source: 'terrarium-dem',
          exaggeration: 1.35,
        },
      },
      center: [9.83, 46.81],
      zoom: 12.5,
      pitch: 60,
      bearing: -20,
      maxPitch: 85,
    });

    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');
    map.addControl(new maplibregl.ScaleControl(), 'bottom-left');

    map.on('load', () => {
      map.addSource('avalanche-detections', {
        type: 'geojson',
        data: geojson || { type: 'FeatureCollection', features: [] },
      });

      map.addLayer({
        id: 'detections-fill',
        type: 'fill-extrusion',
        source: 'avalanche-detections',
        paint: {
          'fill-extrusion-color': [
            'interpolate',
            ['linear'],
            ['get', 'confidence_mean'],
            0.5, '#f59e0b',
            0.8, '#ef4444',
          ],
          'fill-extrusion-height': 15,
          'fill-extrusion-opacity': 0.75,
        },
      });

      map.addSource('transect-line', {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: { type: 'LineString', coordinates: [] },
          properties: {},
        },
      });

      map.addLayer({
        id: 'transect-line-layer',
        type: 'line',
        source: 'transect-line',
        paint: {
          'line-color': '#06b6d4',
          'line-width': 4,
          'line-dasharray': [2, 1],
        },
      });
    });

    map.on('rotate', () => setBearing(Math.round(map.getBearing())));
    map.on('pitch', () => setPitch(Math.round(map.getPitch())));

    map.on('click', (e: any) => {
      if (isDrawingTransect) {
        const newPoint = [e.lngLat.lng, e.lngLat.lat];
        setTransectPoints((prev) => {
          const updated = [...prev, newPoint];
          const lineGeoJSON: any = {
            type: 'Feature',
            geometry: { type: 'LineString', coordinates: updated },
            properties: {},
          };
          (map.getSource('transect-line') as maplibregl.GeoJSONSource)?.setData(lineGeoJSON);

          if (updated.length >= 2) {
            onTransectCreated(updated);
          }
          return updated;
        });
      } else {
        const bbox: [maplibregl.PointLike, maplibregl.PointLike] = [
          [e.point.x - 5, e.point.y - 5],
          [e.point.x + 5, e.point.y + 5],
        ];
        const features = map.queryRenderedFeatures(bbox, { layers: ['detections-fill'] });
        if (features.length > 0) {
          onSelectFeature(features[0].properties);
        }
      }
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (mapRef.current && mapRef.current.isStyleLoaded() && geojson) {
      (mapRef.current.getSource('avalanche-detections') as maplibregl.GeoJSONSource)?.setData(geojson);
    }
  }, [geojson]);

  useEffect(() => {
    if (!mapRef.current) return;
    if (hoveredProfileCoord) {
      if (!hoverMarkerRef.current) {
        const el = document.createElement('div');
        el.className = 'w-4 h-4 bg-cyan-400 border-2 border-white rounded-full shadow-lg shadow-cyan-500/50 animate-ping';
        hoverMarkerRef.current = new maplibregl.Marker({ element: el })
          .setLngLat([hoveredProfileCoord.lon, hoveredProfileCoord.lat])
          .addTo(mapRef.current);
      } else {
        hoverMarkerRef.current.setLngLat([hoveredProfileCoord.lon, hoveredProfileCoord.lat]);
      }
    } else if (hoverMarkerRef.current) {
      hoverMarkerRef.current.remove();
      hoverMarkerRef.current = null;
    }
  }, [hoveredProfileCoord]);

  const clearTransect = () => {
    setTransectPoints([]);
    if (mapRef.current) {
      (mapRef.current.getSource('transect-line') as maplibregl.GeoJSONSource)?.setData({
        type: 'Feature',
        geometry: { type: 'LineString', coordinates: [] },
        properties: {},
      });
    }
  };

  return (
    <div style={{ height: '80vh', minHeight: '700px', width: '100%', position: 'relative' }}>
      <div className="relative w-full h-full bg-slate-950 rounded-lg overflow-hidden border border-slate-800">
        <div
          ref={mapContainer}
          className="w-full h-full"
          style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}
        />
      <div className="absolute top-3 left-3 bg-slate-900/90 backdrop-blur-md px-3 py-2 rounded border border-slate-700/60 text-xs font-mono text-slate-300 flex items-center gap-4 z-10 shadow-lg">
        <div className="flex items-center gap-1.5">
          <Mountain className="w-3.5 h-3.5 text-cyan-400" />
          <span>Pitch: <strong className="text-white">{pitch}°</strong></span>
        </div>
        <div className="flex items-center gap-1.5">
          <Compass className="w-3.5 h-3.5 text-cyan-400" />
          <span>Bearing: <strong className="text-white">{bearing}°</strong></span>
        </div>
      </div>
      <div className="absolute top-3 right-14 bg-slate-900/90 backdrop-blur-md p-1.5 rounded border border-slate-700/60 flex items-center gap-2 z-10">
        <button
          onClick={() => setIsDrawingTransect(!isDrawingTransect)}
          className={`px-3 py-1.5 text-xs font-mono rounded flex items-center gap-1.5 transition-colors ${
            isDrawingTransect
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          {isDrawingTransect ? 'Click Map to Draw Path' : 'Draw Transect'}
        </button>
        {transectPoints.length > 0 && (
          <button
            onClick={clearTransect}
            className="px-2 py-1.5 text-xs font-mono bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 rounded border border-rose-500/40"
          >
            Clear
          </button>
        )}
      </div>
      </div>
    </div>
  );
};