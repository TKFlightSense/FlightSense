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

const LOCAL_STORAGE_TOKEN_KEY = "flightsense_token";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export type AuthUser = {
  username: string;
  role: UserRole;
  departmentId: DepartmentId | null;
};

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  isLoggedIn: boolean;
  isLoading: boolean;
  loginFromMock: (user: MockUser) => void;
  login: (username: string, password: string) => Promise<AuthUser>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load session from localStorage on first render
  useEffect(() => {
    const rawUser = localStorage.getItem(LOCAL_STORAGE_USER_KEY);
    const storedToken = localStorage.getItem(LOCAL_STORAGE_TOKEN_KEY);

    if (rawUser && storedToken) {
      try {
        const parsed = JSON.parse(rawUser) as AuthUser;
        setUser({
          username: parsed.username,
          role: parsed.role,
          departmentId: parsed.departmentId ?? null,
        });
        setToken(storedToken);
      } catch {
        // ignore corrupted data
        localStorage.removeItem(LOCAL_STORAGE_USER_KEY);
        localStorage.removeItem(LOCAL_STORAGE_TOKEN_KEY);
      }
    } else if (rawUser) {
       // Fallback for mock-only sessions that might exist
       try {
        const parsed = JSON.parse(rawUser) as AuthUser;
        setUser(parsed);
       } catch {}
    }
    setIsLoading(false);
  }, []);

  function loginFromMock(mockUser: MockUser) {
    const authUser: AuthUser = {
      username: mockUser.username,
      role: mockUser.role,
      departmentId: mockUser.departmentId ?? null,
    };
    setUser(authUser);
    setToken(null); // Mock login has no token
    localStorage.setItem(LOCAL_STORAGE_USER_KEY, JSON.stringify(authUser));
    localStorage.removeItem(LOCAL_STORAGE_TOKEN_KEY);
  }

  async function login(username: string, password: string): Promise<AuthUser> {
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Login failed");
    }

    const data = await res.json();
    if (!data.success) {
      throw new Error(data.error || "Login failed");
    }

    const authUser: AuthUser = {
      username: data.user.username,
      role: data.user.role as UserRole,
      departmentId: (data.user.department as DepartmentId) || null,
    };

    setUser(authUser);
    setToken(data.token);
    localStorage.setItem(LOCAL_STORAGE_USER_KEY, JSON.stringify(authUser));
    localStorage.setItem(LOCAL_STORAGE_TOKEN_KEY, data.token);
    
    return authUser;
  }

  function logout() {
    setUser(null);
    setToken(null);
    localStorage.removeItem(LOCAL_STORAGE_USER_KEY);
    localStorage.removeItem(LOCAL_STORAGE_TOKEN_KEY);
  }

  const value: AuthContextValue = {
    user,
    token,
    isLoggedIn: !!user,
    isLoading,
    loginFromMock,
    login,
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
