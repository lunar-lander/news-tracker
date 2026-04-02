import React, { useEffect, useState } from 'react';
import { eventsApi } from '../api/events';
import type { NewsEvent } from '../types';

interface ArticleListProps {
    tag: string;
    label: string;
    color: string;
    startDate: string;
    endDate: string;
    onClose: () => void;
}

const ArticleList: React.FC<ArticleListProps> = ({ tag, label, color, startDate, endDate, onClose }) => {
    const [articles, setArticles] = useState<NewsEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [total, setTotal] = useState(0);
    const [offset, setOffset] = useState(0);
    const limit = 50;

    useEffect(() => {
        const fetchArticles = async () => {
            try {
                setLoading(true);
                const response = await eventsApi.listEvents({
                    tags: tag,
                    start_date: startDate,
                    end_date: endDate,
                    limit,
                    offset,
                    sort: 'published_at',
                    order: 'desc',
                });
                setArticles(response.data);
                setTotal(response.pagination.total);
            } catch (error) {
                console.error('Failed to fetch articles:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchArticles();
    }, [tag, startDate, endDate, offset]);

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
        });
    };

    return (
        // Backdrop
        <div
            className="fixed inset-0 bg-black/70 z-50 flex items-start justify-center pt-16 px-4"
            onClick={onClose}
        >
            {/* Panel */}
            <div
                className="bg-gray-900 border border-gray-700 rounded-lg w-full max-w-3xl max-h-[80vh] flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-gray-800">
                    <div>
                        <h2 className="text-xl font-bold" style={{ color }}>
                            {label}
                        </h2>
                        <p className="text-sm text-gray-400">
                            {total} articles · {startDate} to {endDate}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white text-2xl leading-none px-2"
                    >
                        ×
                    </button>
                </div>

                {/* Article list */}
                <div className="overflow-y-auto flex-1 p-4">
                    {loading ? (
                        <div className="text-center py-8 text-gray-500">Loading articles...</div>
                    ) : articles.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">No articles found</div>
                    ) : (
                        <ul className="space-y-3">
                            {articles.map((article) => (
                                <li key={article.id} className="border-b border-gray-800 pb-3 last:border-0">
                                    <a
                                        href={article.source_url || '#'}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="group block"
                                    >
                                        <h3 className="text-white group-hover:text-blue-400 transition-colors text-sm font-medium leading-snug">
                                            {article.headline}
                                        </h3>
                                        <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                                            {article.source_name && <span>{article.source_name}</span>}
                                            <span>{formatDate(article.published_at)}</span>
                                            {article.state && <span>{article.state}</span>}
                                            {article.severity && (
                                                <span className="px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">
                                                    {article.severity}
                                                </span>
                                            )}
                                        </div>
                                        {article.summary && (
                                            <p className="text-gray-500 text-xs mt-1 line-clamp-2">
                                                {article.summary}
                                            </p>
                                        )}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                {/* Pagination */}
                {total > limit && (
                    <div className="flex items-center justify-between p-4 border-t border-gray-800">
                        <button
                            onClick={() => setOffset(Math.max(0, offset - limit))}
                            disabled={offset === 0}
                            className="px-3 py-1 text-sm bg-gray-800 hover:bg-gray-700 text-white rounded disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            ← Prev
                        </button>
                        <span className="text-sm text-gray-400">
                            {offset + 1}–{Math.min(offset + limit, total)} of {total}
                        </span>
                        <button
                            onClick={() => setOffset(offset + limit)}
                            disabled={offset + limit >= total}
                            className="px-3 py-1 text-sm bg-gray-800 hover:bg-gray-700 text-white rounded disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            Next →
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ArticleList;
