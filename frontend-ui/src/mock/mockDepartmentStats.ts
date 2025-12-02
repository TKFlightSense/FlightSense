import type { DepartmentId } from "../departmentConfig";

export type DepartmentIssue = {
  labelKey: string;
  labelDisplay: string;
  count: number;
  trend: "up" | "down" | "flat";
  positive: number;
  negative: number;
};

export type DeptTrendPoint = {
  label: string;
  positive: number;
  negative: number;
};

export type DepartmentStats = {
  departmentId: DepartmentId;
  name: string;
  periodLabel: string;
  totalReviews: number;
  positive: number;
  negative: number;
  highPriority: number;
  mediumPriority: number;
  lowPriority: number;
  topIssues: DepartmentIssue[];
  trend: DeptTrendPoint[];
};

export type TimeRangeKey = "weekly" | "monthly" | "yearly";

/**
 * MONTHLY BASELINE – same totals as before, just extended with issue-level pos/neg.
 */
export const MONTHLY_DEPARTMENT_STATS: Record<DepartmentId, DepartmentStats> = {
  IUIUB: {
    departmentId: "IUIUB",
    name: "İkram ve Uçak İçi Ürünler Başkanlığı",
    periodLabel: "Last 30 days",
    totalReviews: 310,
    positive: 230,
    negative: 80,
    highPriority: 50,
    mediumPriority: 140,
    lowPriority: 120,
    topIssues: [
      {
        labelKey: "inflight_experience_food_beverage",
        labelDisplay: "Food & beverage quality",
        count: 60,
        trend: "down",
        positive: 20,
        negative: 40,
      },
      {
        labelKey: "inflight_experience_entertainment",
        labelDisplay: "IFE content / screens",
        count: 35,
        trend: "flat",
        positive: 22,
        negative: 13,
      },
    ],
    trend: [
      { label: "W1", positive: 60, negative: 25 },
      { label: "W2", positive: 55, negative: 18 },
      { label: "W3", positive: 65, negative: 20 },
      { label: "W4", positive: 50, negative: 17 },
    ],
  },
  BMCOGM: {
    departmentId: "BMCOGM",
    name: "Yer İşletme Bşk - Bagaj Müşteri Çözümleri ve Operasyon Geliştirme Md.",
    periodLabel: "Last 30 days",
    totalReviews: 280,
    positive: 150,
    negative: 130,
    highPriority: 40,
    mediumPriority: 120,
    lowPriority: 120,
    topIssues: [
      {
        labelKey: "baggage_lost",
        labelDisplay: "Lost baggage",
        count: 80,
        trend: "up",
        positive: 8,
        negative: 72,
      },
      {
        labelKey: "baggage_damaged",
        labelDisplay: "Damaged baggage",
        count: 40,
        trend: "flat",
        positive: 10,
        negative: 30,
      },
    ],
    trend: [
      { label: "W1", positive: 40, negative: 25 },
      { label: "W2", positive: 55, negative: 38 },
      { label: "W3", positive: 65, negative: 20 },
      { label: "W4", positive: 20, negative: 23 },
    ],
  },
  KABIN: {
    departmentId: "KABIN",
    name: "Kabin Hizmetleri Başkanlığı",
    periodLabel: "Last 30 days",
    totalReviews: 230,
    positive: 170,
    negative: 60,
    highPriority: 15,
    mediumPriority: 90,
    lowPriority: 125,
    topIssues: [
      {
        labelKey: "inflight_experience_cleanliness",
        labelDisplay: "Cabin cleanliness",
        count: 35,
        trend: "flat",
        positive: 26,
        negative: 9,
      },
    ],
    trend: [
      { label: "W1", positive: 30, negative: 25 },
      { label: "W2", positive: 25, negative: 18 },
      { label: "W3", positive: 35, negative: 30 },
      { label: "W4", positive: 50, negative: 17 },
    ],
  },
  TGS: {
    departmentId: "TGS",
    name: "TGS - Yer Hizmetleri",
    periodLabel: "Last 30 days",
    totalReviews: 420,
    positive: 280,
    negative: 140,
    highPriority: 75,
    mediumPriority: 190,
    lowPriority: 155,
    topIssues: [
      {
        labelKey: "checkin_process",
        labelDisplay: "Check-in queues & staff",
        count: 55,
        trend: "flat",
        positive: 20,
        negative: 35,
      },
      {
        labelKey: "boarding_process",
        labelDisplay: "Boarding process",
        count: 45,
        trend: "up",
        positive: 18,
        negative: 27,
      },
    ],
    trend: [
      { label: "W1", positive: 60, negative: 15 },
      { label: "W2", positive: 55, negative: 28 },
      { label: "W3", positive: 45, negative: 20 },
      { label: "W4", positive: 50, negative: 17 },
    ],
  },
  RVCBM: {
    departmentId: "RVCBM",
    name: "Rezervasyon ve Biletleme Çzm. Mdr.",
    periodLabel: "Last 30 days",
    totalReviews: 0,
    positive: 0,
    negative: 0,
    highPriority: 0,
    mediumPriority: 0,
    lowPriority: 0,
    topIssues: [],
    trend: [],
  },
  CMYM: {
    departmentId: "CMYM",
    name: "Çağrı Merkezi Yönetimi Mdr.",
    periodLabel: "Last 30 days",
    totalReviews: 0,
    positive: 0,
    negative: 0,
    highPriority: 0,
    mediumPriority: 0,
    lowPriority: 0,
    topIssues: [],
    trend: [],
  },
};

