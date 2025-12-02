import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  MOCK_USERS,
  type MockUser,
  type UserRole,
} from "../mock/mockAuth";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { loginFromMock } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const trimmedUsername = username.trim();

    if (!trimmedUsername || !password) {
      setError("Please enter both username and password.");
      return;
    }

    setIsSubmitting(true);

    setTimeout(() => {
      const user: MockUser | undefined = MOCK_USERS.find(
        (u) =>
          u.username.toLowerCase() === trimmedUsername.toLowerCase() &&
          u.password === password
      );

      if (!user) {
        setIsSubmitting(false);
        setError("Invalid username or password.");
        return;
      }

      // tell AuthContext to log in & persist
      loginFromMock(user);

      // Redirect based on role
      if (user.role === "admin" || user.role === "manager") {
        navigate("/dashboard");
      } else if (user.role === "department_viewer" && user.departmentId) {
        navigate(`/department/${user.departmentId}`);
      } else {
        navigate("/dashboard");
      }

      setIsSubmitting(false);
    }, 300);
  }

  return (
    <div className="h-screen flex items-center justify-center bg-slate-100">
      <div className="bg-white shadow-xl rounded-2xl px-8 py-10 w-full max-w-md">
        <h1 className="text-2xl font-bold mb-2 text-slate-900">
          FlightSense Login
        </h1>
        <p className="text-sm text-slate-600 mb-6">
          Use one of the mock accounts to see how different roles are
          routed to different dashboards.
        </p>

        <form className="space-y-4" onSubmit={handleSubmit}>
          {/* Username */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Username
            </label>
            <input
              type="text"
              autoComplete="username"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g. admin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Password
            </label>
            <input
              type="password"
              autoComplete="current-password"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {/* Error message */}
          {error && (
            <div className="rounded-md bg-rose-50 border border-rose-200 px-3 py-2 text-xs text-rose-700">
              {error}
            </div>
          )}

          {/* Submit button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full mt-2 bg-blue-600 text-white py-2.5 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-70 disabled:cursor-not-allowed transition"
          >
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
