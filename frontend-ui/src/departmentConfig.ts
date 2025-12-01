export type DepartmentId =
  | "IkramveUcakIciUrunlerBsk"
  | "YerIsletmeBsk-BagajMusteriCozumleriveOperasyonGelistirmeMudurlugu"
  | "KabinHizmetleriBsk"
  | "TGS";

export type Department = {
  id: DepartmentId;
  name: string;
  labels: string[];
};

export const departments: Department[] = [
  {
    id: "IkramveUcakIciUrunlerBsk",
    name: "İkram ve Uçak İçi Ürünler Başkanlığı",
    labels: [
      "inflight_experience_food_beverage",
      "inflight_experience_entertainment",
    ],
  },
  {
    id: "YerIsletmeBsk-BagajMusteriCozumleriveOperasyonGelistirmeMudurlugu",
    name: "Yer İşletme Bşk - Bagaj Müşteri Çözümleri ve Operasyon Geliştirme Md.",
    labels: ["baggage_lost", "baggage_damaged"],
  },
  {
    id: "KabinHizmetleriBsk",
    name: "Kabin Hizmetleri Başkanlığı",
    labels: ["inflight_experience_cleanliness"],
  },
  {
    id: "TGS",
    name: "TGS - Yer Hizmetleri",
    labels: ["checkin_process", "boarding_process"],
  },
];
