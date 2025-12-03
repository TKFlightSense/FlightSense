// src/utils/managerStatsMapper.ts
import type { ManagerStatisticsData, Period } from "../services/api";

export type ManagerTrendPoint = {
  label: string;
  positive: number;
  negative: number;
};

export type ManagerDepartmentUi = {
  id: string;
  name: string;
  totalReviews: number;
  positive: number;
  negative: number;
};

export type ManagerTopIssue = {
  labelKey: string;
  labelDisplay: string;
  count: number;
  positive: number;
  negative: number;
  trend: "up" | "down" | "stable";
};

export type ManagerStatsUi = {
  periodLabel: string;
  totalReviews: number;
  uniqueReviews: number;
  processedSegments: number;
  positive: number;
  negative: number;
  highPriority: number;
  mediumPriority: number;
  lowPriority: number;
  departments: ManagerDepartmentUi[];
  trend: ManagerTrendPoint[];
  topIssues: ManagerTopIssue[];
};

function mapHistoricalDataToTrend(
  historical_data: ManagerStatisticsData["historical_data"],
  period: Period
): ManagerTrendPoint[] {
  return Object.entries(historical_data).map(([bucket, value]) => {
    let shortLabel = bucket;

    if (period === "weekly" && bucket.startsWith("day_")) {
      shortLabel = "D" + bucket.split("_")[1];
    } else if (period === "monthly" && bucket.startsWith("week_")) {
      shortLabel = "W" + bucket.split("_")[1];
    } else if (period === "yearly" && bucket.startsWith("month_")) {
      shortLabel = "M" + bucket.split("_")[1];
    }

    return {
      label: shortLabel,
      positive: value.positive ?? 0,
      negative: value.negative ?? 0,
    };
  });
}

export function mapManagerStatsApiToUi(
  apiData: ManagerStatisticsData,
  period: Period
): ManagerStatsUi {
  const totalReviews = apiData.total;
  const uniqueReviews = apiData.unique_reviews ?? 0;
  const processedSegments = apiData.processed_segments ?? 0;
  const periodLabel = apiData.period_label;

  const positive = apiData.sentiment_counts.positive ?? 0;
  const negative = apiData.sentiment_counts.negative ?? 0;

  const highPriority = apiData.priority_counts.high ?? 0;
  const mediumPriority = apiData.priority_counts.medium ?? 0;
  const lowPriority = apiData.priority_counts.low ?? 0;

  const departmentsUi: ManagerDepartmentUi[] = Object.entries(
    apiData.department_distribution
  ).map(([backendName, total]) => {
    const sentimentEntry =
      apiData.department_sentiment_distribution[backendName]?.sentiment;

    const depPositive = sentimentEntry?.counts.positive ?? 0;
    const depNegative = sentimentEntry?.counts.negative ?? 0;

    return {
      id: backendName,      // route param olarak da bunu kullanacağız
      name: backendName,    // UI'da görünen isim
      totalReviews: total,
      positive: depPositive,
      negative: depNegative,
    };
  });

  const trend = mapHistoricalDataToTrend(apiData.historical_data, period);

  const topIssues: ManagerTopIssue[] = []; // backend şu anda issue bazlı data göndermiyor

  return {
    periodLabel,
    totalReviews,
    uniqueReviews,
    processedSegments,
    positive,
    negative,
    highPriority,
    mediumPriority,
    lowPriority,
    departments: departmentsUi,
    trend,
    topIssues,
  };
}
