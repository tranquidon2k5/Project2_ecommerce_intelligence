import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { formatPrice, formatPriceShort } from '../../utils/formatPrice'
import { formatDate } from '../../utils/formatDate'

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-lg text-sm">
      <p className="font-medium mb-1">{formatDate(label)}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.name}: {formatPrice(p.value)}
        </p>
      ))}
    </div>
  )
}

export default function PriceHistoryChart({ data = [], minPrice, maxPrice }) {
  const chartData = data.map((point) => ({
    date: point.crawled_at || point.date,
    price: point.price ?? point.avg,
  }))

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
          <XAxis
            dataKey="date"
            tickFormatter={(v) => formatDate(v)}
            tick={{ fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            tickFormatter={formatPriceShort}
            tick={{ fontSize: 11 }}
            width={70}
          />
          <Tooltip content={<CustomTooltip />} />
          {minPrice && <ReferenceLine y={minPrice} stroke="#22c55e" strokeDasharray="4 2" label={{ value: 'Thấp nhất', fontSize: 10 }} />}
          <Area
            type="monotone"
            dataKey="price"
            name="Giá"
            stroke="#3b82f6"
            fill="url(#priceGradient)"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
