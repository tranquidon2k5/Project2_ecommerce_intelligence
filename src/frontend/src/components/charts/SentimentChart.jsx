import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const SENTIMENT_COLORS = {
  positive: '#22c55e',
  neutral: '#f59e0b',
  negative: '#ef4444',
}

export default function SentimentChart({ positive = 0, neutral = 0, negative = 0 }) {
  const data = [
    { name: 'Tích cực', value: positive, key: 'positive' },
    { name: 'Trung tính', value: neutral, key: 'neutral' },
    { name: 'Tiêu cực', value: negative, key: 'negative' },
  ].filter((d) => d.value > 0)

  if (!data.length) return <p className="text-sm text-gray-400">Không có dữ liệu</p>

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={3}>
            {data.map((entry) => (
              <Cell key={entry.key} fill={SENTIMENT_COLORS[entry.key]} />
            ))}
          </Pie>
          <Tooltip formatter={(v) => [`${v}%`, '']} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
