// src/services/api.ts
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export type Period = "weekly" | "monthly" | "yearly";

// ---- Request tipleri ----
export interface ManagerStatisticsRequest {
  period: Period;
  date_from?: string | null; // ISO format, örn: "2025-12-01T00:00:00Z"
  date_to?: string | null;
}

export interface DepartmentStatisticsRequest {
  department_name: string; // "KHB", "IUIUB" vs.
  period: Period;
  date_from?: string | null;
  date_to?: string | null;
}

// ---- Response tipleri (kabaca) ----
export interface ManagerStatisticsResponse {
  success: boolean;
  data: {
    total: number;
    department_distribution: Record<string, number>;
    sentiment_counts: Record<string, number>;
    sentiment_percentages: Record<string, number>;
    priority_counts: Record<string, number>;
    priority_percentages: Record<string, number>;
    department_sentiment_distribution: any;
    period_label: string;
    historical_data: any;
  };
}

export interface DepartmentStatisticsResponse {
  success: boolean;
  data: {
    department_name: string;
    total: number;
    sentiment_distribution: any;
    priority_distribution: any;
    label_distribution: any;
    label_sentiment_distribution: any;
    period_label: string;
    historical_data: any;
  };
}

// ---- Helper: header üret ----
function getAuthHeaders(token: string) {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

// ---- Manager stats çağrısı ----
export async function fetchManagerStatistics(
  token: string,
  { period, date_from = null, date_to = null }: ManagerStatisticsRequest
): Promise<ManagerStatisticsResponse> {
  const res = await fetch(`${API_BASE_URL}/api/statistics/manager`, {
    method: "POST",
    headers: getAuthHeaders(token),
    body: JSON.stringify({ period, date_from, date_to }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch manager statistics");
  }

  return res.json();
}

// ---- Department stats çağrısı ----
export async function fetchDepartmentStatistics(
  token: string,
  {
    department_name,
    period,
    date_from = null,
    date_to = null,
  }: DepartmentStatisticsRequest
): Promise<DepartmentStatisticsResponse> {
  const res = await fetch(`${API_BASE_URL}/api/statistics/department`, {
    method: "POST",
    headers: getAuthHeaders(token),
    body: JSON.stringify({ department_name, period, date_from, date_to }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch department statistics");
  }

  return res.json();
}
