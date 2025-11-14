import { format, parseISO } from 'date-fns';

export const formatDate = (dateString: string | null, formatStr: string = 'MMM dd, yyyy'): string => {
  if (!dateString) return 'N/A';
  try {
    return format(parseISO(dateString), formatStr);
  } catch {
    return 'Invalid Date';
  }
};

export const formatDateTime = (dateString: string | null): string => {
  return formatDate(dateString, 'MMM dd, yyyy HH:mm');
};

export const getRelativeTimeString = (dateString: string): string => {
  const date = parseISO(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return formatDate(dateString, 'MMM dd');
};
