export type DepartmentSummary = {
  id: string;
  name: string;
  totalReviews: number;
  highPriority: number;
  positive: number;
  negative: number;
};

export type TopIssue = {
  labelKey: string;
  labelDisplay: string;
  count: number;
  trend: "up" | "down" | "stable";
  positive: number;
  negative: number;
};

export type TrendPoint = {
  label: string; // e.g. "D1", "W1", "M1"
  positive: number;
  negative: number;
};

export type ManagerStats = {
  periodLabel: string;
  totalReviews: number;
  uniqueReviews: number;
  processedSegments: number;
  positive: number;
  negative: number;
  highPriority: number;
  mediumPriority: number;
  lowPriority: number;
  departments: DepartmentSummary[];
  topIssues: TopIssue[];
  trend: TrendPoint[];
};

export type TimeRangeKey = "weekly" | "monthly" | "yearly";

/**
 * MONTHLY BASELINE (same structure you had, just extended with pos/neg on issues)
 * Think "Last 30 days".
 */
export const MONTHLY_MANAGER_STATS: ManagerStats = {
  periodLabel: "Last 30 days",
  totalReviews: 1240,
  uniqueReviews: 480,
  processedSegments: 1240,
  positive: 830,
  negative: 410,
  highPriority: 180,
  mediumPriority: 520,
  lowPriority: 540,
  departments: [
    {
      id: "TGS",
      name: "TGS - Yer Hizmetleri",
      totalReviews: 420,
      highPriority: 75,
      positive: 280,
      negative: 140,
    },
    {
      id: "IUIUB",
      name: "İkram ve Uçak İçi Ürünler Bşk.",
      totalReviews: 310,
      highPriority: 50,
      positive: 230,
      negative: 80,
    },
    {
      id: "BMCOGM",
      name: "Yer İşletme Bşk - Bagaj",
      totalReviews: 280,
      highPriority: 40,
      positive: 150,
      negative: 130,
    },
    {
      id: "KHB",
      name: "Kabin Hizmetleri Bşk.",
      totalReviews: 230,
      highPriority: 15,
      positive: 170,
      negative: 60,
    },
  ],
  topIssues: [
    {
      labelKey: "baggage_lost",
      labelDisplay: "Baggage lost",
      count: 120,
      trend: "up",
      positive: 10,
      negative: 110,
    },
    {
      labelKey: "checkin_process",
      labelDisplay: "Check-in process",
      count: 95,
      trend: "stable",
      positive: 35,
      negative: 60,
    },
    {
      labelKey: "inflight_experience_food_beverage",
      labelDisplay: "Inflight food & beverage",
      count: 80,
      trend: "down",
      positive: 30,
      negative: 50,
    },
    {
      labelKey: "boarding_process",
      labelDisplay: "Boarding process",
      count: 72,
      trend: "up",
      positive: 25,
      negative: 47,
    },
  ],
  // 4 weekly points within the month
  trend: [
    { label: "W1", positive: 180, negative: 70 },
    { label: "W2", positive: 210, negative: 95 },
    { label: "W3", positive: 200, negative: 120 },
    { label: "W4", positive: 240, negative: 125 },
  ],
};

/**
 * MORE REALISTIC PER-RANGE MOCKS
 */
