import { useCallback, useEffect, useState } from "react";

import type { FacultyConfig } from "@/services/platformConfig.service";
import { getFacultyDisplayName } from "@/services/platformConfig.service";

export function useFacultyConfig(facultyId: number | null): {
  config: FacultyConfig | null;
  isLoading: boolean;
  error: Error | null;
  displayName: (lang?: "th" | "en") => string;
} {
  const [config, setConfig] = useState<FacultyConfig | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (facultyId === null) {
      setConfig(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    // Placeholder until /api/platform/faculty-configs/{id} endpoint is wired
    fetch(`/api/platform/faculty-configs/${facultyId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json() as Promise<FacultyConfig>;
      })
      .then((data) => {
        setConfig(data);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err : new Error(String(err)));
        setConfig(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [facultyId]);

  const displayName = useCallback(
    (lang: "th" | "en" = "th") => getFacultyDisplayName(config, lang),
    [config],
  );

  return { config, isLoading, error, displayName };
}
