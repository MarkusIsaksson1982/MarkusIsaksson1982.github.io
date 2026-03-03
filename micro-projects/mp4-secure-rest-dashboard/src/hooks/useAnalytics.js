import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "../contexts/AuthContext.jsx";

const CACHE_TTL_MS = 30_000;

export function useAnalytics(period = "30d") {
  const { apiFetch } = useAuth();
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState(null);
  const [heatmap, setHeatmap] = useState(null);
  const [productivity, setProductivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const cacheRef = useRef(new Map());

  const fetchWithCache = useCallback(
    async (key, url) => {
      const cached = cacheRef.current.get(key);
      const now = Date.now();
      if (cached && now - cached.timestamp < CACHE_TTL_MS) {
        return cached.value;
      }

      const response = await apiFetch(url);
      cacheRef.current.set(key, { timestamp: now, value: response?.data ?? null });
      return response?.data ?? null;
    },
    [apiFetch],
  );

  const loadAnalytics = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [summaryData, trendsData, heatmapData, productivityData] = await Promise.all([
        fetchWithCache("summary", "/api/analytics/summary"),
        fetchWithCache(`trends:${period}`, `/api/analytics/trends?period=${period}`),
        fetchWithCache(`heatmap:${period}`, `/api/analytics/heatmap?period=${period}`),
        fetchWithCache("productivity", "/api/analytics/productivity"),
      ]);

      setSummary(summaryData);
      setTrends(trendsData);
      setHeatmap(heatmapData);
      setProductivity(productivityData);
    } catch (requestError) {
      setError(requestError.message ?? "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  }, [fetchWithCache, period]);

  useEffect(() => {
    void loadAnalytics();
  }, [loadAnalytics]);

  return {
    summary,
    trends,
    heatmap,
    productivity,
    loading,
    error,
    refresh: loadAnalytics,
  };
}