export const MOCK_MANAGER_STATS_BY_RANGE: Record<TimeRangeKey, ManagerStats> = {
  /**
   * WEEKLY – smaller volume, still ~67% positive
   */
  weekly: {
    periodLabel: "Last 7 days",
    totalReviews: 290,
    uniqueReviews: 112,
    processedSegments: 290,
    positive: 195,
    negative: 95,
    highPriority: 45,
    mediumPriority: 120,
    lowPriority: 125,
    departments: [
      {
        id: "TGS",
        name: "TGS - Yer Hizmetleri",
        totalReviews: 100,
        highPriority: 20,
        positive: 67,
        negative: 33,
      },
      {
        id: "IUIUB",
        name: "İkram ve Uçak İçi Ürünler Bşk.",
        totalReviews: 75,
        highPriority: 13,
        positive: 57,
        negative: 18,
      },
      {
        id: "BMCOGM",
        name: "Yer İşletme Bşk - Bagaj",
        totalReviews: 65,
        highPriority: 8,
        positive: 32,
        negative: 33, // slightly more negative for baggage
      },
      {
        id: "KHB",
        name: "Kabin Hizmetleri Bşk.",
        totalReviews: 50,
        highPriority: 4,
        positive: 39,
        negative: 11,
      },
    ],
    topIssues: [
      {
        labelKey: "baggage_lost",
        labelDisplay: "Baggage lost",
        count: 30,
        trend: "up",
        positive: 2,
        negative: 28,
      },
      {
        labelKey: "checkin_process",
        labelDisplay: "Check-in process",
        count: 24,
        trend: "stable",
        positive: 8,
        negative: 16,
      },
      {
        labelKey: "inflight_experience_food_beverage",
        labelDisplay: "Inflight food & beverage",
        count: 20,
        trend: "down",
        positive: 9,
        negative: 11,
      },
      {
        labelKey: "boarding_process",
        labelDisplay: "Boarding process",
        count: 18,
        trend: "up",
        positive: 6,
        negative: 12,
      },
    ],
    // 7 daily points
    trend: [
      { label: "D1", positive: 26, negative: 9 },
      { label: "D2", positive: 28, negative: 12 },
      { label: "D3", positive: 25, negative: 11 },
      { label: "D4", positive: 30, negative: 13 },
      { label: "D5", positive: 28, negative: 14 },
      { label: "D6", positive: 29, negative: 18 },
      { label: "D7", positive: 29, negative: 18 },
    ],
  },

  /**
   * MONTHLY – your original numbers
   */
  monthly: MONTHLY_MANAGER_STATS,

  /**
   * YEARLY – much larger volume, similar ratios, gentle seasonal pattern
   */
  yearly: {
    periodLabel: "Last 12 months",
    totalReviews: 14600,
    uniqueReviews: 5600,
    processedSegments: 14600,
    positive: 9850,
    negative: 4750,
    highPriority: 2100,
    mediumPriority: 6400,
    lowPriority: 6100,
    departments: [
      {
        id: "TGS",
        name: "TGS - Yer Hizmetleri",
        totalReviews: 5000,
        highPriority: 900,
        positive: 3300,
        negative: 1700,
      },
      {
        id: "IUIUB",
        name: "İkram ve Uçak İçi Ürünler Bşk.",
        totalReviews: 3700,
        highPriority: 650,
        positive: 2700,
        negative: 1000,
      },
      {
        id: "BMCOGM",
        name: "Yer İşletme Bşk - Bagaj",
        totalReviews: 3300,
        highPriority: 400,
        positive: 1650,
        negative: 1650,
      },
      {
        id: "KHB",
        name: "Kabin Hizmetleri Bşk.",
        totalReviews: 2600,
        highPriority: 150,
        positive: 2200,
        negative: 400,
      },
    ],
    topIssues: [
      {
        labelKey: "baggage_lost",
        labelDisplay: "Baggage lost",
        count: 1440,
        trend: "up",
        positive: 120,
        negative: 1320,
      },
      {
        labelKey: "checkin_process",
        labelDisplay: "Check-in process",
        count: 1140,
        trend: "stable",
        positive: 420,
        negative: 720,
      },
      {
        labelKey: "inflight_experience_food_beverage",
        labelDisplay: "Inflight food & beverage",
        count: 960,
        trend: "down",
        positive: 420,
        negative: 540,
      },
      {
        labelKey: "boarding_process",
        labelDisplay: "Boarding process",
        count: 864,
        trend: "up",
        positive: 300,
        negative: 564,
      },
    ],
    // 12 months with a mild "busy summer" bulge
    trend: [
      { label: "M1", positive: 700, negative: 220 },
      { label: "M2", positive: 720, negative: 230 },
      { label: "M3", positive: 780, negative: 250 },
      { label: "M4", positive: 820, negative: 260 },
      { label: "M5", positive: 860, negative: 280 },
      { label: "M6", positive: 900, negative: 310 },
      { label: "M7", positive: 920, negative: 320 },
      { label: "M8", positive: 910, negative: 315 },
      { label: "M9", positive: 880, negative: 300 },
      { label: "M10", positive: 840, negative: 290 },
      { label: "M11", positive: 820, negative: 280 },
      { label: "M12", positive: 780, negative: 280 },
    ],
  },
};
