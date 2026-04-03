import React from 'react';
import { useAppStore } from '../stores/appStore';

const Header: React.FC = () => {
    const { dateRange, setDateRange } = useAppStore();

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

    const handleYTD = () => {
        const end = new Date();
        const start = new Date(end.getFullYear(), 0, 1); // Jan 1 of current year
        setDateRange(
            start.toISOString().split('T')[0],
            end.toISOString().split('T')[0]
        );
    };

    return (
        <header className="bg-[#0a0a0a] border-b border-[#1a1a1a] sticky top-0 z-50">
            <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between flex-wrap gap-4">
                    {/* Logo and Title */}
                    <div className="flex items-center gap-4">
                        <h1 className="text-2xl font-bold text-white">
                            <span className="text-primary">India</span> News Tracker
                        </h1>
                    </div>

                    {/* Date Range Selector */}
                    <div className="flex items-center gap-2 flex-wrap">
                        {/* Quick ranges */}
                        <div className="flex gap-1">
                            {[7, 30, 90, 365].map((days) => (
                                <button
                                    key={days}
                                    onClick={() => handleQuickRange(days)}
                                    className="px-3 py-1 text-sm bg-[#141414] hover:bg-[#1a1a1a] text-white rounded transition-colors"
                                >
                                    {days === 365 ? '1Y' : `${days}d`}
                                </button>
                            ))}
                            <button
                                onClick={handleYTD}
                                className="px-3 py-1 text-sm bg-[#141414] hover:bg-[#1a1a1a] text-white rounded transition-colors"
                            >
                                YTD
                            </button>
                        </div>

                        {/* Custom date range */}
                        <input
                            type="date"
                            value={dateRange.start}
                            onChange={(e) => handleDateChange('start', e.target.value)}
                            className="px-3 py-1 text-sm bg-[#141414] text-white border border-[#222] rounded focus:outline-none focus:border-primary"
                        />
                        <span className="text-gray-500">to</span>
                        <input
                            type="date"
                            value={dateRange.end}
                            onChange={(e) => handleDateChange('end', e.target.value)}
                            className="px-3 py-1 text-sm bg-[#141414] text-white border border-[#222] rounded focus:outline-none focus:border-primary"
                        />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
