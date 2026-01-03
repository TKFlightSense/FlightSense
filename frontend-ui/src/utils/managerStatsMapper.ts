import type { ManagerStatisticsData, Period, SentimentCounts, SentimentPercentages, PriorityCounts, PriorityPercentages } from "../services/api";
import {DEPARTMENT_CODE_TO_LABEL, type DepartmentCode } from "../departmentConfig";

export type ManagerTrendPoint = {
  time_label: string;
  sentimentCounts: SentimentCounts
};

export type ManagerDepartmentUi = {
  id: string;
  name: string;
  totalReviews: number;
  sentimentCounts: SentimentCounts;
  sentimentPercentages: SentimentPercentages;
};

export type ManagerStatsUi = {
  periodLabel: string;
  totalReviews: number;
  uniqueReviews: number;
  processedSegments: number;
  sentimentCounts: SentimentCounts;
  sentimentPercentages: SentimentPercentages;
  priorityCounts: PriorityCounts;
  priorityPercentages: PriorityPercentages;
  departments: ManagerDepartmentUi[];
  historicalData: ManagerTrendPoint[];
};

function mapHistoricalDataToTrend(
  historical_data: ManagerStatisticsData["historical_data"],
  period: Period
): ManagerTrendPoint[] {
  const parseBucketIndex = (bucket: string): number => {
    const parts = bucket.split("_");
    const maybeIndex = Number(parts[1]);
    return Number.isFinite(maybeIndex) ? maybeIndex : Number.POSITIVE_INFINITY;
  };

  const getMonthLabel = (monthIndex1Based: number): string => {
    // Buckets are built as rolling month windows ending at "now".
    // Label each bucket by the *end* month so the most recent bucket shows the current month.
    const now = new Date();
    const monthsBack = 12 - monthIndex1Based;
    const d = new Date(now);
    d.setMonth(now.getMonth() - monthsBack);
    return d.toLocaleString("en-US", { month: "short" });
  };

  return Object.entries(historical_data)
    .sort(([a], [b]) => parseBucketIndex(a) - parseBucketIndex(b))
    .map(([bucket, value]) => {
    let shortLabel = bucket;

    if (period === "weekly" && bucket.startsWith("day_")) {
      shortLabel = "d" + bucket.split("_")[1];
    } else if (period === "monthly" && bucket.startsWith("week_")) {
      shortLabel = "w" + bucket.split("_")[1];
    } else if (period === "yearly" && bucket.startsWith("month_")) {
      shortLabel = getMonthLabel(parseBucketIndex(bucket));
    }

    return {
      time_label: shortLabel,
      sentimentCounts: {
        positive: value.positive?? 0,
        negative: value.negative ?? 0,
        neutral: value.neutral ?? 0,
      },
    };
  });
}

export function mapManagerStatsApiToUi(apiData: ManagerStatisticsData, period: Period): ManagerStatsUi {
  const totalReviews = apiData.total;
  const uniqueReviews = apiData.unique_reviews ?? 0;
  const processedSegments = apiData.processed_segments ?? 0;
  const periodLabel = apiData.period_label;


  const sentimentCounts: SentimentCounts = {
    positive: apiData.sentiment_counts?.positive ?? 0,
    negative: apiData.sentiment_counts?.negative ?? 0,
    neutral: apiData.sentiment_counts?.neutral ?? 0,
  };

  const sentimentPercentages: SentimentPercentages = {
    positive: apiData.sentiment_percentages?.positive ?? 0,
    negative: apiData.sentiment_percentages?.negative ?? 0,
    neutral: apiData.sentiment_percentages?.neutral ?? 0,
  };

  const priorityCounts: PriorityCounts = {
    high: apiData.priority_counts?.high ?? 0,
    medium: apiData.priority_counts?.medium ?? 0,
    low: apiData.priority_counts?.low ?? 0,
  };

  const priorityPercentages: PriorityPercentages = {
    high: apiData.priority_percentages?.high ?? 0,
    medium: apiData.priority_percentages?.medium ?? 0,
    low: apiData.priority_percentages?.low ?? 0,
  };

  const departments: ManagerDepartmentUi[] = Object.entries(
    apiData.department_distribution
  ).map(([backendName, total]) => {
    const sentimentEntry = apiData.department_sentiment_distribution[backendName]?.sentiment;

    const counts: SentimentCounts = {
      positive: sentimentEntry?.counts.positive ?? 0,
      negative: sentimentEntry?.counts.negative ?? 0,
      neutral: sentimentEntry?.counts.neutral ?? 0,
    };

    const percentages: SentimentPercentages = {
      positive: sentimentEntry?.percentage.positive ?? 0,
      negative: sentimentEntry?.percentage.negative ?? 0,
      neutral: sentimentEntry?.percentage.neutral ?? 0,
    };

    const departmentName= DEPARTMENT_CODE_TO_LABEL[backendName as DepartmentCode] ?? backendName;

    return {
      id: backendName,
      name: departmentName,
      totalReviews: total,
      sentimentCounts: counts,
      sentimentPercentages: percentages,
    };
  }) ?? [];

  const historicalData = mapHistoricalDataToTrend(apiData.historical_data, period) ?? [];

  return {
    periodLabel,
    totalReviews,
    uniqueReviews,
    processedSegments,
    sentimentCounts,
    sentimentPercentages,
    priorityCounts,
    priorityPercentages,
    departments,
    historicalData,
  };
}
