export type DepartmentCode = "IUIUB" | "BMCOGM" | "KABIN" | "TGS" | "RVCBM" | "CMYM";
export type DepartmentId = DepartmentCode; // Alias for compatibility

export type DepartmentLabel =
  | "İkram ve Uçak İçi Ürünler Bşk."
  | "Yer İşletme Bşk - Bagaj"
  | "Kabin Hizmetleri Bşk."
  | "TGS - Yer Hizmetleri"
  | "Rezervasyon ve Biletleme Çzm. Mdr."
  | "Çağrı Merkezi Yönetimi Mdr.";


export const DEPARTMENT_LABEL_TO_CODE: Record<DepartmentLabel, DepartmentCode> = {
  "İkram ve Uçak İçi Ürünler Bşk.": "IUIUB",
  "Yer İşletme Bşk - Bagaj": "BMCOGM",
  "Kabin Hizmetleri Bşk.": "KABIN",
  "TGS - Yer Hizmetleri": "TGS",
  "Rezervasyon ve Biletleme Çzm. Mdr.": "RVCBM",
  "Çağrı Merkezi Yönetimi Mdr.": "CMYM",
};


export const DEPARTMENT_CODE_TO_LABEL: Record<DepartmentCode, DepartmentLabel> = Object.entries(
  DEPARTMENT_LABEL_TO_CODE
).reduce((acc, [label, code]) => {
  acc[code as DepartmentCode] = label as DepartmentLabel;
  return acc;
}, {} as Record<DepartmentCode, DepartmentLabel>);
