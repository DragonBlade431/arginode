import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon in React-Leaflet
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerIcon2x,
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
});

function RecenterMap({ lat, lon }) {
  const map = useMap();
  useEffect(() => {
    if (lat && lon) {
      map.setView([lat, lon], 7);
      // Force map to recalculate size after a small delay
      setTimeout(() => {
        map.invalidateSize();
      }, 100);
    }
  }, [lat, lon, map]);
  return null;
}

export default function MapDisplay({ lat, lon, state }) {
  const position = [lat || 13.165, lon || 77.514];

  return (
    <div className="map-container-wrapper" style={{ height: '400px', width: '100%', borderRadius: '24px', overflow: 'hidden', border: '1px solid var(--border)', background: '#f1f5f9' }}>
      <MapContainer 
        center={position} 
        zoom={5} 
        scrollWheelZoom={false} 
        style={{ height: '400px', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {lat && lon && (
          <>
            <Marker position={[lat, lon]}>
              <Popup>
                <b>Field Location</b><br />
                {state || "Detected Region"}
              </Popup>
            </Marker>
            <RecenterMap lat={lat} lon={lon} />
          </>
        )}
      </MapContainer>
    </div>
  );
}
