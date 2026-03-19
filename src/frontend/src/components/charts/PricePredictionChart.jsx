import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
  ResponsiveContainer, Legend,
} from 'recharts'
import { formatPrice } from '../../utils/formatPrice'

export default function PricePredictionChart({ history = [], predictions = [] }) {
  // Combine: historical data (solid) + predicted (dashed)
  const historyData = history.map((h) => ({
    date: h.date?.slice(0, 10) ?? '',
    actual: h.price,
    predicted: undefined,
    lower: undefined,
    upper: undefined,
  }))

  const predData = predictions.map((p) => ({
    date: p.date,
    actual: undefined,
    predicted: p.price,
    lower: p.lower,
    upper: p.upper,
  }))

  const data = [...historyData, ...predData]
  const splitDate = historyData.at(-1)?.date

  const fmt = (v) => (v != null ? formatPrice(v) : '')

  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="gradActual" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="gradPred" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(d) => d.slice(5)} />
        <YAxis tickFormatter={fmt} tick={{ fontSize: 11 }} width={90} />
        <Tooltip formatter={(v) => (v != null ? formatPrice(v) : 'N/A')} />
        <Legend />
        {splitDate && (
          <ReferenceLine x={splitDate} stroke="#9ca3af" strokeDasharray="4 2" label={{ value: 'Hôm nay', fontSize: 11 }} />
        )}
        <Area
          type="monotone"
          dataKey="actual"
          name="Lịch sử"
          stroke="#6366f1"
          fill="url(#gradActual)"
          strokeWidth={2}
          dot={false}
          connectNulls={false}
        />
        <Area
          type="monotone"
          dataKey="predicted"
          name="Dự báo"
          stroke="#f59e0b"
          fill="url(#gradPred)"
          strokeWidth={2}
          strokeDasharray="5 3"
          dot={false}
          connectNulls={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
