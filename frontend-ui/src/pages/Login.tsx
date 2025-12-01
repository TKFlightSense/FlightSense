import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MOCK_USERS, type MockUser } from "../mock/mockAuth";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../hooks/useTheme";

import thyLogo from "../assets/thy-logo-2.png";

export default function Login() {
  const navigate = useNavigate();
  const { loginFromMock } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [logoSlideIn, setLogoSlideIn] = useState(false);

  useEffect(() => {
    const slideTimer = setTimeout(() => setLogoSlideIn(true), 100);
    return () => {
      clearTimeout(slideTimer);
    };
  }, []);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const trimmedUsername = username.trim();
    if (!trimmedUsername || !password) {
      setError("Please enter both username and password.");
      return;
    }

    setIsSubmitting(true);

    try {
      const user: MockUser | undefined = MOCK_USERS.find(
        (u) =>
          u.username.toLowerCase() === trimmedUsername.toLowerCase() &&
          u.password === password
      );

      if (!user) {
        setError("Invalid username or password.");
        return;
      }

      loginFromMock(user);

      if (user.role === "admin" || user.role === "manager") {
        navigate("/dashboard");
      } else if (user.role === "department_viewer" && user.departmentId) {
        navigate(`/department/${user.departmentId}`);
      } else {
        navigate("/dashboard");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900 dark:bg-slate-900 dark:text-slate-50 relative overflow-hidden">
      {/* Theme toggle */}
      <button
        onClick={toggleTheme}
        className="absolute right-4 top-4 z-30 text-xs px-3 py-1.5 rounded-full border border-slate-600 bg-slate-900/80 text-slate-50 hover:bg-slate-800 hover:border-slate-400 transition
                   dark:border-slate-300 dark:bg-white/80 dark:text-slate-700 dark:hover:bg-slate-100"
      >
        {theme === "dark" ? "Light mode ☀️" : "Dark mode 🌙"}
      </button>

      {/* LEFT: big logo panel */}
      <div
        className={`relative z-20 hidden md:flex md:w-2/5 lg:w-3/5 items-center justify-center overflow-hidden
        bg-gradient-to-b from-slate-200 via-slate-100 to-white
        dark:from-slate-900 dark:via-slate-950 dark:to-black
        transition-transform duration-[1500ms] ease-out
        ${logoSlideIn ? "translate-x-0" : "translate-x-full"}`}
      >
        {/* glow background*/}
        <div
          className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_top,_rgba(248,113,113,0.6)_0,_transparent_55%),_radial-gradient(circle_at_bottom,_rgba(56,189,248,0.55)_0,_transparent_55%)]
                     dark:opacity-60 dark:bg-[radial-gradient(circle_at_top,_#f97373_0,_transparent_55%),_radial-gradient(circle_at_bottom,_#38bdf8_0,_transparent_55%)]"
        />

        {/* content */}
        <div className="relative z-10 flex flex-col items-center text-center px-8 max-w-lg">
          <div
            className="
              w-60 h-60 lg:w-80 lg:h-80 rounded-full border-4 flex items-center justify-center mb-10 overflow-hidden
              border-red-600 bg-white shadow-[0_0_40px_rgba(248,113,113,0.45)]
              dark:border-red-700 dark:shadow-[0_0_80px_rgba(248,113,113,0.85)]
            "
          >
            <img
              src={thyLogo}
              alt="Turkish Airlines logo"
              className="w-full h-full object-cover scale-110"
            />
          </div>

          <h1 className="text-2xl lg:text-3xl font-semibold mb-2">
            FlightSense
          </h1>
          <p className="text-s lg:text-sm text-slate-600 dark:text-slate-200 mb-6 leading-relaxed">
            Feedback Analyzer for Turkish Airlines
          </p>
        </div>
      </div>

      {/* RIGHT: login form panel */}
      <div className="flex-1 flex items-center justify-center px-10 py-10 md:px-16 lg:px-24 bg-slate-50 dark:bg-slate-950">
        <div className="w-full max-w-md lg:max-w-lg">
          <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500 mb-2">
            Welcome back
          </p>
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50 mb-1">
            Sign in to FlightSense
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-8">
            Please sign in to continue.
          </p>

          <form className="space-y-4" onSubmit={handleSubmit}>
            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-slate-800 dark:text-slate-200 mb-1">
                Username
              </label>
              <input
                type="text"
                autoComplete="username"
                className="
                  w-full rounded-md px-4 py-3 text-base outline-none
                  bg-white border border-slate-300 text-slate-900 placeholder-slate-400
                  focus:ring-2 focus:ring-red-500 focus:border-red-500
                  dark:bg-slate-900 dark:border-slate-700 dark:text-slate-50 dark:placeholder-slate-500
                "
                placeholder="e.g. admin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-slate-800 dark:text-slate-200 mb-1">
                Password
              </label>
              <input
                type="password"
                autoComplete="current-password"
                className="
                  w-full rounded-md px-4 py-3 text-base outline-none
                  bg-white border border-slate-300 text-slate-900 placeholder-slate-400
                  focus:ring-2 focus:ring-red-500 focus:border-red-500
                  dark:bg-slate-900 dark:border-slate-700 dark:text-slate-50 dark:placeholder-slate-500
                "
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            {/* Error */}
            {error && (
              <div
                className="rounded-md bg-rose-100 border border-rose-300 px-3 py-2 text-xs text-rose-700
                           dark:bg-rose-950/40 dark:border-rose-700/50 dark:text-rose-200"
                aria-live="polite"
              >
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full mt-2 inline-flex items-center justify-center gap-2 bg-red-500 text-white py-2.5 rounded-md text-sm font-medium hover:bg-red-400 disabled:opacity-70 disabled:cursor-not-allowed transition"
            >
              {isSubmitting ? (
                <>
                  <span className="h-3 w-3 rounded-full border-2 border-t-transparent border-white animate-spin" />
                  Signing in…
                </>
              ) : (
                "Sign in"
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
