export interface NewsEvent {
  id: number;
  headline: string;
  summary: string | null;
  source_name: string | null;
  source_url: string | null;
  published_at: string;
  incident_date: string | null;
  primary_tag: string | null;
  all_tags: string[];
  severity: string | null;
  state: string | null;
  city: string | null;
  region: string | null;
}

export interface EventDetail extends NewsEvent {
  full_text: string | null;
  entities: {
    persons: string[];
    organizations: string[];
  } | null;
  classification_confidence: number | null;
  llm_model: string | null;
}

export interface TimeseriesDataPoint {
  timestamp: string;
  count: number;
  breakdown?: Record<string, number>;
}

export interface TimeseriesResponse {
  timeseries: TimeseriesDataPoint[];
  summary: {
    total: number;
    average: number;
    peak: {
      count: number;
      date: string;
    } | null;
  };
}

export interface BatchTimeseriesItem {
  tag: string;
  timeseries: TimeseriesDataPoint[];
  total: number;
}

export interface BatchTimeseriesResponse {
  items: BatchTimeseriesItem[];
}

export interface GeographicDataPoint {
  state: string;
  count: number;
  breakdown?: Record<string, number>;
}

export interface TrendingItem {
  tag: string;
  current_count: number;
  previous_count: number;
  percentage_change: number;
  trend: 'up' | 'down' | 'stable';
}

export interface Tag {
  id: string;
  label: string;
  category: string;
  color: string;
  enabled: boolean;
}

export interface RSSSource {
  id: number;
  name: string;
  category: string | null;
  language: string | null;
  enabled: boolean;
  lastFetched: string | null;
  health: 'healthy' | 'unhealthy' | 'disabled' | 'unknown';
}

export interface PaginationInfo {
  total: number;
  limit: number;
  offset: number;
  hasMore: boolean;
}

export interface EventsListResponse {
  data: NewsEvent[];
  pagination: PaginationInfo;
}

export interface SearchResponse {
  results: NewsEvent[];
  total: number;
}
