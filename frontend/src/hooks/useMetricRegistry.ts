import { useQuery } from '@tanstack/react-query';
import { listMetrics, getMetric } from '@/services/analytics.service';

export function useMetricRegistry() {
  return useQuery({
    queryKey: ['metrics'],
    queryFn: listMetrics,
  });
}

export function useGetMetric(code: string) {
  return useQuery({
    queryKey: ['metric', code],
    queryFn: () => getMetric(code),
    enabled: !!code,
  });
}