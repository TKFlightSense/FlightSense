import type { DepartmentId } from "../departmentConfig";

export type UserRole = "admin" | "manager" | "department_viewer";

export type MockUser = {
  username: string;
  password: string;
  role: UserRole;
  departmentId?: DepartmentId;
};

/** Where we store the logged-in user */
export const LOCAL_STORAGE_USER_KEY = "flightsense_user";

/** Mock users for development/demo */
export const MOCK_USERS: MockUser[] = [
  {
    username: "admin",
    password: "admin123",
    role: "admin",
  },
  {
    username: "manager",
    password: "manager123",
    role: "manager",
  },
  {
    username: "ikram.user",
    password: "test123",
    role: "department_viewer",
    departmentId: "IUIUB",
  },
  {
    username: "bagaj.user",
    password: "test123",
    role: "department_viewer",
    departmentId: "BMCOGM",
  },
  {
    username: "kabin.user",
    password: "test123",
    role: "department_viewer",
    departmentId: "KABIN",
  },
  {
    username: "tgs.user",
    password: "test123",
    role: "department_viewer",
    departmentId: "TGS",
  },
];
