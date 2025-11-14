import { create } from 'zustand';
import type { EventDetail, Tag } from '../types';

interface AppState {
  // Date range filter (global)
  dateRange: {
    start: string;
    end: string;
  };
  setDateRange: (start: string, end: string) => void;

  // Selected filters
  selectedTags: string[];
  selectedState: string | null;
  selectedSeverity: string | null;
  setSelectedTags: (tags: string[]) => void;
  setSelectedState: (state: string | null) => void;
  setSelectedSeverity: (severity: string | null) => void;
  clearFilters: () => void;

  // Sidebar state
  sidebarOpen: boolean;
  sidebarEvent: EventDetail | null;
  openSidebar: (event: EventDetail) => void;
  closeSidebar: () => void;

  // Tags configuration
  tags: Tag[];
  setTags: (tags: Tag[]) => void;
}

const getDefaultDateRange = () => {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 30); // Last 30 days by default

  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0],
  };
};

export const useAppStore = create<AppState>((set) => ({
  // Date range
  dateRange: getDefaultDateRange(),
  setDateRange: (start, end) => set({ dateRange: { start, end } }),

  // Filters
  selectedTags: [],
  selectedState: null,
  selectedSeverity: null,
  setSelectedTags: (tags) => set({ selectedTags: tags }),
  setSelectedState: (state) => set({ selectedState: state }),
  setSelectedSeverity: (severity) => set({ selectedSeverity: severity }),
  clearFilters: () => set({ selectedTags: [], selectedState: null, selectedSeverity: null }),

  // Sidebar
  sidebarOpen: false,
  sidebarEvent: null,
  openSidebar: (event) => set({ sidebarOpen: true, sidebarEvent: event }),
  closeSidebar: () => set({ sidebarOpen: false, sidebarEvent: null }),

  // Tags
  tags: [],
  setTags: (tags) => set({ tags }),
}));
