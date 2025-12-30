import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../hooks/useTheme";
import {
  JIRA_KEY_TO_DEPARTMENT_LABEL,
  DEPARTMENT_LABEL_TO_CODE,
  getJiraProjectUrl,
  type DepartmentId,
  type DepartmentLabel,
} from "../departmentConfig";
import {
  PAGE_WRAPPER,
  PAGE_BACKGROUND_OVERLAY,
  TOPBAR,
  CARD,
  KPI_TITLE,
} from "../styles/dashboardTokens";

import FeedbackTrendChart from "../components/charts/FeedbackTrendChart";
import DistributionPie, {
  type PieItem,
} from "../components/charts/DistributionPie";

import { fetchDepartmentStatistics, type Period } from "../services/api";
import {
  mapDepartmentStatsApiToUi,
  type DepartmentStatsUi,
} from "../utils/departmentStatsMapper";
import { MOCK_DEPARTMENT_STATS_BY_RANGE } from "../mock/mockDepartmentStats";
import { useDepartmentHighPriority } from "../hooks/useHighPriorityReviews";
import HighPriorityFeed from "../components/HighPriorityFeed";

const THY_RED = "#b7312c";

export default function DepartmentDashboard() {
  const { departmentName } = useParams<{ departmentName: string }>();
  const { user, logout, token } = useAuth() as any;
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  
  const [timeRange, setTimeRange] = useState<Period>("monthly");
  const [stats, setStats] = useState<DepartmentStatsUi | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jiraKey, setJiraKey] = useState<string | null>(null);


  if (!departmentName) {
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

  const label = decodeURIComponent(departmentName);
  const deptCode = DEPARTMENT_LABEL_TO_CODE[label as DepartmentLabel] ?? label;
  
  const {items: highPriorityItems, loading: highPriorityLoading, error: highPriorityError} = useDepartmentHighPriority(deptCode, 5);

  useEffect(() => {
    if (!departmentName) return;
    setJiraKey(deptCode);


    setLoading(true);
    setError(null);

    if (!token) {
      setLoading(true);
      setError(null);
      setTimeout(() => {
        const mockStats = MOCK_DEPARTMENT_STATS_BY_RANGE[deptCode as DepartmentId]?.[timeRange];

        if (mockStats) {
          const uiStats = mapDepartmentStatsApiToUi(mockStats, timeRange);
          setStats(uiStats);
        } else {
          setError(`No mock data found for department: ${deptCode}`);
        }
        setLoading(false);
      }, 500);
      return;
    }

    // --- Real API call ---
    setLoading(true);
    setError(null);
    console.log("key:", deptCode, "label: ", label);
    fetchDepartmentStatistics(token, {
      department_name: deptCode, // Backend expects the department code (KHB, TGS, etc.)
      period: timeRange,
    })
      .then((res) => {
        if (!res.success) {
          throw new Error("API returned success = false");
        }
        const ui = mapDepartmentStatsApiToUi(res.data, timeRange);
        setStats(ui);
      })
      .catch((err) => {
        console.error(err);
        setError(err.message || "Failed to load department data");
      })
      .finally(() => setLoading(false));
  }, [token, departmentName, timeRange]);

  function handleLogout() {
    logout();
    navigate("/");
  }

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className={`${CARD} px-6 py-4 max-w-md`}>
          <p className="text-sm text-slate-900 dark:text-slate-50">
            Loading department dashboard...
          </p>
          {error && (
            <p className="mt-2 text-xs text-red-500">
              {error}
            </p>
          )}
        </div>
      </div>
    );
  }

  if (error && !stats) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className={`${CARD} px-6 py-4 max-w-md`}>
          <p className="text-sm text-red-500 mb-2">Error</p>
          <p className="text-xs text-slate-900 dark:text-slate-50 mb-3">
            {error}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="text-xs px-3 py-1.5 rounded-full border border-slate-300 text-slate-700 bg-white hover:bg-slate-100 transition
                       dark:border-slate-600 dark:text-slate-50 dark:bg-slate-900/70 dark:hover:bg-slate-800"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }
  
  if (!stats) {
    return (
       <div className="h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className={`${CARD} px-6 py-4 max-w-md`}>
          <p className="text-sm text-slate-900 dark:text-slate-50">
            No statistics available for this department.
          </p>
        </div>
      </div>
    )
  }


  const {
    departmentName: deptDisplayName,
    periodLabel,
    totalReviews,
    sentimentCounts,
    sentimentPercentages,
    priorityCounts,
    priorityPercentages,
    labelDistribution,
    historicalData,
  } = stats;

  const labelPieData: PieItem[] = labelDistribution.map((label) => ({
    id: label.key,
    name: label.name,
    value: label.totalReviews,
  }));

 function periodButtonClass(current: Period, target: Period) {
    const base = "px-3 py-1 rounded-full border transition text-[11px]";
    const active =
      "border-slate-900 bg-white text-slate-900 dark:border-slate-300 dark:bg-slate-900 dark:text-slate-50";
    const inactive =
      "border-slate-200 bg-white/70 text-slate-500 hover:bg-white " +
      "dark:border-slate-700 dark:bg-slate-900/40 dark:text-slate-300 dark:hover:bg-slate-900/70";

    return base + " " + (current === target ? active : inactive);
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
              <span style={{ color: THY_RED }}>{deptDisplayName}</span>
            </h1>
          </div>

          <div className="flex items-center gap-3">
            {(user?.role === "manager" || user?.role === "admin") && (
              <button
                onClick={() => navigate("/dashboard")}
                className="text-xs px-3 py-1.5 rounded-full border border-slate-300 text-slate-700 bg-white hover:bg-slate-100 hover:border-slate-400 transition flex items-center gap-1.5
                           dark:border-slate-600 dark:text-slate-50 dark:bg-slate-900/70 dark:hover:bg-slate-800"
              >
                ← Back to Dashboard
              </button>
            )}

            {jiraKey && (
              <a
                href={getJiraProjectUrl(jiraKey)}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs px-3 py-1.5 rounded-full border border-blue-500 text-blue-600 bg-white hover:bg-blue-50 hover:border-blue-600 transition flex items-center gap-1.5
                           dark:border-blue-400 dark:text-blue-300 dark:bg-slate-900/70 dark:hover:bg-blue-900/30"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11.53 2c-.94 0-1.7.76-1.7 1.7v1.37c-.88.21-1.69.59-2.4 1.1L6.12 4.86a1.7 1.7 0 00-2.4 0 1.7 1.7 0 000 2.4l1.31 1.31c-.51.71-.89 1.52-1.1 2.4H2.56c-.94 0-1.7.76-1.7 1.7s.76 1.7 1.7 1.7h1.37c.21.88.59 1.69 1.1 2.4l-1.31 1.31a1.7 1.7 0 000 2.4 1.7 1.7 0 002.4 0l1.31-1.31c.71.51 1.52.89 2.4 1.1v1.37c0 .94.76 1.7 1.7 1.7s1.7-.76 1.7-1.7v-1.37c.88-.21 1.69-.59 2.4-1.1l1.31 1.31a1.7 1.7 0 002.4 0 1.7 1.7 0 000-2.4l-1.31-1.31c.51-.71.89-1.52 1.1-2.4h1.37c.94 0 1.7-.76 1.7-1.7s-.76-1.7-1.7-1.7h-1.37c-.21-.88-.59-1.69-1.1-2.4l1.31-1.31a1.7 1.7 0 000-2.4 1.7 1.7 0 00-2.4 0l-1.31 1.31c-.71-.51-1.52-.89-2.4-1.1V3.7c0-.94-.76-1.7-1.7-1.7zm0 7.5a2.5 2.5 0 110 5 2.5 2.5 0 010-5z"/>
                </svg>
                Open Jira Board
              </a>
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
                  Feedback trend for {deptDisplayName}
                </p>
                <p className="text-[11px] text-slate-500 dark:text-slate-300">
                  Positive vs negative reviews over time · {periodLabel}
                </p>
              </div>
              <div className="flex gap-2 text-[11px]">
                <button
                  onClick={() => setTimeRange("weekly")}
                  className={periodButtonClass(timeRange, "weekly")}
                >
                  Last Week
                </button>
                <button
                  onClick={() => setTimeRange("monthly")}
                  className={periodButtonClass(timeRange, "monthly")}

                >
                  Last Month
                </button>
                <button
                  onClick={() => setTimeRange("yearly")}
                  className={periodButtonClass(timeRange, "yearly")}
                >
                  Last Year
                </button>
              </div>
            </div>
            <div className={`${CARD} p-4`}>
              <FeedbackTrendChart data={historicalData} mode={theme} />
            </div>
          </section>

          {/* KPI cards */}
          <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Total reviews</p>
              <p className="mt-2 text-3xl font-semibold">
                {totalReviews.toLocaleString("en-US")}
              </p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-300">
                For this department ({periodLabel})
              </p>
            </div>

            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Sentiment</p>
              <div className="mt-3 flex items-end justify-between">
                <div>
                  <p className="text-sm text-emerald-600 dark:text-emerald-400"> Positive
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-300 font-semibold">
                    {sentimentCounts.positive} ({sentimentPercentages.positive}%)
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-slate-600 dark:text-slate-200"> Neutral
                  </p>
                  <p className="text-[11px] text-slate-500 dark:text-slate-300 font-semibold">
                    {sentimentCounts.neutral} ({sentimentPercentages.neutral}%)
                  </p>
                </div>
                <div>
                  <p className="text-sm" style={{ color: THY_RED }}> Negative
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-300 font-semibold">
                    {sentimentCounts.negative} ({sentimentPercentages.negative}%)
                  </p>
                </div>
              </div>
              <div className="mt-3 h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden flex">
                <div
                  className="h-full bg-emerald-500"
                  style={{ width: `${sentimentPercentages.positive}%` }}
                />
                <div
                  className="h-full bg-slate-500 dark:bg-slate-300"
                  style={{ width: `${sentimentPercentages.neutral}%` }}
                />
                <div
                  className="h-full"
                  style={{
                    width: `${sentimentPercentages.negative}%`,
                    backgroundColor: THY_RED,
                  }}
                />
              </div>
            </div>

            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Priority mix</p>
              <div className="mt-3 flex justify-between text-xs text-slate-700 dark:text-slate-200">
                <div>
                  <p className="text-sm"style={{ color: THY_RED }}>High</p>
                  <p className="font-semibold">{priorityCounts.high} ({priorityPercentages.high}%)</p>
                </div>
                <div>
                  <p className="text-sm text-amber-400">Medium</p>
                  <p className="font-semibold">{priorityCounts.medium} ({priorityPercentages.medium}%)</p>
                </div>
                <div>
                  <p className="text-sm text-sky-400">Low</p>
                  <p className="font-semibold">{priorityCounts.low} ({priorityPercentages.low}%)</p>
                </div>
              </div>
              <div className="mt-3 h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden flex">
                <div
                  className="h-full"
                  style={{
                    width: `${priorityPercentages.high}%`,
                    backgroundColor: THY_RED,
                  }}
                />
                <div
                  className="h-full bg-amber-400"
                  style={{
                    width: `${priorityPercentages.medium}%`,
                  }}
                />
                <div
                  className="h-full bg-sky-400"
                  style={{
                    width: `${priorityPercentages.low}%`,
                  }}
                />
              </div>
            </div>
          </section>

          {/* Pie + label sentiment percentages */}
          <section>
            <div className={`${CARD} p-4`}>
              <DistributionPie
                title="Reviews by subcategories"
                subtitle="Distribution of feedback across labels handled by this department"
                data={labelPieData}
                mode={theme}
                rightContent={
                  <div className="space-y-3 text-xs">
                    {labelDistribution.map((label) => (
                      <div key={label.key}>
                        <p className="font-semibold text-slate-900 dark:text-slate-50">
                          {label.name}
                        </p>
                        <p className="text-[11px] flex flex-wrap gap-x-2">
                          <span className="text-emerald-500 dark:text-emerald-400 font-semibold">
                            {label.sentimentPercentages.positive}% positive
                          </span>
                          <span className="text-slate-500 dark:text-slate-300 font-semibold">
                            {label.sentimentPercentages.neutral}% neutral
                          </span>
                          <span className="mx-1 text-slate-500">·</span>
                          <span
                            className="font-semibold"
                            style={{ color: THY_RED }}
                          >
                            {label.sentimentPercentages.negative}% negative
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
               High Priority Feedback
            </p>
            <p className="text-[11px] text-slate-500 dark:text-slate-300 mb-3">
              Most recent high-priority reviews for this department.
            </p>

            {highPriorityLoading && (
              <p className="text-xs text-slate-500">Loading high priority feedback…</p>
            )}
            {highPriorityError && (
              <p className="text-xs text-red-500">
                Failed to load high priority feedback
              </p>
            )}
            {!highPriorityLoading && highPriorityItems.length === 0 && (
              <p className="text-xs text-emerald-600">
                No urgent issues detected 
              </p>
            )}
            {!highPriorityLoading && !highPriorityError && (
              <HighPriorityFeed items={highPriorityItems} />
            )}
          </section>
        </main>
      </div>
    </div>
  );
}
