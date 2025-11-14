import React, { useEffect, useState } from 'react';
import { eventsApi } from '../api/events';
import { useAppStore } from '../stores/appStore';
import CategoryTile from '../components/CategoryTile';
import { Tag } from '../types';

const Dashboard: React.FC = () => {
  const { tags, setTags } = useAppStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTags = async () => {
      try {
        const response = await eventsApi.getTags();
        setTags(response.tags);
      } catch (error) {
        console.error('Failed to fetch tags:', error);
      } finally {
        setLoading(false);
      }
    };

    if (tags.length === 0) {
      fetchTags();
    } else {
      setLoading(false);
    }
  }, [tags.length, setTags]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-2xl text-gray-500">Loading dashboard...</div>
      </div>
    );
  }

  // Group tags by category for better organization
  const enabledTags = tags.filter(t => t.enabled);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">
          News Dashboard
        </h2>
        <p className="text-gray-400">
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
          />
        ))}
      </div>

      {enabledTags.length === 0 && (
        <div className="text-center py-16">
          <p className="text-gray-500 text-lg">No tags configured</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
