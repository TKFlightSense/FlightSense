export type DepartmentCode = "IUIUB" | "BMCOGM" | "KHB" | "TGS" | "RVBCM" | "CMYM" | "GYB";
export type DepartmentId = DepartmentCode; // Alias for compatibility

export type DepartmentLabel =
  | "İkram ve Uçak İçi Ürünler Başkanlığı"
  | "Bagaj Müşteri Çözümleri ve Operasyon Geliştirme Müdürlüğü"
  | "Kabin Hizmetleri Başkanlığı"
  | "Turkish Ground Services"
  | "Rezervasyon ve Biletleme Çözümleri Müdürlüğü"
  | "Çağrı Merkezi Yönetim Müdürlüğü"
  | "Gelir Yönetimi Başkanlığı";


export const DEPARTMENT_LABEL_TO_CODE: Record<DepartmentLabel, DepartmentCode> = {
  "İkram ve Uçak İçi Ürünler Başkanlığı": "IUIUB",
  "Bagaj Müşteri Çözümleri ve Operasyon Geliştirme Müdürlüğü": "BMCOGM",
  "Kabin Hizmetleri Başkanlığı": "KHB",
  "Turkish Ground Services": "TGS",
  "Rezervasyon ve Biletleme Çözümleri Müdürlüğü": "RVBCM",
  "Çağrı Merkezi Yönetim Müdürlüğü": "CMYM",
  "Gelir Yönetimi Başkanlığı": "GYB",
};


export const DEPARTMENT_CODE_TO_LABEL: Record<DepartmentCode, DepartmentLabel> = Object.entries(
  DEPARTMENT_LABEL_TO_CODE
).reduce((acc, [label, code]) => {
  acc[code as DepartmentCode] = label as DepartmentLabel;
  return acc;
}, {} as Record<DepartmentCode, DepartmentLabel>);

/**
 * Jira project keys for each department.
 * These map to Jira project URLs like: https://your-jira-instance.atlassian.net/jira/software/projects/{KEY}/boards
 */
export const DEPARTMENT_JIRA_PROJECT_KEY: Record<DepartmentCode, string> = {
  IUIUB: "IUIUB",
  BMCOGM: "BMCOGM",
  KHB: "KHB",
  TGS: "TGS",
  RVBCM: "RVBCM",
  CMYM: "CMYM",
  GYB: "GYB",
};

/**
 * Map from department label (as returned by backend) to Jira project key.
 * These keys are also used as backend department codes for API calls.
 */
export const DEPARTMENT_LABEL_TO_JIRA_KEY: Record<string, string> = {
  "İkram ve Uçak İçi Ürünler Başkanlığı": "IUIUB",
  "Bagaj Müşteri Çözümleri ve Operasyon Geliştirme Müdürlüğü": "BMCOGM",
  "Kabin Hizmetleri Başkanlığı": "KHB",
  "Turkish Ground Services": "TGS",
  "Rezervasyon ve Biletleme Çözümleri Müdürlüğü": "RVBCM",
  "Çağrı Merkezi Yönetim Müdürlüğü": "CMYM",
  "Gelir Yönetimi Başkanlığı": "GYB",
};

/**
 * Map from Jira project key (also backend code) to department display label.
 */
export const JIRA_KEY_TO_DEPARTMENT_LABEL: Record<string, string> = {
  "IUIUB": "İkram ve Uçak İçi Ürünler Başkanlığı",
  "BMCOGM": "Bagaj Müşteri Çözümleri ve Operasyon Geliştirme Müdürlüğü",
  "KHB": "Kabin Hizmetleri Başkanlığı",
  "TGS": "Turkish Ground Services",
  "RVBCM": "Rezervasyon ve Biletleme Çözümleri Müdürlüğü",
  "CMYM": "Çağrı Merkezi Yönetim Müdürlüğü",
  "GYB": "Gelir Yönetimi Başkanlığı",
};

/**
 * Base URL for your Jira instance.
 */
export const JIRA_BASE_URL = "https://tkflightsense.atlassian.net";

/**
 * Get the full Jira project URL for a department.
 * @param jiraKey - The Jira project key (e.g., "KHB", "TGS")
 */
export function getJiraProjectUrl(jiraKey: string): string {
  return `${JIRA_BASE_URL}/jira/core/projects/${jiraKey}`;
}
