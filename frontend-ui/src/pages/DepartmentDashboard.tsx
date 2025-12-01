// src/pages/DepartmentDashboard.tsx
import { useParams, Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { departments, type DepartmentId } from "../departmentConfig";
import { MOCK_DEPARTMENT_STATS } from "../mock/mockDepartmentStats";
import FeedbackTrendChart from "../components/charts/FeedbackTrendChart";
import DistributionPie from "../components/charts/DistributionPie";

export default function DepartmentDashboard() {
  const { departmentId } = useParams<{ departmentId: string }>();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!departmentId) {
    return (
      <div className="h-screen flex items-center justify-center bg-rose-50">
        <div className="bg-white px-6 py-4 rounded-xl shadow">
          <p className="text-slate-800 text-sm mb-2">
            No department specified in URL.
          </p>
          <Link to="/" className="text-xs text-blue-600 underline">
            Back to login
          </Link>
        </div>
      </div>
    );
  }

  const deptId = departmentId as DepartmentId;
  const department = departments.find((d) => d.id === deptId);
  const stats = MOCK_DEPARTMENT_STATS[deptId];

  if (!department || !stats) {
    return (
      <div className="h-screen flex items-center justify-center bg-rose-50">
        <div className="bg-white px-6 py-4 rounded-xl shadow max-w-md">
          <p className="text-sm text-slate-800 mb-1">Unknown department:</p>
          <p className="text-xs font-mono text-slate-600 mb-3">
            {departmentId}
          </p>
          <Link to="/" className="text-xs text-blue-600 underline">
            Back to login
          </Link>
        </div>
      </div>
    );
  }

  const positivePercent = Math.round(
    (stats.positive / Math.max(stats.totalReviews, 1)) * 100
  );
  const negativePercent = 100 - positivePercent;

  const totalPriority =
    stats.highPriority + stats.mediumPriority + stats.lowPriority || 1;

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top bar */}
      <header className="flex items-center justify-between px-8 py-4 border-b bg-white">
        <div>
          <h1 className="text-lg font-semibold text-slate-900">
            {department.name}
          </h1>
          <p className="text-[11px] text-slate-500">
            Department dashboard · {stats.periodLabel}
          </p>
        </div>

        <div className="flex items-center gap-4">
          {user && (
            <div className="text-right">
              <p className="text-sm text-slate-700">
                {user.username}{" "}
                <span className="text-xs text-slate-500">({user.role})</span>
              </p>
              {user.departmentId && (
                <p className="text-[11px] text-slate-500">
                  Assigned dept: {user.departmentId}
                </p>
              )}
            </div>
          )}
          <button
            onClick={handleLogout}
            className="text-xs px-3 py-1.5 rounded-full border border-slate-300 text-slate-700 hover:bg-slate-100 transition"
          >
            Log out
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="px-8 py-6 max-w-6xl mx-auto space-y-6">
        {/* Trend chart */}
        <section className="space-y-3">
          <div>
            <p className="text-sm font-semibold text-slate-900">
              Feedback trend for this department
            </p>
            <p className="text-[11px] text-slate-500">
              Positive vs negative reviews over time ({stats.periodLabel})
            </p>
          </div>
          <FeedbackTrendChart data={stats.trend} />
        </section>

        {/* KPI cards */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Total reviews */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
              Total reviews
            </p>
            <p className="mt-2 text-3xl font-semibold text-slate-900">
              {stats.totalReviews.toLocaleString("en-US")}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              For this department ({stats.periodLabel})
            </p>
          </div>

          {/* Sentiment */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
              Sentiment
            </p>
            <div className="mt-3 flex items-end justify-between">
              <div>
                <p className="text-sm text-emerald-600 font-semibold">
                  {positivePercent}% positive
                </p>
                <p className="text-xs text-slate-500">
                  {stats.positive} reviews
                </p>
              </div>
              <div>
                <p className="text-sm text-rose-600 font-semibold">
                  {negativePercent}% negative
                </p>
                <p className="text-xs text-slate-500">
                  {stats.negative} reviews
                </p>
              </div>
            </div>
            <div className="mt-3 h-2 rounded-full bg-slate-100 overflow-hidden flex">
              <div
                className="h-full bg-emerald-500"
                style={{ width: `${positivePercent}%` }}
              />
              <div
                className="h-full bg-rose-500"
                style={{ width: `${negativePercent}%` }}
              />
            </div>
          </div>

          {/* Priority mix */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
              Priority mix
            </p>
            <div className="mt-3 flex justify-between text-xs">
              <div>
                <p className="text-[11px] text-slate-500">High</p>
                <p className="font-semibold text-slate-900">
                  {stats.highPriority}
                </p>
              </div>
              <div>
                <p className="text-[11px] text-slate-500">Medium</p>
                <p className="font-semibold text-slate-900">
                  {stats.mediumPriority}
                </p>
              </div>
              <div>
                <p className="text-[11px] text-slate-500">Low</p>
                <p className="font-semibold text-slate-900">
                  {stats.lowPriority}
                </p>
              </div>
            </div>
            <div className="mt-3 h-2 rounded-full bg-slate-100 overflow-hidden flex">
              <div
                className="h-full bg-rose-500"
                style={{
                  width: `${(stats.highPriority / totalPriority) * 100}%`,
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

        {/* Middle: pie + labels (with numeric panel) */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Pie chart: issues/labels for this department */}
          <div className="lg:col-span-2">
            <DistributionPie
              title="Issues by label"
              subtitle="Distribution of feedback across labels handled by this department"
              data={stats.topIssues.map((issue) => ({
                name: issue.labelDisplay,
                value: issue.count,
              }))}
              rightContent={
                <div className="space-y-3">
                  <div>
                    <p className="text-[11px] uppercase tracking-wide text-slate-400">
                      Total reviews
                    </p>
                    <p className="text-xl font-semibold text-slate-900">
                      {stats.totalReviews.toLocaleString("en-US")}
                    </p>
                  </div>

                  <div className="flex justify-between gap-4">
                    <div>
                      <p className="text-[11px] uppercase tracking-wide text-slate-400">
                        Positive
                      </p>
                      <p className="text-sm font-semibold text-emerald-600">
                        {stats.positive.toLocaleString("en-US")}
                      </p>
                    </div>
                    <div>
                      <p className="text-[11px] uppercase tracking-wide text-slate-400">
                        Negative
                      </p>
                      <p className="text-sm font-semibold text-rose-600">
                        {stats.negative.toLocaleString("en-US")}
                      </p>
                    </div>
                  </div>

                  <div>
                    <p className="text-[11px] uppercase tracking-wide text-slate-400 mb-1">
                      Priority
                    </p>
                    <p className="text-[11px] text-slate-600">
                      High:{" "}
                      <span className="font-semibold">
                        {stats.highPriority}
                      </span>
                    </p>
                    <p className="text-[11px] text-slate-600">
                      Medium:{" "}
                      <span className="font-semibold">
                        {stats.mediumPriority}
                      </span>
                    </p>
                    <p className="text-[11px] text-slate-600">
                      Low:{" "}
                      <span className="font-semibold">
                        {stats.lowPriority}
                      </span>
                    </p>
                  </div>
                </div>
              }
            />
          </div>

          {/* Labels routed to this department */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
            <p className="text-sm font-semibold text-slate-900 mb-2">
              Labels routed to this department
            </p>
            <p className="text-[11px] text-slate-500 mb-3">
              These are the fine-grained LLM labels that generate tickets for
              this team.
            </p>

            <ul className="flex flex-wrap gap-2">
              {department.labels.map((label) => (
                <li
                  key={label}
                  className="inline-flex items-center px-2 py-1 rounded-full border border-slate-200 bg-slate-50 text-[11px] font-mono text-slate-700"
                >
                  {label}
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* Bottom: top issues list */}
        <section className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
          <p className="text-sm font-semibold text-slate-900 mb-2">
            Top issues in this department
          </p>
          <p className="text-[11px] text-slate-500 mb-3">
            Based on number of reviews mapped to this department in the selected
            period.
          </p>

          <ul className="space-y-2 text-xs">
            {stats.topIssues.map((issue) => (
              <li
                key={issue.labelKey}
                className="flex items-center justify-between"
              >
                <div>
                  <p className="text-slate-800">{issue.labelDisplay}</p>
                  <p className="font-mono text-[11px] text-slate-500">
                    {issue.labelKey}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-slate-900">
                    {issue.count} reviews
                  </p>
                  <p
                    className={
                      "text-[11px] " +
                      (issue.trend === "up"
                        ? "text-rose-600"
                        : issue.trend === "down"
                        ? "text-emerald-600"
                        : "text-slate-500")
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
            ))}
          </ul>

          <p className="mt-4 text-[11px] text-slate-400">
            Later this section can open filtered review lists or ticket views
            for this department.
          </p>
        </section>
      </main>
    </div>
  );
}
