import React, { useEffect, useState } from 'react';
import { eventsApi } from '../api/events';
import { TimeseriesDataPoint } from '../types';
import TimeSeriesChart from './TimeSeriesChart';
import { useAppStore } from '../stores/appStore';
import { getTagColor } from '../utils/chartColors';

interface CategoryTileProps {
  tag: string;
  label: string;
  color: string;
}

const CategoryTile: React.FC<CategoryTileProps> = ({ tag, label, color }) => {
  const { dateRange } = useAppStore();
  const [timeseriesData, setTimeseriesData] = useState<TimeseriesDataPoint[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [trend, setTrend] = useState<'up' | 'down' | 'stable'>('stable');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await eventsApi.getTimeseries({
          start_date: dateRange.start,
          end_date: dateRange.end,
          tag,
          granularity: 'day',
        });

        setTimeseriesData(response.timeseries);
        setTotalCount(response.summary.total);

        // Calculate trend (compare first half vs second half)
        const mid = Math.floor(response.timeseries.length / 2);
        const firstHalf = response.timeseries.slice(0, mid);
        const secondHalf = response.timeseries.slice(mid);

        const firstAvg = firstHalf.reduce((sum, d) => sum + d.count, 0) / firstHalf.length || 0;
        const secondAvg = secondHalf.reduce((sum, d) => sum + d.count, 0) / secondHalf.length || 0;

        if (secondAvg > firstAvg * 1.1) setTrend('up');
        else if (secondAvg < firstAvg * 0.9) setTrend('down');
        else setTrend('stable');
      } catch (error) {
        console.error(`Failed to fetch data for ${tag}:`, error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [tag, dateRange]);

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
      className={`${getTileSize()} bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-all cursor-pointer`}
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
