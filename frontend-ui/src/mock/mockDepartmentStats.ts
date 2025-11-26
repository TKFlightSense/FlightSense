import type { DepartmentId } from "../departmentConfig";

export type DepartmentIssue = {
  labelKey: string;
  labelDisplay: string;
  count: number;
  trend: "up" | "down" | "flat";
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

// Simple map for quick lookup by id
export const MOCK_DEPARTMENT_STATS: Record<DepartmentId, DepartmentStats> = {
  IkramveUcakIciUrunlerBsk: {
    departmentId: "IkramveUcakIciUrunlerBsk",
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
      },
      {
        labelKey: "inflight_experience_entertainment",
        labelDisplay: "IFE content / screens",
        count: 35,
        trend: "flat",
      },
    ],
    trend: [
      { label: "W1", positive: 60, negative: 25 },
      { label: "W2", positive: 55, negative: 18 },
      { label: "W3", positive: 65, negative: 20 },
      { label: "W4", positive: 50, negative: 17 },
    ],
  },
  "YerIsletmeBsk-BagajMusteriCozumleriveOperasyonGelistirmeMudurlugu": {
    departmentId:
      "YerIsletmeBsk-BagajMusteriCozumleriveOperasyonGelistirmeMudurlugu",
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
      },
      {
        labelKey: "baggage_damaged",
        labelDisplay: "Damaged baggage",
        count: 40,
        trend: "flat",
      },
    ],
    trend: [
      { label: "W1", positive: 40, negative: 25 },
      { label: "W2", positive: 55, negative: 38 },
      { label: "W3", positive: 65, negative: 20 },
      { label: "W4", positive: 20, negative: 23 },
    ],
  },
  KabinHizmetleriBsk: {
    departmentId: "KabinHizmetleriBsk",
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
      },
      {
        labelKey: "boarding_process",
        labelDisplay: "Boarding process",
        count: 45,
        trend: "up",
      },
    ],
    trend: [
      { label: "W1", positive: 60, negative: 15 },
      { label: "W2", positive: 55, negative: 28 },
      { label: "W3", positive: 45, negative: 20 },
      { label: "W4", positive: 50, negative: 17 },
    ],
  },
};
