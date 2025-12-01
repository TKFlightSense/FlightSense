import {
  PieChart,
  Pie,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
} from "recharts";
import type { ReactNode } from "react";
import type { Theme } from "../../hooks/useTheme";

export type PieItem = {
  name: string;
  value: number;
  id?: string;
};

type Props = {
  title?: string;
  subtitle?: string;
  data: PieItem[];
  onSliceClick?: (item: PieItem) => void;
  rightContent?: ReactNode;
  mode?: Theme;
};

const COLORS_DARK = [
  "#38bdf8",
  "#22c55e",
  "#b7312c", // THY red
  "#f97316",
  "#a855f7",
  "#facc15",
];

const COLORS_LIGHT = [
  "#2563eb",
  "#0ea5e9",
  "#22c55e",
  "#b7312c", // THY red
  "#f97316",
  "#7c3aed",
];

export default function DistributionPie({
  title,
  subtitle,
  data,
  onSliceClick,
  rightContent,
  mode = "dark",
}: Props) {
  const isDark = mode === "dark";
  const colors = isDark ? COLORS_DARK : COLORS_LIGHT;

  const titleColor = isDark ? "text-slate-50" : "text-slate-900";
  const subtitleColor = isDark ? "text-slate-300" : "text-slate-500";
  const legendColor = isDark ? "#e5e7eb" : "#374151";
  const chartBg = isDark ? "bg-slate-950 border-slate-800" : "bg-white border-slate-200";

  return (
    <div className="space-y-3">
      {title && (
        <p className={`text-sm font-semibold ${titleColor}`}>{title}</p>
      )}
      {subtitle && (
        <p className={`text-[11px] ${subtitleColor}`}>{subtitle}</p>
      )}

      <div className="flex flex-col md:flex-row items-stretch gap-4">
        {/* Chart */}
        <div
          className={`h-52 flex-1 min-w-[220px] rounded-2xl border px-3 py-2 ${chartBg}`}
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                outerRadius="80%"
              >
                {data.map((entry, index) => (
                  <Cell
                    key={`slice-${entry.name}-${index}`}
                    fill={colors[index % colors.length]}
                    style={{
                      cursor: onSliceClick ? "pointer" : "default",
                    }}
                    onClick={() => onSliceClick?.(entry)}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: isDark ? "#0f172a" : "#ffffff",
                  borderRadius: 12,
                  border: `1px solid ${isDark ? "#475569" : "#e5e7eb"}`,
                  fontSize: 11,
                  color: isDark ? "#f1f5f9" : "#0f172a",
                }}
                labelStyle={{
                  color: isDark ? "#f8fafc" : "#0f172a",
                }}
                itemStyle={{
                  color: isDark ? "#f1f5f9" : "#0f172a",
                }}
              />
              <Legend
                layout="vertical"
                align="right"
                verticalAlign="middle"
                wrapperStyle={{ fontSize: 11, color: legendColor }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Right-side panel */}
        {rightContent && (
          <div className="w-full md:w-52 text-xs space-y-2">
            {rightContent}
          </div>
        )}
      </div>
    </div>
  );
}
