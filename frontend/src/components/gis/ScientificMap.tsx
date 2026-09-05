import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, ImageOverlay, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { DetectionFeature, DetectionGeoJSON } from '../../types';

interface ScientificMapProps {
  geoJsonData: DetectionGeoJSON | null;
  selectedFeature: DetectionFeature | null;
  onSelectFeature: (feature: DetectionFeature | null) => void;
  activeBasemap: 'satellite' | 'topo';
  showObservationFootprint: boolean;
  showAOIBoundary: boolean;
  opacity: number;
  rasterLayerUrl?: string;
  rasterBounds?: [[number, number], [number, number]];
  rasterOpacity?: number;
}

// Coordinate tracking HUD component
const CursorTracker: React.FC = () => {
  const [coords, setCoords] = useState<{ lat: number; lng: number; zoom: number }>({ lat: 46.80, lng: 9.83, zoom: 12 });

  const map = useMapEvents({
    mousemove(e) {
      setCoords({
        lat: Number(e.latlng.lat.toFixed(5)),
        lng: Number(e.latlng.lng.toFixed(5)),
        zoom: map.getZoom(),
      });
    },
    zoomend() {
      setCoords((prev) => ({ ...prev, zoom: map.getZoom() }));
    },
  });

  return (
    <div className="map-hud-overlay">
      <div className="hud-item">
        <span>LAT:</span>
        <span className="hud-val">{coords.lat.toFixed(5)}°N</span>
      </div>
      <div className="hud-item">
        <span>LON:</span>
        <span className="hud-val">{coords.lng.toFixed(5)}°E</span>
      </div>
      <div className="hud-item">
        <span>CRS:</span>
        <span className="hud-val">EPSG:4326 (WGS84)</span>
      </div>
      <div className="hud-item">
        <span>ZOOM:</span>
        <span className="hud-val">{coords.zoom}</span>
      </div>
    </div>
  );
};

// Auto-fitter to center the map when features change
const MapBoundsFitter: React.FC<{ geoJsonData: DetectionGeoJSON | null }> = ({ geoJsonData }) => {
  const map = useMap();
  useEffect(() => {
    if (geoJsonData && geoJsonData.features && geoJsonData.features.length > 0) {
      try {
        const layer = L.geoJSON(geoJsonData as any);
        const bounds = layer.getBounds();
        if (bounds.isValid()) {
          map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
        }
      } catch (e) {
        console.warn('Bounds fit warning:', e);
      }
    }
  }, [geoJsonData, map]);

  return null;
};

