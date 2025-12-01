import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import type { DepartmentId } from "../departmentConfig";
import {
  LOCAL_STORAGE_USER_KEY,
  type MockUser,
  type UserRole,
} from "../mock/mockAuth";

export type AuthUser = {
  username: string;
  role: UserRole;
  departmentId: DepartmentId | null;
};

type AuthContextValue = {
  user: AuthUser | null;
  isLoggedIn: boolean;
  isLoading: boolean;
  loginFromMock: (user: MockUser) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load session from localStorage on first render
  useEffect(() => {
    const raw = localStorage.getItem(LOCAL_STORAGE_USER_KEY);
    if (!raw) {
      setIsLoading(false);
      return;
    }
    try {
      const parsed = JSON.parse(raw) as AuthUser;
      setUser({
        username: parsed.username,
        role: parsed.role,
        departmentId: parsed.departmentId ?? null,
      });
    } catch {
      // ignore corrupted data
    } finally {
      setIsLoading(false);
    }
  }, []);

  function loginFromMock(mockUser: MockUser) {
    const authUser: AuthUser = {
      username: mockUser.username,
      role: mockUser.role,
      departmentId: mockUser.departmentId ?? null,
    };
    setUser(authUser);
    localStorage.setItem(LOCAL_STORAGE_USER_KEY, JSON.stringify(authUser));
  }

  function logout() {
    setUser(null);
    localStorage.removeItem(LOCAL_STORAGE_USER_KEY);
  }

  const value: AuthContextValue = {
    user,
    isLoggedIn: !!user,
    isLoading,
    loginFromMock,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
