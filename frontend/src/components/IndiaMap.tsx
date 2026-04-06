import { geoCentroid, geoMercator, geoPath } from 'd3-geo';
import type { Feature, FeatureCollection } from 'geojson';
import React, { useEffect, useMemo, useState } from 'react';
import { eventsApi, type GeographicQuery } from '../api/events';
import rawGeoJson from '../assets/india-states.json';
import type { GeographicDataPoint } from '../types';

// Cast the imported JSON to a proper GeoJSON FeatureCollection
const indiaFC = rawGeoJson as unknown as FeatureCollection;

// The GeoJSON uses older names for some states — map them to our DB names.
const GEOJSON_TO_DB: Record<string, string[]> = {
    'Andhra Pradesh': ['Andhra Pradesh', 'Telangana'], // pre-2014 boundary
    'Jammu and Kashmir': ['Jammu and Kashmir', 'Jammu And Kashmir', 'Ladakh'],
    'Uttarakhand': ['Uttarakhand'],
    'Odisha': ['Odisha'],
};

// Reverse: DB state name → GeoJSON feature name
const DB_TO_GEOJSON: Record<string, string> = {};
for (const [geoName, dbNames] of Object.entries(GEOJSON_TO_DB)) {
    for (const db of dbNames) {
        DB_TO_GEOJSON[db] = geoName;
    }
}

// SVG dimensions
const WIDTH = 500;
const HEIGHT = 520;

interface IndiaMapProps {
    startDate: string;
    endDate: string;
}

