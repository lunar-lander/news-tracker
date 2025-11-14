import apiClient from './client';
import type { EventsListResponse, EventDetail, TimeseriesResponse, GeographicDataPoint, TrendingItem, Tag, RSSSource, SearchResponse } from '../types';

export interface EventsQuery {
  start_date?: string;
  end_date?: string;
  tags?: string;
  state?: string;
  city?: string;
  severity?: string;
  limit?: number;
  offset?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface TimeseriesQuery {
  start_date: string;
  end_date: string;
  granularity?: 'day' | 'week' | 'month';
  tag?: string;
  tags?: string;
  state?: string;
  group_by?: 'tag' | 'state' | 'severity';
}

export interface GeographicQuery {
  start_date: string;
  end_date: string;
  tag?: string;
  granularity?: 'state' | 'city';
}

export interface SearchQuery {
  q: string;
  start_date?: string;
  end_date?: string;
  tags?: string;
  state?: string;
  limit?: number;
  offset?: number;
}

export const eventsApi = {
  // List events with filters
  async listEvents(query: EventsQuery = {}): Promise<EventsListResponse> {
    const response = await apiClient.get('/api/v1/events', { params: query });
    return response.data;
  },

  // Get event detail
  async getEvent(id: number): Promise<EventDetail> {
    const response = await apiClient.get(`/api/v1/events/${id}`);
    return response.data;
  },

  // Get timeseries data
  async getTimeseries(query: TimeseriesQuery): Promise<TimeseriesResponse> {
    const response = await apiClient.get('/api/v1/analytics/timeseries', { params: query });
    return response.data;
  },

  // Get geographic distribution
  async getGeographic(query: GeographicQuery): Promise<{ geographic: GeographicDataPoint[] }> {
    const response = await apiClient.get('/api/v1/analytics/geographic', { params: query });
    return response.data;
  },

  // Get trending tags
  async getTrending(timeframe: '24h' | '7d' | '30d' = '24h', limit: number = 10): Promise<{ trending: TrendingItem[] }> {
    const response = await apiClient.get('/api/v1/analytics/trending', { params: { timeframe, limit } });
    return response.data;
  },

  // Search events
  async search(query: SearchQuery): Promise<SearchResponse> {
    const response = await apiClient.get('/api/v1/search', { params: query });
    return response.data;
  },

  // Get tags configuration
  async getTags(): Promise<{ tags: Tag[] }> {
    const response = await apiClient.get('/api/v1/config/tags');
    return response.data;
  },

  // Get RSS sources
  async getSources(): Promise<{ sources: RSSSource[] }> {
    const response = await apiClient.get('/api/v1/config/sources');
    return response.data;
  },
};
