import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { departments, type DepartmentId } from "../departmentConfig";
import {
  MOCK_DEPARTMENT_STATS_BY_RANGE,
  type TimeRangeKey,
} from "../mock/mockDepartmentStats";
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

export default function DepartmentDashboard() {
  const { departmentId } = useParams<{ departmentId: string }>();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  const [timeRange, setTimeRange] = useState<TimeRangeKey>("monthly");

  if (!departmentId) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className={`${CARD} px-6 py-4 max-w-md`}>
          <p className="text-slate-900 dark:text-slate-50 text-sm mb-2">
            No department specified in URL.
          </p>
          <Link
            to="/"
            className="text-xs text-blue-600 dark:text-blue-300 underline"
          >
            Back to login
          </Link>
        </div>
      </div>
    );
  }

  const deptId = departmentId as DepartmentId;
  const department = departments.find((d) => d.id === deptId);

  if (!department) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className={`${CARD} px-6 py-4 max-w-md`}>
          <p className="text-sm text-slate-900 dark:text-slate-50 mb-1">
            Unknown department:
          </p>
          <p className="text-xs font-mono text-slate-600 dark:text-slate-300 mb-3">
            {departmentId}
          </p>
          <Link
            to="/"
            className="text-xs text-blue-600 dark:text-blue-300 underline"
          >
            Back to login
          </Link>
        </div>
      </div>
    );
  }

  const stats = MOCK_DEPARTMENT_STATS_BY_RANGE[deptId][timeRange];

  const positivePercent = Math.round(
    (stats.positive / Math.max(stats.totalReviews, 1)) * 100
  );
  const negativePercent = 100 - positivePercent;

  const totalPriority =
    stats.highPriority + stats.mediumPriority + stats.lowPriority || 1;

  const issuesPieData: PieItem[] = stats.topIssues.map((issue) => ({
    name: issue.labelDisplay,
    value: issue.count,
  }));

  const labelPercentages = stats.topIssues.map((issue) => {
    const total = Math.max(issue.positive + issue.negative, 1);
    const pos = Math.round((issue.positive / total) * 100);
    const neg = 100 - pos;
    return {
      labelKey: issue.labelKey,
      labelDisplay: issue.labelDisplay,
      positivePercent: pos,
      negativePercent: neg,
    };
  });

  function handleLogout() {
    logout();
    navigate("/");
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
            <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
              <span style={{ color: THY_RED }}>{department.name}</span>
            </h1>
            <p className="text-[11px] text-slate-500 dark:text-slate-300">
              Period · {stats.periodLabel}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {user && (
              <div className="text-right">
                <p className="text-sm text-slate-900 dark:text-slate-50">
                  {user.username}{" "}
                  <span className="text-xs text-slate-500 dark:text-slate-300">
                    ({user.role})
                  </span>
                </p>
                {user.departmentId && (
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Assigned dept: {user.departmentId}
                  </p>
                )}
              </div>
            )}

            <button
              onClick={toggleTheme}
              className="text-xs px-3 py-1.5 rounded-full border border-slate-300 bg-white/80 text-slate-700 hover:bg-slate-100 hover:border-slate-400 transition
                         dark:border-slate-600 dark:bg-slate-900/70 dark:text-slate-50 dark:hover:bg-slate-800"
            >
              {theme === "dark" ? "Light mode ☀️" : "Dark mode 🌙"}
            </button>

            <button
              onClick={handleLogout}
              className="text-xs px-3 py-1.5 rounded-full border border-slate-300 text-slate-700 bg-white hover:bg-slate-100 transition
                         dark:border-slate-600 dark:text-slate-50 dark:bg-slate-900/70 dark:hover:bg-slate-800"
            >
              Log out
            </button>
          </div>
        </header>

        {/* Main content */}
        <main className="px-6 md:px-8 py-6 max-w-6xl mx-auto w-full space-y-6">
          {/* Trend chart */}
          <section className="space-y-3">
            <div className="flex flex-wrap gap-3 items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-50">
                  Feedback trend for {department.name}
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
          <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Total reviews</p>
              <p className="mt-2 text-3xl font-semibold">
                {stats.totalReviews.toLocaleString("en-US")}
              </p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-300">
                For this department ({stats.periodLabel})
              </p>
            </div>

            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Sentiment</p>
              <div className="mt-3 flex items-end justify-between">
                <div>
                  <p className="text-sm text-emerald-600 dark:text-emerald-400 font-semibold">
                    {positivePercent}% positive
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-300">
                    {stats.positive} reviews
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
                    {stats.negative} reviews
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

          {/* Pie + label sentiment percentages */}
          <section>
            <div className={`${CARD} p-4`}>
              <DistributionPie
                title="Issues by label"
                subtitle="Distribution of feedback across labels handled by this department"
                data={issuesPieData}
                mode={theme}
                rightContent={
                  <div className="space-y-3 text-xs">
                    {labelPercentages.map((issue) => (
                      <div key={issue.labelKey}>
                        <p className="font-semibold text-slate-900 dark:text-slate-50">
                          {issue.labelDisplay}
                        </p>
                        <p className="text-[11px]">
                          <span className="text-emerald-500 dark:text-emerald-400 font-semibold">
                            {issue.positivePercent}% positive
                          </span>
                          <span className="mx-1 text-slate-500">·</span>
                          <span
                            className="font-semibold"
                            style={{ color: THY_RED }}
                          >
                            {issue.negativePercent}% negative
                          </span>
                        </p>
                      </div>
                    ))}
                  </div>
                }
              />
            </div>
          </section>

          {/* Bottom: top issues list */}
          <section className={`${CARD} p-4`}>
            <p className="text-sm font-semibold text-slate-900 dark:text-slate-50 mb-2">
              Top issues in this department
            </p>
            <p className="text-[11px] text-slate-500 dark:text-slate-300 mb-3">
              Selected high-priority issues and their sentiment split in the
              current period.
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
                      <p className="text-slate-900 dark:text-slate-50">
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

            <p className="mt-4 text-[11px] text-slate-500 dark:text-slate-400">
              Later this section can open filtered review lists or ticket views
              for this department.
            </p>
          </section>
        </main>
      </div>
    </div>
  );
}
