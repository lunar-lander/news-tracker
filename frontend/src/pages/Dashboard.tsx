import React, { useEffect, useState } from 'react';
import { eventsApi } from '../api/events';
import CategoryTile from '../components/CategoryTile';
import { useAppStore } from '../stores/appStore';
import type { BatchTimeseriesItem } from '../types';

const Dashboard: React.FC = () => {
    const { tags, setTags, dateRange } = useAppStore();
    const [loading, setLoading] = useState(true);
    const [tagData, setTagData] = useState<Map<string, BatchTimeseriesItem>>(new Map());

    // Fetch tags config
    useEffect(() => {
        const fetchTags = async () => {
            try {
                const response = await eventsApi.getTags();
                setTags(response.tags);
            } catch (error) {
                console.error('Failed to fetch tags:', error);
            }
        };

        if (tags.length === 0) {
            fetchTags();
        }
    }, [tags.length, setTags]);

    // Fetch batch timeseries for all enabled tags in one request
    const enabledTags = tags.filter(t => t.enabled);

    useEffect(() => {
        if (enabledTags.length === 0) {
            setLoading(false);
            return;
        }

        const fetchBatchData = async () => {
            try {
                setLoading(true);
                const response = await eventsApi.getTimeseriesBatch({
                    start_date: dateRange.start,
                    end_date: dateRange.end,
                    tags: enabledTags.map(t => t.id).join(','),
                    granularity: 'day',
                });

                const dataMap = new Map<string, BatchTimeseriesItem>();
                for (const item of response.items) {
                    dataMap.set(item.tag, item);
                }
                setTagData(dataMap);
            } catch (error) {
                console.error('Failed to fetch batch timeseries:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchBatchData();
    }, [enabledTags.length, dateRange.start, dateRange.end]);

    if (loading && tags.length === 0) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-2xl text-gray-500">Loading dashboard...</div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-white mb-2 text-center">
                </h2>
                <p className="text-gray-400 text-center">
                    Real-time tracking of incidents across India
                </p>
            </div>

            {/* Grid of Category Tiles */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 auto-rows-auto">
                {enabledTags.map((tag) => (
                    <CategoryTile
                        key={tag.id}
                        tag={tag.id}
                        label={tag.label}
                        color={tag.color}
                        data={tagData.get(tag.id)}
                        loading={loading}
                    />
                ))}
            </div>

            {enabledTags.length === 0 && !loading && (
                <div className="text-center py-16">
                    <p className="text-gray-500 text-lg">No tags configured</p>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