export const ScientificMap: React.FC<ScientificMapProps> = ({
  geoJsonData,
  selectedFeature,
  onSelectFeature,
  activeBasemap,
  showObservationFootprint,
  showAOIBoundary,
  opacity,
  rasterLayerUrl,
  rasterBounds,
  rasterOpacity = 0.7,
}) => {
  const defaultCenter: [number, number] = [46.80, 9.83]; // Davos Flüela Pass, Switzerland
  const geoJsonRef = useRef<L.GeoJSON | null>(null);

  // Style function for detection polygons
  const styleFeature = (feature: any) => {
    const isSelected = selectedFeature?.id === feature?.id || selectedFeature?.properties?.detection_id === feature?.properties?.detection_id;
    const conf = feature?.properties?.confidence_score || 0.5;

    let fillColor = '#ef4444'; // Red for High/Very High
    let strokeColor = '#b91c1c';

    if (conf >= 0.80) {
      fillColor = '#dc2626';
      strokeColor = '#7f1d1d';
    } else if (conf < 0.60) {
      fillColor = '#f59e0b';
      strokeColor = '#b45309';
    }

    if (isSelected) {
      return {
        fillColor: '#06b6d4',
        fillOpacity: Math.min(1.0, opacity + 0.35),
        color: '#22d3ee',
        weight: 3,
        dashArray: '',
      };
    }

    return {
      fillColor: fillColor,
      fillOpacity: opacity,
      color: strokeColor,
      weight: 1.5,
    };
  };

  const onEachFeature = (feature: any, layer: L.Layer) => {
    const props = feature.properties || {};
    const tooltipContent = `
      <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; padding: 4px;">
        <strong style="color: #22d3ee;">${props.detection_id || 'DETECTION'}</strong><br/>
        <span>Risk: <b style="color: ${props.risk_level === 'Very High' ? '#f87171' : '#fbbf24'};">${props.risk_level || 'High'}</b></span><br/>
        <span>Confidence: <b>${((props.confidence_score || 0) * 100).toFixed(1)}%</b></span><br/>
        <span>Area: <b>${props.area_ha || 0} ha</b></span><br/>
        <span>Slope: <b>${props.slope_mean_deg || 0}° (${props.aspect_cardinal || 'N'})</b></span><br/>
        <span>Elevation: <b>${props.elevation_mean_m || 0} m</b></span>
      </div>
    `;

    layer.bindTooltip(tooltipContent, { sticky: true, className: 'scientific-map-tooltip' });

    layer.on({
      click: (e) => {
        L.DomEvent.stopPropagation(e);
        onSelectFeature(feature as DetectionFeature);
      },
      mouseover: (e) => {
        const target = e.target;
        if (selectedFeature?.id !== feature?.id) {
          target.setStyle({ weight: 2.5, fillOpacity: Math.min(1.0, opacity + 0.2) });
        }
      },
      mouseout: (e) => {
        const target = e.target;
        if (selectedFeature?.id !== feature?.id) {
          target.setStyle(styleFeature(feature));
        }
      },
    });
  };

  // AOI Davos Bounding Box
  const aoiPolygonGeoJson: any = {
    type: 'Feature',
    properties: { name: 'Davos Flüela Pass AOI' },
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [9.75, 46.75],
        [9.90, 46.75],
        [9.90, 46.88],
        [9.75, 46.88],
        [9.75, 46.75]
      ]]
    }
  };

  return (
    <div className="gis-map-container" id="gis-viewport">
      <MapContainer
        center={defaultCenter}
        zoom={12}
        scrollWheelZoom={true}
        style={{ width: '100%', height: '100%' }}
        attributionControl={false}
      >
        {activeBasemap === 'satellite' ? (
          <TileLayer
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            maxZoom={18}
          />
        ) : (
          <TileLayer
            url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
            maxZoom={17}
          />
        )}

        {/* AOI Bounding Box Layer */}
        {showAOIBoundary && (
          <GeoJSON
            data={aoiPolygonGeoJson}
            style={{
              color: '#06b6d4',
              weight: 1.5,
              fillColor: '#06b6d4',
              fillOpacity: 0.04,
              dashArray: '4, 4',
            }}
          />
        )}

        {/* Sentinel-1 Observation Footprint Layer */}
        {showObservationFootprint && (
          <GeoJSON
            data={{
              type: 'Feature',
              properties: { name: 'Sentinel-1 Track 168 Swath' },
              geometry: {
                type: 'Polygon',
                coordinates: [[
                  [9.72, 46.72],
                  [9.95, 46.72],
                  [9.95, 46.90],
                  [9.72, 46.90],
                  [9.72, 46.72]
                ]]
              }
            } as any}
            style={{
              color: '#38bdf8',
              weight: 1,
              fillColor: '#38bdf8',
              fillOpacity: 0.03,
              dashArray: '6, 6',
            }}
          />
        )}

        {rasterLayerUrl && rasterBounds && (
          <ImageOverlay
            url={rasterLayerUrl}
            bounds={rasterBounds}
            opacity={rasterOpacity}
            interactive={false}
          />
        )}

        {/* Avalanche Deposit Vector Features */}
        {geoJsonData && geoJsonData.features && (
          <GeoJSON
            key={`geojson-${geoJsonData.features.length}-${selectedFeature?.id || 'none'}-${opacity}`}
            ref={geoJsonRef}
            data={geoJsonData as any}
            style={styleFeature}
            onEachFeature={onEachFeature}
          />
        )}

        <MapBoundsFitter geoJsonData={geoJsonData} />
        <CursorTracker />
      </MapContainer>
    </div>
  );
};
