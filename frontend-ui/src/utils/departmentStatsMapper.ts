// src/utils/departmentStatsMapper.ts

import type { DepartmentStatisticsData, Period } from "../services/api";

export type DepartmentIssueUi = {
  labelKey: string;
  labelDisplay: string;
  count: number;
  trend: "up" | "down" | "flat";
  positive: number;
  negative: number;
};

export type DeptTrendPointUi = {
  label: string;
  positive: number;
  negative: number;
};

export type DepartmentStatsUi = {
  departmentName: string; // backend'in gönderdiği görünen label
  periodLabel: string;
  totalReviews: number;
  positive: number;
  negative: number;
  highPriority: number;
  mediumPriority: number;
  lowPriority: number;
  topIssues: DepartmentIssueUi[];
  trend: DeptTrendPointUi[];
};

function mapHistoricalDataToTrend(
  historical: DepartmentStatisticsData["historical_data"],
  period: Period
): DeptTrendPointUi[] {
  return Object.entries(historical).map(([bucket, value]) => {
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

export function mapDepartmentStatsApiToUi(
  apiData: DepartmentStatisticsData,
  // display için backend label'ı route paramdan alıyoruz
  departmentLabelFromRoute: string,
  period: Period
): DepartmentStatsUi {
  const totalReviews = apiData.total ?? 0;
  const periodLabel = apiData.period_label;

  const positive = apiData.sentiment_distribution.counts.positive ?? 0;
  const negative = apiData.sentiment_distribution.counts.negative ?? 0;

  const highPriority = apiData.priority_distribution.counts.high ?? 0;
  const mediumPriority = apiData.priority_distribution.counts.medium ?? 0;
  const lowPriority = apiData.priority_distribution.counts.low ?? 0;

  const topIssues: DepartmentIssueUi[] = Object.entries(
    apiData.label_distribution
  ).map(([labelKey, dist]) => {
    const pos = dist.counts.positive ?? 0;
    const neg = dist.counts.negative ?? 0;
    const neu = dist.counts.neutral ?? 0;
    const total = pos + neg + neu;

    // Şimdilik trend bilgisi backend'de yok, "flat" diyelim
    const trend: "up" | "down" | "flat" = "flat";

    return {
      labelKey,
      labelDisplay: labelKey, // istersen burada human-readable label mapping yapabilirsin
      count: total,
      trend,
      positive: pos,
      negative: neg,
    };
  });

  const trend = mapHistoricalDataToTrend(apiData.historical_data, period);

  return {
    departmentName: departmentLabelFromRoute,
    periodLabel,
    totalReviews,
    positive,
    negative,
    highPriority,
    mediumPriority,
    lowPriority,
    topIssues,
    trend,
  };
}
