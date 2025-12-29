import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  DEPARTMENT_CODE_TO_LABEL,
  type DepartmentCode,
} from "../departmentConfig";

type Role = "admin" | "manager" | "viewer";

export default function CreateUser() {
  const navigate = useNavigate();
  const { token } = useAuth();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("viewer");
  const [department, setDepartment] = useState<DepartmentCode | "">("");

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!username.trim() || !email.trim() || !password) {
      setError("Please fill in all required fields.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (role === "viewer" && !department) {
      setError("Viewer users must be assigned a department.");
      return;
    }

    setIsSubmitting(true);

    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/api/auth/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            username: username.trim(),
            email: email.trim(),
            password,
            role,
            department: role === "viewer" ? department : null,
          }),
        }
      );

      // SAFE response parsing (no JSON crash)
      let data: any = null;
      try {
        const text = await res.text();
        data = text ? JSON.parse(text) : null;
      } catch {
        data = null;
      }

      if (!res.ok) {
        throw new Error(
          data?.detail || data?.error || "Failed to create user"
        );
      }

      setSuccess(`User "${username}" created successfully.`);
      setUsername("");
      setEmail("");
      setPassword("");
      setRole("viewer");
      setDepartment("");
    } catch (err: any) {
      setError(err.message || "Failed to create user.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 px-8">
      <div className="w-full max-w-lg bg-white dark:bg-slate-900 rounded-xl shadow p-8">
        <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500 mb-2">
          Admin Panel
        </p>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50 mb-1">
          Create User
        </h2>

        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
          Only administrators can create new users.
        </p>

        <form className="space-y-4" onSubmit={handleSubmit}>
          {/* Username */}
          <input
            className="input"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isSubmitting}
          />

          {/* Email */}
          <input
            className="input"
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isSubmitting}
          />

          {/* Password */}
          <input
            className="input"
            type="password"
            placeholder="Password (min 8 chars)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isSubmitting}
          />

          {/* Role */}
          <select
            className="input"
            value={role}
            onChange={(e) => setRole(e.target.value as Role)}
            disabled={isSubmitting}
          >
            <option value="viewer">Viewer</option>
            <option value="manager">Manager</option>
            <option value="admin">Admin</option>
          </select>

          {/* Department (only for viewer) */}
          {role === "viewer" && (
            <select
              className="input"
              value={department}
              onChange={(e) =>
                setDepartment(e.target.value as DepartmentCode)
              }
              disabled={isSubmitting}
            >
              <option value="">Select department</option>
              {Object.entries(DEPARTMENT_CODE_TO_LABEL).map(
                ([code, label]) => (
                  <option key={code} value={code}>
                    {label}
                  </option>
                )
              )}
            </select>
          )}

          {/* Error */}
          {error && <div className="error-box">{error}</div>}

          {/* Success */}
          {success && <div className="success-box">{success}</div>}

          {/* Submit */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary"
          >
            {isSubmitting ? "Creating…" : "Create User"}
          </button>
        </form>

        <button
          onClick={() => navigate("/dashboard")}
          className="mt-4 text-xs text-slate-500 underline"
        >
          Back to dashboard
        </button>
      </div>
    </div>
  );
}
