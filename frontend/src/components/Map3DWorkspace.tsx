import React, { useState, useCallback, useMemo } from 'react';
import Map, { Source, Layer, MapLayerMouseEvent } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import { fetchTerrainProfile, TransectPoint } from '../api/terrainClient';
import { TerrainProfileChart } from './TerrainProfileChart';

export const Map3DWorkspace: React.FC = () => {
  const [transectCoords, setTransectCoords] = useState<number[][]>([]);
  const [profileData, setProfileData] = useState<TransectPoint[]>([]);
  const [isDrawing, setIsDrawing] = useState(false);

  const detectionLayerStyle = {
    id: 'avalanche-detections',
    type: 'fill',
    paint: {
      'fill-color': '#ff0000',
      'fill-opacity': 0.4,
      'fill-outline-color': '#8b0000'
    }
  } as const;

  const transectLineGeoJSON = useMemo(() => ({
    type: 'FeatureCollection',
    features: transectCoords.length > 1 ? [{
      type: 'Feature',
      geometry: { type: 'LineString', coordinates: transectCoords },
      properties: {}
    }] : []
  }), [transectCoords]);

  const handleMapClick = useCallback(async (event: MapLayerMouseEvent) => {
    if (!isDrawing) return;

    const newCoord = [event.lngLat.lng, event.lngLat.lat];
    const updatedCoords = [...transectCoords, newCoord];
    setTransectCoords(updatedCoords);

    if (updatedCoords.length >= 2) {
      try {
        const response = await fetchTerrainProfile(updatedCoords, 50);
        setProfileData(response.profile);
      } catch (error) {
        console.error("Failed to fetch terrain profile", error);
      }
    }
  }, [isDrawing, transectCoords]);

  return (
    // CRITICAL FIX 1: Replaced h-screen with h-full and min-h-[800px] to prevent tab collapse
    <div className="flex flex-col h-full min-h-[800px] w-full relative bg-gray-50">
      <div className="absolute top-4 left-4 z-10 bg-white p-2 rounded shadow flex gap-2">
        <button 
          onClick={() => {
            setIsDrawing(!isDrawing);
            if (!isDrawing) {
              setTransectCoords([]);
              setProfileData([]);
            }
          }}
          className={`px-4 py-2 rounded font-semibold transition-colors ${
            isDrawing ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          {isDrawing ? 'Stop Drawing' : 'Draw Transect'}
        </button>
        {transectCoords.length > 0 && (
          <button 
            onClick={() => { setTransectCoords([]); setProfileData([]); }}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded font-medium"
          >
            Clear Line
          </button>
        )}
      </div>

      <div className="flex-grow relative w-full h-full">
        <Map
          style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}
          initialViewState={{
            longitude: 9.831,
            latitude: 46.801,
            zoom: 12,
            pitch: 45,
            bearing: 0
          }}
          mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
          terrain={{ source: 'mapbox-dem', exaggeration: 1.5 }}
          onClick={handleMapClick}
          interactiveLayerIds={isDrawing ? [] : ['avalanche-detections']}
        >
          <Source 
            id="mapbox-dem" 
            type="raster-dem" 
            // CRITICAL FIX 2: Valid MapLibre DEM TileJSON endpoint
            url="https://demotiles.maplibre.org/terrain-tiles/tiles.json" 
            tileSize={256} 
            maxzoom={14} 
          />

          <Source id="detections-data" type="geojson" data="/api/v1/detections/geojson">
            <Layer {...detectionLayerStyle} />
          </Source>

          <Source id="transect-line" type="geojson" data={transectLineGeoJSON as any}>
            <Layer 
              id="transect-line-layer" 
              type="line" 
              paint={{ 'line-color': '#0000ff', 'line-width': 4 }} 
            />
          </Source>
        </Map>
      </div>

      <div className="absolute bottom-4 left-4 right-4 z-10 max-w-4xl mx-auto w-full">
        <TerrainProfileChart data={profileData} />
      </div>
    </div>
  );
};