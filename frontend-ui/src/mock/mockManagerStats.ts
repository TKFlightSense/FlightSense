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
  // simple trend indicator: +, -, or 0
  trend: "up" | "down" | "flat";
};

export type TrendPoint = {
  label: string;      // e.g. "Week 1" or "Day 01"
  positive: number;
  negative: number;
};

export type ManagerStats = {
  periodLabel: string; // e.g. "Last 30 days"
  totalReviews: number;
  positive: number;
  negative: number;
  highPriority: number;
  mediumPriority: number;
  lowPriority: number;
  departments: DepartmentSummary[];
  topIssues: TopIssue[];
  trend: TrendPoint[];
};

// 🚨 PURELY MOCK DATA FOR UI DEVELOPMENT
export const MOCK_MANAGER_STATS: ManagerStats = {
  periodLabel: "Last 30 days",
  totalReviews: 1240,
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
      id: "IkramveUcakIciUrunlerBsk",
      name: "İkram ve Uçak İçi Ürünler Bşk.",
      totalReviews: 310,
      highPriority: 50,
      positive: 230,
      negative: 80,
    },
    {
      id: "YerIsletmeBsk-BagajMusteriCozumleriveOperasyonGelistirmeMudurlugu",
      name: "Yer İşletme Bşk - Bagaj",
      totalReviews: 280,
      highPriority: 40,
      positive: 150,
      negative: 130,
    },
    {
      id: "KabinHizmetleriBsk",
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
    },
    {
      labelKey: "checkin_process",
      labelDisplay: "Check-in process",
      count: 95,
      trend: "flat",
    },
    {
      labelKey: "inflight_experience_food_beverage",
      labelDisplay: "Inflight food & beverage",
      count: 80,
      trend: "down",
    },
    {
      labelKey: "boarding_process",
      labelDisplay: "Boarding process",
      count: 72,
      trend: "up",
    },
  ],
  trend: [
    { label: "W1", positive: 180, negative: 70 },
    { label: "W2", positive: 210, negative: 95 },
    { label: "W3", positive: 200, negative: 120 },
    { label: "W4", positive: 240, negative: 125 },
  ],
};
