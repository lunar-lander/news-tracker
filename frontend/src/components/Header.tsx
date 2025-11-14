import React, { useState } from 'react';
import { useAppStore } from '../stores/appStore';
import { useNavigate } from 'react-router-dom';

const Header: React.FC = () => {
  const { dateRange, setDateRange } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleDateChange = (type: 'start' | 'end', value: string) => {
    if (type === 'start') {
      setDateRange(value, dateRange.end);
    } else {
      setDateRange(dateRange.start, value);
    }
  };

  const handleQuickRange = (days: number) => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - days);

    setDateRange(
      start.toISOString().split('T')[0],
      end.toISOString().split('T')[0]
    );
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          {/* Logo and Title */}
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-white cursor-pointer" onClick={() => navigate('/')}>
              <span className="text-primary">India</span> News Tracker
            </h1>
          </div>

          {/* Date Range Selector */}
          <div className="flex items-center gap-2 flex-wrap">
            {/* Quick ranges */}
            <div className="flex gap-1">
              {[7, 30, 90].map((days) => (
                <button
                  key={days}
                  onClick={() => handleQuickRange(days)}
                  className="px-3 py-1 text-sm bg-gray-800 hover:bg-gray-700 text-white rounded transition-colors"
                >
                  {days}d
                </button>
              ))}
            </div>

            {/* Custom date range */}
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => handleDateChange('start', e.target.value)}
              className="px-3 py-1 text-sm bg-gray-800 text-white border border-gray-700 rounded focus:outline-none focus:border-primary"
            />
            <span className="text-gray-500">to</span>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => handleDateChange('end', e.target.value)}
              className="px-3 py-1 text-sm bg-gray-800 text-white border border-gray-700 rounded focus:outline-none focus:border-primary"
            />
          </div>

          {/* Search */}
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search headlines..."
              className="px-4 py-2 bg-gray-800 text-white border border-gray-700 rounded focus:outline-none focus:border-primary w-64"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-primary hover:bg-red-600 text-white rounded transition-colors"
            >
              Search
            </button>
          </form>
        </div>
      </div>
    </header>
  );
};

export default Header;
