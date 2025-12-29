import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import type { UserRole } from "../departmentConfig";

type ProtectedRouteProps = {
  children: ReactNode;
  allowedRoles?: UserRole[]; // if omitted → any logged-in user
};

export default function ProtectedRoute({
  children,
  allowedRoles,
}: ProtectedRouteProps) {
  const { user, isLoggedIn, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-50">
        <div className="text-sm text-slate-500">Checking session…</div>
      </div>
    );
  }

  if (!isLoggedIn || !user) {
    return <Navigate to="/" replace state={{ from: location }} />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return (
      <div className="h-screen flex items-center justify-center bg-rose-50">
        <div className="bg-white px-6 py-4 rounded-xl shadow max-w-md">
          <p className="text-sm text-slate-800 font-semibold mb-1">
            Unauthorized
          </p>
          <p className="text-xs text-slate-500 mb-3">
            Your role (<span className="font-mono">{user.role}</span>) does not
            have access to this page.
          </p>
          <a href="/" className="text-xs text-blue-600 underline">
            Back to login
          </a>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
