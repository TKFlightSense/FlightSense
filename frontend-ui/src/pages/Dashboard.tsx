import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { fetchManagerStatistics, type Period } from "../services/api";
import {
  mapManagerStatsApiToUi,
  type ManagerStatsUi,
} from "../utils/managerStatsMapper";
import {
  MOCK_MANAGER_STATS_BY_RANGE,
  type TimeRangeKey,
} from "../mock/mockManagerStats";
import FeedbackTrendChart from "../components/charts/FeedbackTrendChart";
import DistributionPie, {
  type PieItem,
} from "../components/charts/DistributionPie";
import { useTheme } from "../hooks/useTheme";

import {
  PAGE_WRAPPER,
  PAGE_BACKGROUND_OVERLAY,
  TOPBAR,
  CARD,
  KPI_TITLE,
} from "../styles/dashboardTokens";

const THY_RED = "#b7312c";

export default function Dashboard() {
  const { user, logout, token } = useAuth() as any;
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  const [timeRange, setTimeRange] = useState<Period>("monthly");
  const [stats, setStats] = useState<ManagerStatsUi | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;

    // If you don’t have a backend token (mock login), just use mock data
    if (!token) {
      const mockKey = timeRange as TimeRangeKey;
      setStats(MOCK_MANAGER_STATS_BY_RANGE[mockKey]);
      setError("Using mock data (no API token available).");
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchManagerStatistics(token, timeRange)
      .then((res) => {
        if (cancelled) return;

        if (!res.success) {
          throw new Error("API returned success = false");
        }

        const uiStats = mapManagerStatsApiToUi(res.data, timeRange);
        setStats(uiStats);
      })
      .catch((err) => {
        if (cancelled) return;
        console.error(err);

        // Fallback to mock data if API fails
        const mockKey = timeRange as TimeRangeKey;
        setStats(MOCK_MANAGER_STATS_BY_RANGE[mockKey]);
        setError(
          err?.message
            ? `API failed, showing mock data. (${err.message})`
            : "API failed, showing mock data."
        );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [user, token, timeRange]);

  if (!user) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-950 text-slate-50">
        <div className={`${CARD} px-6 py-5 max-w-md`}>
          <p className="text-sm">
            No user info found. Go back to{" "}
            <a href="/" className="text-red-400 underline underline-offset-2">
              login
            </a>
            .
          </p>
        </div>
      </div>
    );
  }

  // While we don’t have any stats yet
  if (!stats) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-950 text-slate-50">
        <div className={`${CARD} px-6 py-4`}>
          <p className="text-sm">
            {loading ? "Loading manager dashboard..." : "No data yet."}
          </p>
          {error && (
            <p className="mt-2 text-xs text-red-300">
              {error}
            </p>
          )}
        </div>
      </div>
    );
  }

  const totalPriority =
    stats.highPriority + stats.mediumPriority + stats.lowPriority || 1;

  const positivePercent = Math.round(
    (stats.positive / Math.max(stats.totalReviews, 1)) * 100
  );
  const negativePercent = 100 - positivePercent;

  const departmentPieData: PieItem[] = stats.departments.map((dep) => ({
    id: dep.id,
    name: dep.name,
    value: dep.totalReviews,
  }));

  const departmentPercentages = stats.departments.map((dep) => {
    const total = Math.max(dep.positive + dep.negative, 1);
    const pos = Math.round((dep.positive / total) * 100);
    const neg = 100 - pos;
    return {
      id: dep.id,
      name: dep.name,
      positivePercent: pos,
      negativePercent: neg,
    };
  });

  function handleLogout() {
    logout();
    navigate("/");
  }

  function handleDepartmentSliceClick(item: PieItem) {
    if (item.id) {
      navigate(`/department/${item.id}`);
    }
  }

  return (
    <div className={PAGE_WRAPPER}>
      <div className={PAGE_BACKGROUND_OVERLAY} />

      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Top bar */}
        <header className={TOPBAR}>
          <div>
            <p className="text-xs font-semibold tracking-[0.25em] text-slate-400 uppercase">
              FlightSense
            </p>
            <h1 className="text-lg font-semibold">
              <span style={{ color: THY_RED }}>Manager Dashboard</span>
            </h1>
            <p className="text-[11px] text-slate-500 dark:text-slate-300">
              Period · {stats.periodLabel}
            </p>
            {error && (
              <p className="mt-1 text-[11px] text-amber-500 dark:text-amber-300">
                {error}
              </p>
            )}
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm text-slate-900 dark:text-slate-50">
                {user.username}{" "}
                <span className="text-xs text-slate-500 dark:text-slate-300">
                  ({user.role})
                </span>
              </p>
              {user.departmentId && (
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Dept: {user.departmentId}
                </p>
              )}
            </div>
            <button
              onClick={toggleTheme}
              className="text-xs px-3 py-1.5 rounded-full border border-slate-300 bg-white/80 text-slate-700 hover:bg-slate-100 hover:border-slate-400 transition
                         dark:border-slate-600 dark:bg-slate-900/70 dark:text-slate-50 dark:hover:bg-slate-800"
            >
              {theme === "dark" ? "Light mode ☀️" : "Dark mode 🌙"}
            </button>

            <button
              onClick={handleLogout}
              className="text-xs px-4 py-1.5 rounded-full border border-slate-300 text-slate-700 bg-white hover:bg-slate-100 hover:border-slate-400 transition
                         dark:border-slate-600 dark:text-slate-50 dark:bg-slate-900/70 dark:hover:bg-slate-800"
            >
              Log out
            </button>
          </div>
        </header>

        {/* Main content – your original JSX unchanged */}
        <main className="px-6 md:px-8 py-6 max-w-6xl mx-auto w-full space-y-6">
          {/* Trend card */}
          <section className="space-y-3">
            <div className="flex flex-wrap gap-3 items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-50">
                  Overall feedback trend
                </p>
                <p className="text-[11px] text-slate-500 dark:text-slate-300">
                  Positive vs negative reviews over time · {stats.periodLabel}
                </p>
              </div>
              <div className="flex gap-2 text-[11px]">
                <button
                  onClick={() => setTimeRange("weekly")}
                  className={
                    "px-3 py-1 rounded-full border transition " +
                    (timeRange === "weekly"
                      ? "border-slate-900 bg-white text-slate-900 dark:border-slate-300 dark:bg-slate-900 dark:text-slate-50"
                      : "border-slate-200 bg-white/70 text-slate-500 hover:bg-white dark:border-slate-700 dark:bg-slate-900/40 dark:text-slate-300 dark:hover:bg-slate-900/70")
                  }
                >
                  Weekly
                </button>
                <button
                  onClick={() => setTimeRange("monthly")}
                  className={
                    "px-3 py-1 rounded-full border transition " +
                    (timeRange === "monthly"
                      ? "border-slate-900 bg-white text-slate-900 dark:border-slate-300 dark:bg-slate-900 dark:text-slate-50"
                      : "border-slate-200 bg-white/70 text-slate-500 hover:bg-white dark:border-slate-700 dark:bg-slate-900/40 dark:text-slate-300 dark:hover:bg-slate-900/70")
                  }
                >
                  Monthly
                </button>
                <button
                  onClick={() => setTimeRange("yearly")}
                  className={
                    "px-3 py-1 rounded-full border transition " +
                    (timeRange === "yearly"
                      ? "border-slate-900 bg-white text-slate-900 dark:border-slate-300 dark:bg-slate-900 dark:text-slate-50"
                      : "border-slate-200 bg-white/70 text-slate-500 hover:bg-white dark:border-slate-700 dark:bg-slate-900/40 dark:text-slate-300 dark:hover:bg-slate-900/70")
                  }
                >
                  Yearly
                </button>
              </div>
            </div>

            <div className={`${CARD} p-4`}>
              <FeedbackTrendChart data={stats.trend} mode={theme} />
            </div>
          </section>

          {/* KPI cards */}
          <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Unique Reviews */}
            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Unique reviews</p>
              <p className="mt-3 text-3xl font-semibold">
                {stats.uniqueReviews.toLocaleString("en-US")}
              </p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-300">
                Total customer reviews ({stats.periodLabel})
              </p>
            </div>

            {/* Processed Segments */}
            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Processed segments</p>
              <p className="mt-3 text-3xl font-semibold">
                {stats.processedSegments.toLocaleString("en-US")}
              </p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-300">
                Classified feedback segments
              </p>
            </div>

            {/* Sentiment split */}
            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Sentiment split</p>
              <div className="mt-3 flex items-end justify-between">
                <div>
                  <p className="text-sm text-emerald-600 dark:text-emerald-400 font-semibold">
                    {positivePercent}% positive
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-300">
                    {stats.positive} segments
                  </p>
                </div>
                <div>
                  <p
                    className="text-sm font-semibold"
                    style={{ color: THY_RED }}
                  >
                    {negativePercent}% negative
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-300">
                    {stats.negative} segments
                  </p>
                </div>
              </div>

              <div className="mt-3 h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden flex">
                <div
                  className="h-full bg-emerald-500"
                  style={{ width: `${positivePercent}%` }}
                />
                <div
                  className="h-full"
                  style={{
                    width: `${negativePercent}%`,
                    backgroundColor: THY_RED,
                  }}
                />
              </div>
            </div>

            {/* Priority mix */}
            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Priority mix</p>
              <div className="mt-3 flex justify-between text-xs text-slate-700 dark:text-slate-200">
                <div>
                  <p className="text-[11px] text-slate-500">High</p>
                  <p className="font-semibold">{stats.highPriority}</p>
                </div>
                <div>
                  <p className="text-[11px] text-slate-500">Medium</p>
                  <p className="font-semibold">{stats.mediumPriority}</p>
                </div>
                <div>
                  <p className="text-[11px] text-slate-500">Low</p>
                  <p className="font-semibold">{stats.lowPriority}</p>
                </div>
              </div>
              <div className="mt-3 h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden flex">
                <div
                  className="h-full"
                  style={{
                    width: `${(stats.highPriority / totalPriority) * 100}%`,
                    backgroundColor: THY_RED,
                  }}
                />
                <div
                  className="h-full bg-amber-400"
                  style={{
                    width: `${(stats.mediumPriority / totalPriority) * 100}%`,
                  }}
                />
                <div
                  className="h-full bg-sky-400"
                  style={{
                    width: `${(stats.lowPriority / totalPriority) * 100}%`,
                  }}
                />
              </div>
            </div>
          </section>

          {/* Pie + per-department sentiment percentages */}
          <section>
            <div className={`${CARD} p-4`}>
              <DistributionPie
                title="Reviews by department"
                subtitle="Click a department slice to view details"
                data={departmentPieData}
                onSliceClick={handleDepartmentSliceClick}
                mode={theme}
                rightContent={
                  <div className="space-y-3 text-xs">
                    {departmentPercentages.map((dep) => (
                      <div key={dep.id}>
                        <p className="font-semibold text-slate-900 dark:text-slate-50">
                          {dep.name}
                        </p>
                        <p className="text-[11px]">
                          <span className="text-emerald-500 dark:text-emerald-400 font-semibold">
                            {dep.positivePercent}% positive
                          </span>
                          <span className="mx-1 text-slate-500">·</span>
                          <span
                            className="font-semibold"
                            style={{ color: THY_RED }}
                          >
                            {dep.negativePercent}% negative
                          </span>
                        </p>
                      </div>
                    ))}
                  </div>
                }
              />
            </div>
          </section>

          {/* High-priority issues across departments */}
          <section className={`${CARD} p-4`}>
            <p className="text-sm font-semibold text-slate-900 dark:text-slate-50 mb-2">
              High-priority issues across departments
            </p>
            <p className="text-[11px] text-slate-500 dark:text-slate-300 mb-3">
              Selected issues with the highest priority or volume in the current
              period.
            </p>

            <ul className="space-y-2 text-xs">
              {stats.topIssues.map((issue) => {
                const total = Math.max(issue.positive + issue.negative, 1);
                const pos = Math.round((issue.positive / total) * 100);
                const neg = 100 - pos;

                return (
                  <li
                    key={issue.labelKey}
                    className="flex items-center justify-between"
                  >
                    <div>
                      <p className="text-slate-900 dark:text-slate-50 font-medium">
                        {issue.labelDisplay}
                      </p>
                      <p className="font-mono text-[11px] text-slate-500 dark:text-slate-400">
                        {issue.labelKey}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-slate-900 dark:text-slate-50">
                        {issue.count} reviews
                      </p>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">
                        <span className="text-emerald-500 dark:text-emerald-400 font-semibold">
                          {pos}% +
                        </span>{" "}
                        /{" "}
                        <span
                          className="font-semibold"
                          style={{ color: THY_RED }}
                        >
                          {neg}% −
                        </span>
                      </p>
                      <p
                        className={
                          "text-[11px] " +
                          (issue.trend === "up"
                            ? "text-rose-600 dark:text-rose-400"
                            : issue.trend === "down"
                            ? "text-emerald-600 dark:text-emerald-400"
                            : "text-slate-500 dark:text-slate-400")
                        }
                      >
                        {issue.trend === "up"
                          ? "↑ increasing"
                          : issue.trend === "down"
                          ? "↓ decreasing"
                          : "→ stable"}
                      </p>
                    </div>
                  </li>
                );
              })}
            </ul>
          </section>
        </main>
      </div>
    </div>
  );
}
