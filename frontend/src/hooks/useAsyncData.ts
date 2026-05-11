import { useCallback, useEffect, useState, type DependencyList } from "react";
import { translate } from "@/i18n";

export interface AsyncState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  reload: () => Promise<void>;
}

export function useAsyncData<T>(
  loader: () => Promise<T>,
  dependencies: DependencyList = [],
): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await loader();
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : translate("errors.unexpected"));
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    reload();
  }, [reload]);

  return { data, error, loading, reload };
}
