import type { DepartmentStatisticsData, Period, SentimentCounts, SentimentPercentages, PriorityCounts, PriorityPercentages } from "../services/api";
import {LABEL_KEY_TO_NAME, JIRA_KEY_TO_DEPARTMENT_LABEL, type DepartmentCode} from "../departmentConfig"

export type DepartmentHighPrioritySamplesUi = {
  labelKey: string;
  labelDisplay: string;
  samples: string[];
};

export type DeptTrendPointUi = {
  time_label: string;
  sentimentCounts: SentimentCounts
};

export type DepartmentLabelUi = {
  key: string;
  name: string;
  totalReviews: number;
  sentimentCounts: SentimentCounts;
  sentimentPercentages: SentimentPercentages;
};

export type DepartmentStatsUi = {
  departmentName: string;
  periodLabel: string;
  totalReviews: number;
  sentimentCounts: SentimentCounts;
  sentimentPercentages: SentimentPercentages;
  priorityCounts: PriorityCounts;
  priorityPercentages: PriorityPercentages;
  labelDistribution: DepartmentLabelUi[];
  highPrioritySamples: DepartmentHighPrioritySamplesUi[];
  historicalData: DeptTrendPointUi[];
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
      time_label: shortLabel,
      sentimentCounts: {
        positive: value.positive?? 0,
        negative: value.negative ?? 0,
        neutral: value.neutral ?? 0,
      },
    };
  });
}

export function mapDepartmentStatsApiToUi(apiData: DepartmentStatisticsData, period: Period): DepartmentStatsUi {
  const departmentName = JIRA_KEY_TO_DEPARTMENT_LABEL[apiData.department_name as DepartmentCode] ?? apiData.department_name;
  const totalReviews = apiData.total ?? 0;
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

  const labelDistribution: DepartmentLabelUi[] = Object.entries(
    apiData.label_distribution
  ).map(([labelKey, dist]) => {

    const counts: SentimentCounts = {
      positive: dist?.counts.positive ?? 0,
      negative: dist?.counts.negative ?? 0,
      neutral: dist?.counts.neutral ?? 0,
    };

    const percentages: SentimentPercentages = {
      positive: dist?.percentage.positive ?? 0,
      negative: dist?.percentage.negative ?? 0,
      neutral: dist?.percentage.neutral ?? 0,
    };

    const labelDisplay= LABEL_KEY_TO_NAME[labelKey] ?? labelKey;

    const total = counts.positive + counts.negative + counts.neutral;

    return {
      key: labelKey,
      name: labelDisplay,
      totalReviews: total,
      sentimentCounts: counts,
      sentimentPercentages: percentages,
    };
  }) ?? [];

  const highPrioritySamples: DepartmentHighPrioritySamplesUi[] = Object
    .entries(apiData.high_priority_samples ?? {} )
    .map(([labelKey, reviews]) => {
      const labelDisplay = LABEL_KEY_TO_NAME[labelKey] ?? labelKey;
      return {
        labelKey,
        labelDisplay ,
        samples: reviews,
    };
  }) ?? [];

  const historicalData = mapHistoricalDataToTrend(apiData.historical_data, period) ?? [];

  return {
    departmentName,
    periodLabel,
    totalReviews,
    sentimentCounts,
    sentimentPercentages,
    priorityCounts,
    priorityPercentages,
    labelDistribution,
    highPrioritySamples,
    historicalData,
  };
}
