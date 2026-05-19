import { useQuery } from '@tanstack/react-query';
import { getExecutiveSummary } from '@/services/analytics.service';

export function useExecutiveAnalytics() {
  return useQuery({
    queryKey: ['executive-summary'],
    queryFn: getExecutiveSummary,
  });
}