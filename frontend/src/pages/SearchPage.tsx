import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { eventsApi } from '../api/events';
import type { NewsEvent } from '../types';
import { formatDate } from '../utils/dateFormat';
import { getTagColor } from '../utils/chartColors';

const SearchPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  const [results, setResults] = useState<NewsEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const search = async () => {
      if (!query) return;

      try {
        setLoading(true);
        const response = await eventsApi.search({ q: query, limit: 100 });
        setResults(response.results);
        setTotal(response.total);
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setLoading(false);
      }
    };

    search();
  }, [query]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">
          Search Results
        </h2>
        <p className="text-gray-400">
          {loading ? 'Searching...' : `Found ${total} results for "${query}"`}
        </p>
      </div>

      {/* Results List */}
      <div className="space-y-4">
        {results.map((event) => (
          <div
            key={event.id}
            className="bg-gray-900 border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-all cursor-pointer"
          >
            {/* Headline */}
            <h3 className="text-xl font-semibold text-white mb-2">
              {event.headline}
            </h3>

            {/* Summary */}
            {event.summary && (
              <p className="text-gray-400 mb-4 line-clamp-2">
                {event.summary}
              </p>
            )}

            {/* Metadata */}
            <div className="flex items-center gap-4 flex-wrap text-sm">
              {/* Date */}
              <span className="text-gray-500">
                {formatDate(event.published_at)}
              </span>

              {/* Source */}
              {event.source_name && (
                <span className="text-gray-500">
                  {event.source_name}
                </span>
              )}

              {/* Location */}
              {event.state && (
                <span className="text-gray-500">
                  📍 {event.city ? `${event.city}, ` : ''}{event.state}
                </span>
              )}

              {/* Tags */}
              <div className="flex gap-2">
                {event.all_tags.slice(0, 3).map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 rounded text-xs font-medium"
                    style={{
                      backgroundColor: `${getTagColor(tag)}33`,
                      color: getTagColor(tag),
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>

              {/* Link */}
              {event.source_url && (
                <a
                  href={event.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:text-red-600 transition-colors ml-auto"
                  onClick={(e) => e.stopPropagation()}
                >
                  Read More →
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* No results */}
      {!loading && results.length === 0 && query && (
        <div className="text-center py-16">
          <p className="text-gray-500 text-lg">No results found</p>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
