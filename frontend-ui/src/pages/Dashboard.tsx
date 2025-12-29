import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { fetchManagerStatistics, type Period } from "../services/api";
import {mapManagerStatsApiToUi, type ManagerStatsUi} from "../utils/managerStatsMapper";
import {MOCK_MANAGER_STATS_BY_RANGE} from "../mock/mockManagerStats";
import FeedbackTrendChart from "../components/charts/FeedbackTrendChart";
import DistributionPie, {type PieItem} from "../components/charts/DistributionPie";
import { useTheme } from "../hooks/useTheme";
import {PAGE_WRAPPER, PAGE_BACKGROUND_OVERLAY, TOPBAR, CARD, KPI_TITLE} from "../styles/dashboardTokens";
import { useManagerHighPriority } from "../hooks/useHighPriorityReviews";
import HighPriorityFeed from "../components/HighPriorityFeed";


const THY_RED = "#b7312c";

export default function Dashboard() {
  const { user, logout, token } = useAuth() as any;
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  const [timeRange, setTimeRange] = useState<Period>("monthly");
  const [stats, setStats] = useState<ManagerStatsUi | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {data: highPriorityByDept, loading: highPriorityLoading, error: highPriorityError} = useManagerHighPriority(2);


  useEffect(() => {
    if (!user) return;

    if (!token) {
      const apiMock = MOCK_MANAGER_STATS_BY_RANGE[timeRange];
      const uiStats = mapManagerStatsApiToUi(apiMock, timeRange);
      setStats(uiStats);
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
        
        const apiMock = MOCK_MANAGER_STATS_BY_RANGE[timeRange];
        const uiStats = mapManagerStatsApiToUi(apiMock, timeRange);
        setStats(uiStats);
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


  const{periodLabel, totalReviews, uniqueReviews, processedSegments, sentimentCounts, sentimentPercentages, priorityCounts, priorityPercentages, departments, historicalData} = stats;

  const departmentPieData: PieItem[] = departments.map((dep) => ({
    id: dep.id,
    name: dep.name,
    value: dep.totalReviews,
  }));


  function handleLogout() {
    logout();
    navigate("/");
  }

  function handleDepartmentSliceClick(item: PieItem) {
    if (item.id) {
      navigate(`/department/${item.id}`);
    }
  }

  function periodButtonClass(current: Period, target: Period) {
    const base =
      "px-3 py-1 rounded-full border transition text-[11px]";
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
            <h1 className="text-lg font-semibold">
              <span style={{ color: THY_RED }}>Manager Dashboard</span>
            </h1>
            <p className="text-[11px] text-slate-500 dark:text-slate-300">
              Period · {periodLabel}
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
            {user?.role === "admin" && (
              <button
                onClick={() => navigate("/admin/create-user")}
                className="
                  text-xs px-4 py-1.5 rounded-full
                  border border-red-300 text-red-600 bg-white
                  hover:bg-red-50 hover:border-red-400
                  transition
                  dark:border-red-600 dark:text-red-400 dark:bg-slate-900/70
                  dark:hover:bg-red-900/20
                "
              >
                👤➕ Create User
              </button>
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
              className="text-xs px-4 py-1.5 rounded-full border border-slate-300 text-slate-700 bg-white hover:bg-slate-100 hover:border-slate-400 transition
                         dark:border-slate-600 dark:text-slate-50 dark:bg-slate-900/70 dark:hover:bg-slate-800"
            >
              Log out
            </button>
          </div>
        </header>


        <main className="px-6 md:px-8 py-6 max-w-6xl mx-auto w-full space-y-6">
          {/* Trend card */}
          <section className="space-y-3">
            <div className="flex flex-wrap gap-3 items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-50">
                  Overall feedback trend
                </p>
                <p className="text-[11px] text-slate-500 dark:text-slate-300">
                  Positive / neutral / negative reviews over time · {periodLabel}
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
          <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
          
            {/* Unique Reviews */}
            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Unique reviews</p>
              <p className="mt-3 text-3xl font-semibold">
                {uniqueReviews.toLocaleString("en-US")}
              </p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-300">
                Total customer reviews ({periodLabel})
              </p>
            </div>

            {/* Processed Segments */}
            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Processed segments</p>
              <p className="mt-3 text-3xl font-semibold">
                {totalReviews.toLocaleString("en-US")}  {/*{processedSegments.toLocaleString("en-US")}*/}
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

            {/* Priority mix */}
            <div className={`${CARD} p-4`}>
              <p className={KPI_TITLE}>Priority mix</p>
              <div className="mt-3 flex justify-between text-xs text-slate-700 dark:text-slate-200">
                <div>
                  <p className="text-sm" style={{ color: THY_RED }}> High</p>
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
                    {departments.map((dep) => (
                      <div key={dep.id}>
                        <p className="font-semibold text-slate-900 dark:text-slate-50">
                          {dep.name} ({dep.totalReviews.toLocaleString("en-US")} reviews)
                        </p>
                        <p className="text-[11px] flex flex-wrap gap-x-3">
                          <span className="text-emerald-500 dark:text-emerald-400 font-semibold">
                            {dep.sentimentPercentages.positive}% positive
                          </span>
                          <span className="text-slate-500 dark:text-slate-300 font-semibold">
                             {dep.sentimentPercentages.neutral}% neutral
                          </span>
                          <span className="text-slate-500"></span>
                          <span className="font-semibold" style={{ color: THY_RED }}>
                             {dep.sentimentPercentages.negative}% negative
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
              High-priority review samples across departments
            </p>
            <p className="text-[11px] text-slate-500 dark:text-slate-300 mb-3">
              Most recent high-priority feedback from each department
            </p>

            {highPriorityLoading && (
              <p className="text-xs text-slate-500">
                Loading high-priority feedback…
              </p>
            )}

            {highPriorityError && (
              <p className="text-xs text-red-500">
                Failed to load high-priority feedback
              </p>
            )}

            {!highPriorityLoading && !highPriorityError && (
              <div className="space-y-6">
                {Object.entries(highPriorityByDept).filter(([, items]) => items.length > 0).map(([dept, items]) => (
                  <div key={dept}>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                      {dept}
                    </p>
                    <HighPriorityFeed items={items} />
                  </div>
                ))}
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}