const IndiaMap: React.FC<IndiaMapProps> = ({ startDate, endDate }) => {
    const [geoData, setGeoData] = useState<GeographicDataPoint[]>([]);
    const [hoveredState, setHoveredState] = useState<string | null>(null);
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const fetchGeo = async () => {
            try {
                const query: GeographicQuery = {
                    start_date: startDate,
                    end_date: endDate,
                    granularity: 'state',
                };
                const resp = await eventsApi.getGeographic(query);
                setGeoData(resp.geographic);
            } catch (err) {
                console.error('Failed to fetch geographic data:', err);
            }
        };
        fetchGeo();
    }, [startDate, endDate]);

    // Aggregate counts per GeoJSON feature name
    const countByGeoFeature = useMemo(() => {
        const map: Record<string, number> = {};
        for (const d of geoData) {
            const geoName = DB_TO_GEOJSON[d.state] || d.state;
            map[geoName] = (map[geoName] || 0) + d.count;
        }
        return map;
    }, [geoData]);

    // Also keep a DB-name lookup for tooltip breakdown
    const countByDbState = useMemo(() => {
        const map: Record<string, number> = {};
        for (const d of geoData) {
            map[d.state] = (map[d.state] || 0) + d.count;
        }
        return map;
    }, [geoData]);

    // d3-geo projection — fit India into our SVG viewBox
    const projection = useMemo(
        () =>
            geoMercator().fitExtent(
                [
                    [20, 20],
                    [WIDTH - 20, HEIGHT - 20],
                ],
                indiaFC,
            ),
        [],
    );

    const pathGen = useMemo(() => geoPath(projection), [projection]);

    // Centroids for placing count-dot labels
    const centroids = useMemo(() => {
        const map: Record<string, [number, number] | null> = {};
        for (const f of indiaFC.features) {
            const name = (f.properties as Record<string, string>)?.name;
            if (!name) continue;
            const c = projection(geoCentroid(f as Feature));
            map[name] = c as [number, number] | null;
        }
        return map;
    }, [projection]);

    if (geoData.length === 0) return null;

    const counts = Object.values(countByGeoFeature);
    const maxCount = Math.max(...counts, 1);
    const minCount = Math.min(...counts.filter((c) => c > 0), 1);

    // Log-scale normalization: spreads values evenly instead of one state dominating
    const getNeonIntensity = (count: number) => {
        if (count <= 0) return 0;
        const logMin = Math.log(minCount);
        const logMax = Math.log(maxCount);
        if (logMax === logMin) return 1;
        return (Math.log(count) - logMin) / (logMax - logMin);
    };
    const getRadius = (count: number) => 3 + 15 * getNeonIntensity(count);

    const features = indiaFC.features;

    return (
        <div className="relative w-full flex justify-center mb-6">
            <svg
                viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
                className="w-full max-w-2xl"
                style={{ maxHeight: '480px' }}
                onMouseMove={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect();
                    setMousePos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
                }}
                onMouseLeave={() => setHoveredState(null)}
            >
                <defs>
                    {/* Neon glow filters — 5 intensity levels */}
                    {[1, 2, 3, 4, 5].map((level) => (
                        <filter
                            key={level}
                            id={`neon-${level}`}
                            x="-50%"
                            y="-50%"
                            width="200%"
                            height="200%"
                        >
                            <feGaussianBlur
                                in="SourceGraphic"
                                stdDeviation={1 + level * 0.6}
                                result="blur"
                            />
                            <feMerge>
                                <feMergeNode in="blur" />
                                <feMergeNode in="blur" />
                                <feMergeNode in="SourceGraphic" />
                            </feMerge>
                        </filter>
                    ))}
                    {/* Dot glow */}
                    <filter id="dot-glow" x="-100%" y="-100%" width="300%" height="300%">
                        <feGaussianBlur stdDeviation="2.5" result="blur" />
                        <feMerge>
                            <feMergeNode in="blur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* ---- State boundaries with neon glow ---- */}
                {features.map((feature: Feature) => {
                    const name = (feature.properties as Record<string, string>)?.name;
                    if (!name) return null;
                    const d = pathGen(feature);
                    if (!d) return null;

                    const count = countByGeoFeature[name] || 0;
                    const intensity = count > 0 ? getNeonIntensity(count) : 0;
                    const neonLevel = count > 0
                        ? Math.min(5, Math.max(1, Math.ceil(intensity * 5)))
                        : 0;
                    const isHovered = hoveredState === name;

                    // Color ramp: dim cyan → bright orange/red
                    const r = Math.round(60 + 195 * intensity);
                    const g = Math.round(220 - 170 * intensity);
                    const b = Math.round(255 - 200 * intensity);
                    const color = count > 0 ? `rgb(${r},${g},${b})` : '#222';
                    const fillOpacity = count > 0 ? 0.04 + 0.12 * intensity : 0.01;

                    return (
                        <path
                            key={name}
                            d={d}
                            fill={count > 0 ? color : '#111'}
                            fillOpacity={isHovered ? Math.min(fillOpacity + 0.15, 0.4) : fillOpacity}
                            stroke={isHovered && count > 0 ? '#fff' : color}
                            strokeWidth={isHovered ? 2 : count > 0 ? 1 : 0.3}
                            filter={count > 0 ? `url(#neon-${neonLevel})` : undefined}
                            className="cursor-pointer transition-all duration-200"
                            onMouseEnter={() => setHoveredState(name)}
                            onMouseLeave={() => setHoveredState(null)}
                        />
                    );
                })}

                {/* ---- Incident count dots at centroids ---- */}
                {features.map((feature: Feature) => {
                    const name = (feature.properties as Record<string, string>)?.name;
                    if (!name) return null;
                    const count = countByGeoFeature[name] || 0;
                    if (count === 0) return null;

                    const centroid = centroids[name];
                    if (!centroid) return null;
                    const [cx, cy] = centroid;
                    const radius = getRadius(count);

                    return (
                        <g key={`dot-${name}`}>
                            <circle
                                cx={cx}
                                cy={cy}
                                r={radius}
                                fill="rgba(239, 68, 68, 0.6)"
                                stroke="rgba(239, 68, 68, 0.85)"
                                strokeWidth="0.8"
                                filter="url(#dot-glow)"
                                className="cursor-pointer"
                                onMouseEnter={() => setHoveredState(name)}
                                onMouseLeave={() => setHoveredState(null)}
                            />
                            {radius > 8 && (
                                <text
                                    x={cx}
                                    y={cy + 1}
                                    textAnchor="middle"
                                    dominantBaseline="central"
                                    fill="white"
                                    fontSize={radius > 14 ? 10 : 8}
                                    fontWeight="bold"
                                    pointerEvents="none"
                                >
                                    {count}
                                </text>
                            )}
                        </g>
                    );
                })}
            </svg>

            {/* ---- Tooltip ---- */}
            {hoveredState && (countByGeoFeature[hoveredState] ?? 0) > 0 && (
                <div
                    className="absolute pointer-events-none bg-[#0a0a0a] border border-[#333] rounded px-3 py-2 text-sm z-50 shadow-lg"
                    style={{
                        left: `${mousePos.x + 14}px`,
                        top: `${mousePos.y - 12}px`,
                    }}
                >
                    <div className="font-semibold text-white">{hoveredState}</div>
                    <div className="text-gray-400">
                        {countByGeoFeature[hoveredState]} incidents
                    </div>
                    {/* Break down if this GeoJSON feature covers multiple DB states */}
                    {GEOJSON_TO_DB[hoveredState] &&
                        GEOJSON_TO_DB[hoveredState].length > 1 && (
                            <div className="mt-1 pt-1 border-t border-[#333] text-xs text-gray-500">
                                {GEOJSON_TO_DB[hoveredState].map((db) =>
                                    countByDbState[db] ? (
                                        <div key={db}>
                                            {db}: {countByDbState[db]}
                                        </div>
                                    ) : null,
                                )}
                            </div>
                        )}
                </div>
            )}
        </div>
    );
};

export default IndiaMap;
