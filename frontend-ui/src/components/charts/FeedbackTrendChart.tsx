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

export type TrendPoint = {
  label: string;
  positive: number;
  negative: number;
};

type Props = {
  title?: string;
  data: TrendPoint[];
};

export default function FeedbackTrendChart({ title, data }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4">
      {title && (
        <p className="text-sm font-semibold text-slate-900 mb-2">{title}</p>
      )}

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 16, left: -10, bottom: 0 }}
          >
            <defs>
              <linearGradient id="positiveFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#10b981" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="negativeFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f97373" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#f97373" stopOpacity={0.05} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="label" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip />
            <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />

            <Area
              type="monotone"
              dataKey="positive"
              name="Positive"
              stroke="#10b981"
              strokeWidth={2}
              fill="url(#positiveFill)"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Area
              type="monotone"
              dataKey="negative"
              name="Negative"
              stroke="#f97373"
              strokeWidth={2}
              fill="url(#negativeFill)"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
