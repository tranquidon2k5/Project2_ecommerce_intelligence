import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { formatPriceShort } from '../../utils/formatPrice'
import { PLATFORM_COLORS, PLATFORM_LABELS } from '../../utils/constants'

export default function PlatformCompareChart({ data = [] }) {
  // Auto-detect: nếu tất cả avg_price = 0, dùng product_count
  const hasPrice = data.some(d => d.avg_price > 0)
  const useKey = hasPrice ? 'price' : 'count'

  const chartData = data.map((d) => ({
    platform: PLATFORM_LABELS[d.platform] || d.platform,
    price: d.avg_price,
    count: d.product_count,
    raw: d.platform,
  }))

  const formatter = useKey === 'price'
    ? (v) => [formatPriceShort(v), 'Giá TB']
    : (v) => [v.toLocaleString(), 'Sản phẩm']

  const yFormatter = useKey === 'price' ? formatPriceShort : (v) => v

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
          <XAxis dataKey="platform" tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={yFormatter} tick={{ fontSize: 11 }} width={60} />
          <Tooltip formatter={formatter} />
          <Bar dataKey={useKey} radius={[4, 4, 0, 0]}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={PLATFORM_COLORS[entry.raw] || '#3b82f6'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
