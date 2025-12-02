import {
  PieChart,
  Pie,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
} from "recharts";
import type { ReactNode } from "react";

export type PieItem = {
  name: string;
  value: number;
  id?: string; // optional – used for navigation (e.g. department id)
};

type Props = {
  title?: string;
  subtitle?: string;
  data: PieItem[];
  onSliceClick?: (item: PieItem) => void;
  rightContent?: ReactNode; // stuff you want to show to the right of the chart
};

const COLORS = [
  "#2563eb",
  "#0ea5e9",
  "#10b981",
  "#f97316",
  "#e11d48",
  "#a855f7",
];

export default function DistributionPie({
  title,
  subtitle,
  data,
  onSliceClick,
  rightContent,
}: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
      {title && (
        <p className="text-sm font-semibold text-slate-900 mb-1">{title}</p>
      )}
      {subtitle && (
        <p className="text-[11px] text-slate-500 mb-3">{subtitle}</p>
      )}

      <div className="flex items-center gap-4">
        {/* Chart */}
        <div className="h-52 flex-1 min-w-[220px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                outerRadius="80%"
                innerRadius="50%"
              >
                {data.map((entry, index) => (
                  <Cell
                    key={`slice-${entry.name}-${index}`}
                    fill={COLORS[index % COLORS.length]}
                    style={{
                      cursor: onSliceClick ? "pointer" : "default",
                    }}
                    onClick={() => onSliceClick?.(entry)}
                  />
                ))}
              </Pie>
              <Tooltip />
              <Legend
                layout="vertical"
                align="right"
                verticalAlign="middle"
                wrapperStyle={{ fontSize: 11 }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Right-side panel for numbers (optional) */}
        {rightContent && (
          <div className="w-48 text-xs text-slate-700">{rightContent}</div>
        )}
      </div>
    </div>
  );
}
