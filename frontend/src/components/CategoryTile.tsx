import React, { useMemo } from 'react';
import type { BatchTimeseriesItem } from '../types';
import TimeSeriesChart from './TimeSeriesChart';

interface CategoryTileProps {
    tag: string;
    label: string;
    color: string;
    data?: BatchTimeseriesItem;
    loading?: boolean;
}

const CategoryTile: React.FC<CategoryTileProps> = ({ tag: _tag, label, color, data, loading = false }) => {
    const timeseriesData = data?.timeseries ?? [];
    const totalCount = data?.total ?? 0;

    const trend = useMemo(() => {
        if (timeseriesData.length < 2) return 'stable' as const;

        const mid = Math.floor(timeseriesData.length / 2);
        const firstHalf = timeseriesData.slice(0, mid);
        const secondHalf = timeseriesData.slice(mid);

        const firstAvg = firstHalf.reduce((sum, d) => sum + d.count, 0) / firstHalf.length || 0;
        const secondAvg = secondHalf.reduce((sum, d) => sum + d.count, 0) / secondHalf.length || 0;

        if (secondAvg > firstAvg * 1.1) return 'up' as const;
        if (secondAvg < firstAvg * 0.9) return 'down' as const;
        return 'stable' as const;
    }, [timeseriesData]);

    const trendIcon = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→';
    const trendColor = trend === 'up' ? '#FF6B6B' : trend === 'down' ? '#95E1D3' : '#AAAAAA';

    // Determine tile size based on volume (simple: small, medium, large)
    const getTileSize = () => {
        if (totalCount > 100) return 'col-span-2 row-span-2';
        if (totalCount > 50) return 'col-span-2 row-span-1';
        return 'col-span-1 row-span-1';
    };

    return (
        <div
            className={`${getTileSize()} bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-all`}
            style={{ borderColor: `${color}33` }}
        >
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <div>
                    <h3 className="text-lg font-semibold" style={{ color }}>
                        {label}
                    </h3>
                    <p className="text-sm text-gray-400">
                        {totalCount} incidents
                    </p>
                </div>
                <div className="text-2xl" style={{ color: trendColor }}>
                    {trendIcon}
                </div>
            </div>

            {/* Mini Chart */}
            {loading ? (
                <div className="h-32 flex items-center justify-center text-gray-500">
                    Loading...
                </div>
            ) : timeseriesData.length > 0 ? (
                <TimeSeriesChart
                    data={timeseriesData}
                    height={128}
                    showPoints={false}
                    fill={true}
                />
            ) : (
                <div className="h-32 flex items-center justify-center text-gray-500">
                    No data
                </div>
            )}
        </div>
    );
};

export default CategoryTile;
