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

/**
 * Jira project keys for each department.
 * These map to Jira project URLs like: https://your-jira-instance.atlassian.net/jira/software/projects/{KEY}/boards
 */
export const DEPARTMENT_JIRA_PROJECT_KEY: Record<DepartmentCode, string> = {
  IUIUB: "IUIUB",
  BMCOGM: "BMCOGM",
  KABIN: "KHB",
  TGS: "TGS",
  RVCBM: "RVBCM",
  CMYM: "CMYM",
};

/**
 * Map from department label (as returned by backend) to Jira project key.
 * These keys are also used as backend department codes for API calls.
 */
export const DEPARTMENT_LABEL_TO_JIRA_KEY: Record<string, string> = {
  "İkram ve Uçak İçi Ürünler Bşk.": "IUIUB",
  "Yer İşletme Bşk - Bagaj": "BMCOGM",
  "Kabin Hizmetleri Bşk.": "KHB",
  "TGS - Yer Hizmetleri": "TGS",
  "Rezervasyon ve Biletleme Çzm. Mdr.": "RVCBM",
  "Çağrı Merkezi Yönetimi Mdr.": "CMYM",
};

/**
 * Map from Jira project key (also backend code) to department display label.
 */
export const JIRA_KEY_TO_DEPARTMENT_LABEL: Record<string, string> = {
  "IUIUB": "İkram ve Uçak İçi Ürünler Bşk.",
  "BMCOGM": "Yer İşletme Bşk - Bagaj",
  "KHB": "Kabin Hizmetleri Bşk.",
  "TGS": "TGS - Yer Hizmetleri",
  "RVCBM": "Rezervasyon ve Biletleme Çzm. Mdr.",
  "CMYM": "Çağrı Merkezi Yönetimi Mdr.",
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
