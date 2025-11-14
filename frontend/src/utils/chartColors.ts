// Vibrant colors for pure black background
export const CHART_COLORS = [
  '#FF6B6B', // Red
  '#4ECDC4', // Teal
  '#FFD93D', // Yellow
  '#95E1D3', // Mint
  '#F38181', // Light Red
  '#A8E6CF', // Light Green
  '#FF8B94', // Pink
  '#C7CEEA', // Light Purple
  '#FECA57', // Orange-Yellow
  '#48DBFB', // Light Blue
  '#FF9FF3', // Light Pink
  '#54A0FF', // Blue
];

export const getChartColor = (index: number): string => {
  return CHART_COLORS[index % CHART_COLORS.length];
};

export const TAG_COLORS: Record<string, string> = {
  murder: '#FF6B6B',
  rape: '#F38181',
  corruption: '#FFD93D',
  discrimination: '#FF8B94',
  accidents: '#4ECDC4',
  'political_corruption': '#FFA502',
  'hate_crime': '#FF6348',
  'communal_violence': '#FF4757',
  'traffic_accident': '#48DBFB',
  'building_collapse': '#0ABDE3',
  // Add more tag-specific colors as needed
};

export const getTagColor = (tag: string): string => {
  return TAG_COLORS[tag] || CHART_COLORS[0];
};

export const SEVERITY_COLORS: Record<string, string> = {
  low: '#95E1D3',
  medium: '#FFD93D',
  high: '#FF8B94',
  critical: '#FF6B6B',
};

export const getSeverityColor = (severity: string | null): string => {
  return severity ? SEVERITY_COLORS[severity] || '#888' : '#888';
};
