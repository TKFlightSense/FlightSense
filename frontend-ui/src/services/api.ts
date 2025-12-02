export type Period = "weekly" | "monthly" | "yearly";

/* ---------- MANAGER TYPES ---------- */

export interface ManagerStatisticsData {
  total: number;
  department_distribution: Record<string, number>;
  sentiment_counts: {
    positive: number;
    negative: number;
    neutral: number;
  };
  sentiment_percentages: Record<string, number>;
  priority_counts: {
    high: number;
    medium: number;
    low: number;
  };
  priority_percentages: Record<string, number>;
  department_sentiment_distribution: {
    [deptLabel: string]: {
      sentiment: {
        counts: {
          positive: number;
          negative: number;
          neutral: number;
        };
        percentage: Record<string, number>;
      };
    };
  };
  period_label: string;
  historical_data: {
    [bucket: string]: {
      positive: number;
      negative: number;
    };
  };
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

  sentiment_distribution: {
    counts: {
      positive: number;
      negative: number;
      neutral: number;
    };
    percentage: {
      positive: number;
      negative: number;
      neutral: number;
    };
  };

  priority_distribution: {
    counts: {
      high: number;
      medium: number;
      low: number;
    };
    percentage: {
      high: number;
      medium: number;
      low: number;
    };
  };

  label_distribution: {
    [labelKey: string]: {
      counts: {
        positive: number;
        negative: number;
        neutral: number;
      };
      percentage: {
        positive: number;
        negative: number;
        neutral: number;
      };
    };
  };

  label_sentiment_distribution: {
    [labelKey: string]: {
      counts: {
        positive: number;
        negative: number;
        neutral: number;
      };
      percentage: {
        positive: number;
        negative: number;
        neutral: number;
      };
    };
  };

  period_label: string;

  historical_data: {
    [bucket: string]: {
      positive: number;
      negative: number;
    };
  };
}

export interface DepartmentStatisticsResult {
  success: boolean;
  data: DepartmentStatisticsData;
}

export interface DepartmentStatisticsHttpResponse {
  success: boolean;
  result: DepartmentStatisticsResult;
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
    department_name: string; // backend code: "TGS", "KABIN", "IUIUB", "BMCOGM", ...
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
