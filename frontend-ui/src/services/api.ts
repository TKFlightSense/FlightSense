export type Period = "weekly" | "monthly" | "yearly";

export interface SentimentCounts {positive: number; negative: number; neutral: number}

export interface SentimentPercentages {positive: number; negative: number; neutral: number}

export interface PriorityCounts {high: number; medium: number; low: number}

export interface PriorityPercentages {high: number; medium: number; low: number}

export interface HistoricalBucket {positive: number; negative: number; neutral: number}

export type HistoricalData = Record<string, HistoricalBucket>;

/* ---------- MANAGER TYPES ---------- */

export interface ManagerStatisticsData {
  total: number;
  unique_reviews: number;
  processed_segments: number;
  department_distribution: Record<string, number>;
  sentiment_counts: SentimentCounts;
  sentiment_percentages: SentimentPercentages;
  priority_counts: PriorityCounts;
  priority_percentages: PriorityPercentages;
  department_sentiment_distribution: {
    [deptLabel: string]: {
      sentiment: {
        counts: SentimentCounts
        percentage: SentimentPercentages
      };
    };
  };
  period_label: string;
  historical_data: HistoricalData;
}

export interface ManagerStatisticsResult {
  success: boolean;
  data: ManagerStatisticsData;
}

export interface ManagerStatisticsHttpResponse {
  success: boolean;
  result: ManagerStatisticsResult;
}

/* ---------- DEPARTMENT TYPES ---------- */

export interface DepartmentStatisticsData {
  department_name: string;
  total: number;

  sentiment_counts: SentimentCounts;
  sentiment_percentages: SentimentPercentages;
  priority_counts: PriorityCounts;
  priority_percentages: PriorityPercentages;

  

  label_distribution: {
    [labelKey: string]: {
      counts: SentimentCounts
      percentage: SentimentPercentages
    };
  };

  period_label: string;

  historical_data: HistoricalData;
}

export interface DepartmentStatisticsResult {
  success: boolean;
  data: DepartmentStatisticsData;
}

export interface DepartmentStatisticsHttpResponse {
  success: boolean;
  result: DepartmentStatisticsResult;
}

/* ---------- HIGH PRIORITY TYPES ---------- */

export interface HighPriorityReviewItem {
  label: string;
  review: string;
  highlightIndex?: string;
  date: string;
  flightNumber?: string;
  route?: string;
}

export interface DepartmentHighPriorityResponse {
  department: string;
  items: HighPriorityReviewItem[];
}

export interface ManagerHighPriorityResponse {
  departments: Record<string, HighPriorityReviewItem[]>;
}


/* ---------- COMMON HTTP ---------- */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function getAuthHeaders(token: string) {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

/* ---------- MANAGER FETCH ---------- */

export async function fetchManagerStatistics(
  token: string,
  period: Period
): Promise<ManagerStatisticsResult> {
  const res = await fetch(`${API_BASE_URL}/api/statistics/manager`, {
    method: "POST",
    headers: getAuthHeaders(token),
    body: JSON.stringify({
      period,
      date_from: null,
      date_to: null,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch manager statistics");
  }

  const json: ManagerStatisticsHttpResponse = await res.json();
  return json.result; // { success, data }
}

/* ---------- DEPARTMENT FETCH ---------- */

export async function fetchDepartmentStatistics(
  token: string,
  params: {
    department_name: string; // backend code: "TGS", "KHB", "IUIUB", "BMCOGM", ...
    period: Period;
    date_from?: string | null;
    date_to?: string | null;
  }
): Promise<DepartmentStatisticsResult> {
  const res = await fetch(`${API_BASE_URL}/api/statistics/department`, {
    method: "POST",
    headers: getAuthHeaders(token),
    body: JSON.stringify({
      department_name: params.department_name,
      period: params.period,
      date_from: params.date_from ?? null,
      date_to: params.date_to ?? null,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch department statistics");
  }

  const json: DepartmentStatisticsHttpResponse = await res.json();
  return json.result; // { success, data }
}

/* ---------- HIGH PRIORITY FETCH ---------- */

export async function fetchDepartmentHighPriority(
  department: string,
  limit = 5
): Promise<DepartmentHighPriorityResponse> {
  const res = await fetch(
    `${API_BASE_URL}/api/high-priority/department?department=${department}&limit=${limit}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("flightsense_token")}`,
      },
    }
  );

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch department high priority");
  }
  return res.json();
}

export async function fetchManagerHighPriority(
  limitPerDepartment = 3
): Promise<ManagerHighPriorityResponse> {
  const res = await fetch(
    `${API_BASE_URL}/api/high-priority/manager?limit_per_department=${limitPerDepartment}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("flightsense_token")}`,
      },
    }
  );

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch manager high priority");
  }

  return res.json();
}
