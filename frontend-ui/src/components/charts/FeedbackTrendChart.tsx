import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
} from "recharts";
import type { Theme } from "../../hooks/useTheme";
import type { SentimentCounts } from "../../services/api";

export type TrendPoint = {
  time_label: string;
  sentimentCounts: SentimentCounts;
};

type Props = {
  title?: string;
  data: TrendPoint[];
  mode?: Theme; // "light" | "dark"
};

const THY_RED = "#b7312c";

export default function FeedbackTrendChart({
  title,
  data,
  mode = "dark",
}: Props) {
  const isDark = mode === "dark";

  const bg = isDark ? "bg-slate-950" : "bg-white";
  const border = isDark ? "border-slate-800" : "border-slate-200";
  const textTitle = isDark ? "text-slate-50" : "text-slate-900";

  const gridColor = isDark ? "#1f2937" : "#e5e7eb";
  const axisColor = isDark ? "#4b5563" : "#d1d5db";
  const tickColor = isDark ? "#9ca3af" : "#6b7280";
  const tooltipBg = isDark ? "#020617" : "#ffffff";
  const tooltipBorder = isDark ? "#4b5563" : "#e5e7eb";
  const legendColor = isDark ? "#e5e7eb" : "#374151";
  const tooltipText = isDark ? "#e5e7eb" : "#0f172a";
  const tooltipLabel = isDark ? "#e5e7eb" : "#111827";

  return (
    <div className="space-y-2">
      {title && <p className={`text-sm font-semibold ${textTitle}`}>{title}</p>}

      <div className={`h-64 w-full rounded-2xl border px-4 py-3 ${bg} ${border}`}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 16, left: -10, bottom: 0 }}
          >
            <defs>
              <linearGradient id="positiveFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#22c55e" stopOpacity={0.4} />
                <stop offset="100%" stopColor="#22c55e" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="negativeFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={THY_RED} stopOpacity={0.45} />
                <stop offset="100%" stopColor={THY_RED} stopOpacity={0.06} />
              </linearGradient>
              <linearGradient id="neutralFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#9ca3af" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#9ca3af" stopOpacity={0.05} />
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke={gridColor}
            />
            <XAxis
              dataKey="time_label"
              tick={{ fontSize: 11, fill: tickColor }}
              axisLine={{ stroke: axisColor }}
              tickLine={{ stroke: axisColor }}
            />
            <YAxis
              tick={{ fontSize: 11, fill: tickColor }}
              axisLine={{ stroke: axisColor }}
              tickLine={{ stroke: axisColor }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: tooltipBg,
                borderRadius: 12,
                border: `1px solid ${tooltipBorder}`,
                fontSize: 11,
                color: tooltipText,
              }}
              labelStyle={{ color: tooltipLabel }}
            />
            <Legend
              iconSize={10}
              wrapperStyle={{ fontSize: 11, color: legendColor }}
            />

            <Area
              type="monotone"
              dataKey={(d) => d.sentimentCounts.positive}
              name="Positive"
              stroke="#22c55e"
              strokeWidth={2}
              fill="url(#positiveFill)"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Area
              type="monotone"
              dataKey={(d) => d.sentimentCounts.negative}
              name="Negative"
              stroke={THY_RED}
              strokeWidth={2}
              fill="url(#negativeFill)"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Area
              type="monotone"
              dataKey={(d) => d.sentimentCounts.neutral}
              name="Neutral"
              stroke="#9ca3af"
              strokeWidth={2}
              fill="url(#neutralFill)"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
