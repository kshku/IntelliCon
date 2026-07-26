import React, { useEffect, useRef } from 'react';

interface MapPin {
  name: string;
  lat: number;
  lng: number;
  count: string;
}

const mapPins: MapPin[] = [
  { name: 'Koramangala', lat: 12.9352, lng: 77.6245, count: '28 cases' },
  { name: 'Whitefield', lat: 12.9698, lng: 77.7500, count: '41 cases' },
  { name: 'Yeshwanthpur', lat: 13.0238, lng: 77.5529, count: '19 cases' },
  { name: 'HSR Layout', lat: 12.9101, lng: 77.6450, count: '22 cases' },
  { name: 'Shivajinagar', lat: 12.9857, lng: 77.6057, count: '35 cases' },
];

export const InteractiveMap: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);

  useEffect(() => {
    // 1. Helper function to load Leaflet resources dynamically from CDN
    const loadLeaflet = async (): Promise<any> => {
      if ((window as any).L) return (window as any).L;

      return new Promise((resolve, reject) => {
        // Load CSS
        if (!document.getElementById('leaflet-css')) {
          const link = document.createElement('link');
          link.id = 'leaflet-css';
          link.rel = 'stylesheet';
          link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
          document.head.appendChild(link);
        }

        // Load JS
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.async = true;
        script.onload = () => resolve((window as any).L);
        script.onerror = () => reject(new Error('Leaflet script failed to load'));
        document.body.appendChild(script);
      });
    };

    loadLeaflet().then((L) => {
      if (!mapContainerRef.current || mapInstanceRef.current) return;

      // Check if it's in dark mode
      const isDarkMode = document.documentElement.classList.contains('dark');
      const tileUrl = isDarkMode
        ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';

      // Create map instance
      const map = L.map(mapContainerRef.current, {
        center: [12.96, 77.64], // Slightly adjusted center to frame all Bengaluru pins beautifully
        zoom: 11,
        zoomControl: false,
        attributionControl: false,
      });

      // Add base map tiles (CartoDB maps are clean and look great in dashboards)
      L.tileLayer(tileUrl, {
        maxZoom: 19,
        subdomains: 'abcd',
      }).addTo(map);

      // Create a DivIcon to support high-quality Tailwind custom styles (pulsing effect)
      const customIcon = L.divIcon({
        className: 'custom-leaflet-marker',
        html: `
          <div class="relative flex items-center justify-center">
            <span class="animate-ping absolute inline-flex h-7 w-7 rounded-full bg-red-400 opacity-60"></span>
            <div class="relative w-4 h-4 rounded-full bg-red-500 border-2 border-white shadow-md flex items-center justify-center">
              <div class="w-1.5 h-1.5 rounded-full bg-white"></div>
            </div>
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
      });

      // Add crime hotspots markers
      mapPins.forEach((pin) => {
        L.marker([pin.lat, pin.lng], { icon: customIcon })
          .addTo(map)
          .bindPopup(`
            <div class="font-sans text-[var(--color-heading-dark)] p-0.5">
              <div class="font-bold text-[14px] leading-tight">${pin.name}</div>
              <div class="text-[12px] text-red-500 font-semibold mt-1">${pin.count}</div>
            </div>
          `);
      });

      // Add zoom control to bottom right
      L.control.zoom({ position: 'bottomright' }).addTo(map);

      mapInstanceRef.current = map;
    }).catch((err) => {
      console.error('Failed to initialize Leaflet Map:', err);
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div className="w-full h-full relative" style={{ minHeight: '260px' }}>
      <div ref={mapContainerRef} className="w-full h-full rounded-custom-lg" />
    </div>
  );
};