/**
 * PER-RANGE VARIANTS – weekly and yearly tuned around the monthly baseline.
 */
export const MOCK_DEPARTMENT_STATS_BY_RANGE: Record<
  DepartmentId,
  Record<TimeRangeKey, DepartmentStats>
> = {
  IUIUB: {
    weekly: {
      departmentId: "IUIUB",
      name: "İkram ve Uçak İçi Ürünler Başkanlığı",
      periodLabel: "Last 7 days",
      totalReviews: 75,
      positive: 56,
      negative: 19,
      highPriority: 12,
      mediumPriority: 34,
      lowPriority: 29,
      topIssues: [
        {
          labelKey: "inflight_experience_food_beverage",
          labelDisplay: "Food & beverage quality",
          count: 15,
          trend: "down",
          positive: 5,
          negative: 10,
        },
        {
          labelKey: "inflight_experience_entertainment",
          labelDisplay: "IFE content / screens",
          count: 9,
          trend: "flat",
          positive: 6,
          negative: 3,
        },
      ],
      trend: [
        { label: "D1", positive: 7, negative: 3 },
        { label: "D2", positive: 8, negative: 2 },
        { label: "D3", positive: 7, negative: 3 },
        { label: "D4", positive: 8, negative: 3 },
        { label: "D5", positive: 9, negative: 3 },
        { label: "D6", positive: 9, negative: 3 },
        { label: "D7", positive: 8, negative: 2 },
      ],
    },
    monthly: MONTHLY_DEPARTMENT_STATS.IUIUB,
    yearly: {
      departmentId: "IUIUB",
      name: "İkram ve Uçak İçi Ürünler Başkanlığı",
      periodLabel: "Last 12 months",
      totalReviews: 3700,
      positive: 2700,
      negative: 1000,
      highPriority: 620,
      mediumPriority: 1650,
      lowPriority: 1430,
      topIssues: [
        {
          labelKey: "inflight_experience_food_beverage",
          labelDisplay: "Food & beverage quality",
          count: 720,
          trend: "down",
          positive: 260,
          negative: 460,
        },
        {
          labelKey: "inflight_experience_entertainment",
          labelDisplay: "IFE content / screens",
          count: 430,
          trend: "flat",
          positive: 270,
          negative: 160,
        },
      ],
      trend: [
        { label: "M1", positive: 180, negative: 60 },
        { label: "M2", positive: 190, negative: 70 },
        { label: "M3", positive: 200, negative: 75 },
        { label: "M4", positive: 220, negative: 80 },
        { label: "M5", positive: 230, negative: 85 },
        { label: "M6", positive: 240, negative: 90 },
        { label: "M7", positive: 245, negative: 90 },
        { label: "M8", positive: 240, negative: 90 },
        { label: "M9", positive: 230, negative: 85 },
        { label: "M10", positive: 225, negative: 80 },
        { label: "M11", positive: 215, negative: 80 },
        { label: "M12", positive: 205, negative: 75 },
      ],
    },
  },

  BMCOGM: {
    weekly: {
      departmentId:
        "BMCOGM",
      name: "Yer İşletme Bşk - Bagaj Müşteri Çözümleri ve Operasyon Geliştirme Md.",
      periodLabel: "Last 7 days",
      totalReviews: 65,
      positive: 35,
      negative: 30,
      highPriority: 10,
      mediumPriority: 28,
      lowPriority: 27,
      topIssues: [
        {
          labelKey: "baggage_lost",
          labelDisplay: "Lost baggage",
          count: 22,
          trend: "up",
          positive: 2,
          negative: 20,
        },
        {
          labelKey: "baggage_damaged",
          labelDisplay: "Damaged baggage",
          count: 10,
          trend: "flat",
          positive: 2,
          negative: 8,
        },
      ],
      trend: [
        { label: "D1", positive: 5, negative: 4 },
        { label: "D2", positive: 6, negative: 5 },
        { label: "D3", positive: 4, negative: 6 },
        { label: "D4", positive: 7, negative: 5 },
        { label: "D5", positive: 5, negative: 6 },
        { label: "D6", positive: 4, negative: 4 },
        { label: "D7", positive: 4, negative: 4 },
      ],
    },
    monthly:
      MONTHLY_DEPARTMENT_STATS[
        "BMCOGM"
      ],
    yearly: {
      departmentId:
        "BMCOGM",
      name: "Yer İşletme Bşk - Bagaj Müşteri Çözümleri ve Operasyon Geliştirme Md.",
      periodLabel: "Last 12 months",
      totalReviews: 3300,
      positive: 1650,
      negative: 1650,
      highPriority: 380,
      mediumPriority: 1500,
      lowPriority: 1420,
      topIssues: [
        {
          labelKey: "baggage_lost",
          labelDisplay: "Lost baggage",
          count: 900,
          trend: "up",
          positive: 90,
          negative: 810,
        },
        {
          labelKey: "baggage_damaged",
          labelDisplay: "Damaged baggage",
          count: 500,
          trend: "flat",
          positive: 120,
          negative: 380,
        },
      ],
      trend: [
        { label: "M1", positive: 120, negative: 110 },
        { label: "M2", positive: 130, negative: 115 },
        { label: "M3", positive: 135, negative: 120 },
        { label: "M4", positive: 140, negative: 125 },
        { label: "M5", positive: 145, negative: 130 },
        { label: "M6", positive: 150, negative: 140 },
        { label: "M7", positive: 155, negative: 145 },
        { label: "M8", positive: 150, negative: 140 },
        { label: "M9", positive: 145, negative: 135 },
        { label: "M10", positive: 140, negative: 130 },
        { label: "M11", positive: 135, negative: 125 },
        { label: "M12", positive: 130, negative: 125 },
      ],
    },
  },

  KABIN: {
    weekly: {
      departmentId: "KABIN",
      name: "Kabin Hizmetleri Başkanlığı",
      periodLabel: "Last 7 days",
      totalReviews: 50,
      positive: 38,
      negative: 12,
      highPriority: 3,
      mediumPriority: 18,
      lowPriority: 29,
      topIssues: [
        {
          labelKey: "inflight_experience_cleanliness",
          labelDisplay: "Cabin cleanliness",
          count: 10,
          trend: "flat",
          positive: 8,
          negative: 2,
        },
      ],
      trend: [
        { label: "D1", positive: 6, negative: 2 },
        { label: "D2", positive: 5, negative: 2 },
        { label: "D3", positive: 6, negative: 1 },
        { label: "D4", positive: 7, negative: 2 },
        { label: "D5", positive: 5, negative: 2 },
        { label: "D6", positive: 5, negative: 2 },
        { label: "D7", positive: 4, negative: 1 },
      ],
    },
    monthly: MONTHLY_DEPARTMENT_STATS.KABIN,
    yearly: {
      departmentId: "KABIN",
      name: "Kabin Hizmetleri Başkanlığı",
      periodLabel: "Last 12 months",
      totalReviews: 2600,
      positive: 2000,
      negative: 600,
      highPriority: 140,
      mediumPriority: 950,
      lowPriority: 1510,
      topIssues: [
        {
          labelKey: "inflight_experience_cleanliness",
          labelDisplay: "Cabin cleanliness",
          count: 420,
          trend: "flat",
          positive: 320,
          negative: 100,
        },
      ],
      trend: [
        { label: "M1", positive: 150, negative: 50 },
        { label: "M2", positive: 155, negative: 50 },
        { label: "M3", positive: 160, negative: 55 },
        { label: "M4", positive: 170, negative: 55 },
        { label: "M5", positive: 175, negative: 55 },
        { label: "M6", positive: 180, negative: 60 },
        { label: "M7", positive: 185, negative: 60 },
        { label: "M8", positive: 180, negative: 55 },
        { label: "M9", positive: 175, negative: 50 },
        { label: "M10", positive: 170, negative: 50 },
        { label: "M11", positive: 165, negative: 50 },
        { label: "M12", positive: 160, negative: 50 },
      ],
    },
  },

  TGS: {
    weekly: {
      departmentId: "TGS",
      name: "TGS - Yer Hizmetleri",
      periodLabel: "Last 7 days",
      totalReviews: 100,
      positive: 66,
      negative: 34,
      highPriority: 20,
      mediumPriority: 40,
      lowPriority: 40,
      topIssues: [
        {
          labelKey: "checkin_process",
          labelDisplay: "Check-in queues & staff",
          count: 18,
          trend: "flat",
          positive: 6,
          negative: 12,
        },
        {
          labelKey: "boarding_process",
          labelDisplay: "Boarding process",
          count: 14,
          trend: "up",
          positive: 5,
          negative: 9,
        },
      ],
      trend: [
        { label: "D1", positive: 9, negative: 3 },
        { label: "D2", positive: 10, negative: 4 },
        { label: "D3", positive: 8, negative: 4 },
        { label: "D4", positive: 11, negative: 5 },
        { label: "D5", positive: 9, negative: 6 },
        { label: "D6", positive: 10, negative: 6 },
        { label: "D7", positive: 9, negative: 6 },
      ],
    },
    monthly: MONTHLY_DEPARTMENT_STATS.TGS,
    yearly: {
      departmentId: "TGS",
      name: "TGS - Yer Hizmetleri",
      periodLabel: "Last 12 months",
      totalReviews: 5000,
      positive: 3300,
      negative: 1700,
      highPriority: 900,
      mediumPriority: 2300,
      lowPriority: 1800,
      topIssues: [
        {
          labelKey: "checkin_process",
          labelDisplay: "Check-in queues & staff",
          count: 700,
          trend: "flat",
          positive: 260,
          negative: 440,
        },
        {
          labelKey: "boarding_process",
          labelDisplay: "Boarding process",
          count: 620,
          trend: "up",
          positive: 240,
          negative: 380,
        },
      ],
      trend: [
        { label: "M1", positive: 260, negative: 90 },
        { label: "M2", positive: 270, negative: 95 },
        { label: "M3", positive: 280, negative: 100 },
        { label: "M4", positive: 290, negative: 110 },
        { label: "M5", positive: 300, negative: 115 },
        { label: "M6", positive: 310, negative: 120 },
        { label: "M7", positive: 315, negative: 125 },
        { label: "M8", positive: 310, negative: 125 },
        { label: "M9", positive: 300, negative: 120 },
        { label: "M10", positive: 290, negative: 115 },
        { label: "M11", positive: 280, negative: 110 },
        { label: "M12", positive: 275, negative: 105 },
      ],
    },
  },
  RVCBM: {
    weekly: {
      departmentId: "RVCBM",
      name: "Rezervasyon ve Biletleme Çzm. Mdr.",
      periodLabel: "Last 7 days",
      totalReviews: 0,
      positive: 0,
      negative: 0,
      highPriority: 0,
      mediumPriority: 0,
      lowPriority: 0,
      topIssues: [],
      trend: [],
    },
    monthly: {
      departmentId: "RVCBM",
      name: "Rezervasyon ve Biletleme Çzm. Mdr.",
      periodLabel: "Last 30 days",
      totalReviews: 0,
      positive: 0,
      negative: 0,
      highPriority: 0,
      mediumPriority: 0,
      lowPriority: 0,
      topIssues: [],
      trend: [],
    },
    yearly: {
      departmentId: "RVCBM",
      name: "Rezervasyon ve Biletleme Çzm. Mdr.",
      periodLabel: "Last 12 months",
      totalReviews: 0,
      positive: 0,
      negative: 0,
      highPriority: 0,
      mediumPriority: 0,
      lowPriority: 0,
      topIssues: [],
      trend: [],
    },
  },
  CMYM: {
    weekly: {
      departmentId: "CMYM",
      name: "Çağrı Merkezi Yönetimi Mdr.",
      periodLabel: "Last 7 days",
      totalReviews: 0,
      positive: 0,
      negative: 0,
      highPriority: 0,
      mediumPriority: 0,
      lowPriority: 0,
      topIssues: [],
      trend: [],
    },
    monthly: {
      departmentId: "CMYM",
      name: "Çağrı Merkezi Yönetimi Mdr.",
      periodLabel: "Last 30 days",
      totalReviews: 0,
      positive: 0,
      negative: 0,
      highPriority: 0,
      mediumPriority: 0,
      lowPriority: 0,
      topIssues: [],
      trend: [],
    },
    yearly: {
      departmentId: "CMYM",
      name: "Çağrı Merkezi Yönetimi Mdr.",
      periodLabel: "Last 12 months",
      totalReviews: 0,
      positive: 0,
      negative: 0,
      highPriority: 0,
      mediumPriority: 0,
      lowPriority: 0,
      topIssues: [],
      trend: [],
    },
  },
};
