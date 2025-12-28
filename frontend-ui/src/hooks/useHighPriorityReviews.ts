import { useEffect, useState } from "react";
import {
  fetchDepartmentHighPriority,
  fetchManagerHighPriority,
} from "../services/api";
import type { HighPriorityReviewItem } from "../services/api";
import type { DepartmentId } from "../departmentConfig";

/* ---------- DEPARTMENT ---------- */

export function useDepartmentHighPriority(department: string, limit = 5) {
  const [items, setItems] = useState<HighPriorityReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetchDepartmentHighPriority(department, limit)
      .then((res) => setItems(res.items))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [department, limit]);
  return { items, loading, error };
}

/* ---------- MANAGER ---------- */

export function useManagerHighPriority(limitPerDepartment = 3) {
  const [data, setData] = useState<
  Partial<Record<DepartmentId, HighPriorityReviewItem[]>>
  >({});

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetchManagerHighPriority(limitPerDepartment)
      .then((res) => setData(res.departments))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [limitPerDepartment]);

  return { data, loading, error };
}
