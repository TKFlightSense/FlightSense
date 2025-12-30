export type UserRole = "admin" | "manager" | "viewer";

export type DepartmentCode = "IUIUB" | "BMCOGM" | "KHB" | "TGS" | "RVBCM" | "CMYM" | "GYB";
export type DepartmentId = DepartmentCode; // Alias for compatibility

export type DepartmentLabel =
  | "In-Flight Catering & Onboard Products"
  | "Baggage Customer Solutions & Operational Improvement"
  | "Cabin Services"
  | "Turkish Ground Services"
  | "Reservations & Ticketing Solutions"
  | "Call Center Management"
  | "Revenue Management";

export const DEPARTMENT_LABEL_TO_CODE: Record<DepartmentLabel, DepartmentCode> = {
  "In-Flight Catering & Onboard Products": "IUIUB",
  "Baggage Customer Solutions & Operational Improvement": "BMCOGM",
  "Cabin Services": "KHB",
  "Turkish Ground Services": "TGS",
  "Reservations & Ticketing Solutions": "RVBCM",
  "Call Center Management": "CMYM",
  "Revenue Management": "GYB",
};

export const DEPARTMENT_CODE_TO_LABEL: Record<DepartmentCode, DepartmentLabel> = {
  IUIUB: "In-Flight Catering & Onboard Products",
  BMCOGM: "Baggage Customer Solutions & Operational Improvement",
  KHB: "Cabin Services",
  TGS: "Turkish Ground Services",
  RVBCM: "Reservations & Ticketing Solutions",
  CMYM: "Call Center Management",
  GYB: "Revenue Management",
};


export const LABEL_KEY_TO_NAME: Record <string, string> = {
  inflight_experience_food_beverage: "Food & Beverage Quality",
  inflight_experience_entertainment: "In-Flight Entertainment",
  inflight_experience_seats_comfort: "Seats & Comfort",
  inflight_experience_cabin_service: "Cabin Crew Service",
  inflight_experience_cleanliness: "Cleanliness & Hygiene",
  checkin_process: "Check-in Process",
  boarding_process: "Boarding Process",
  flight_delay_cancellation: "Flight Delay / Cancellation",
  baggage_lost: "Lost Baggage",
  baggage_damaged: "Damaged Baggage",
  booking_and_ticketing: "Booking & Ticketing",
  customer_support: "Customer Support",
  pricing_and_loyalty: "Pricing & Loyalty",
};

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
 * Map from Jira project key (also backend code) to department display label.
 */
export const JIRA_KEY_TO_DEPARTMENT_LABEL: Record<DepartmentCode, DepartmentLabel> = DEPARTMENT_CODE_TO_LABEL;

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
