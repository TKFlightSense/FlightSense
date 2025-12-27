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

export type ManagerHighPrioritySamplesUi = {
  department_id: string;
  department_name: string;
  samples: string[];
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
  highPrioritySamples: ManagerHighPrioritySamplesUi[];
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

  const highPrioritySamples: ManagerHighPrioritySamplesUi[] = Object.entries(
    apiData.high_priority_samples ?? {})
    .map(([department_id, samples]) => {
      const department_name = DEPARTMENT_CODE_TO_LABEL[department_id as DepartmentCode] ?? department_id;
      return {
        department_id,
        department_name,
        samples,
      };
    }) ?? [];
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
    highPrioritySamples,
  };
}
