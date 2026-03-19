import { useState } from 'react'
import { useAnomalies, usePricePrediction } from '../hooks/useAIInsights'
import PricePredictionChart from '../components/charts/PricePredictionChart'
import { formatPrice } from '../utils/formatPrice'
import { TableRowSkeleton } from '../components/common/LoadingSkeleton'
import BuySignalBadge from '../components/common/BuySignalBadge'

export default function AIInsights() {
  const [previewId, setPreviewId] = useState(null)
  const { data: anomaliesData, isLoading } = useAnomalies(20)
  const { data: predData } = usePricePrediction(previewId, 7)

  const anomalies = anomaliesData?.data ?? []
  const predictions = predData?.data?.predictions ?? []

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">AI Insights</h1>

      {/* Anomaly Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold">Phát hiện bất thường giá</h2>
          <p className="text-sm text-gray-500 mt-0.5">Sản phẩm có biến động giá bất thường (điểm &gt; 0.7)</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 dark:bg-gray-900/50">
              <tr>
                <th className="text-left px-5 py-3 font-medium text-gray-600 dark:text-gray-400">Sản phẩm</th>
                <th className="text-right px-5 py-3 font-medium text-gray-600 dark:text-gray-400">Giá hiện tại</th>
                <th className="text-right px-5 py-3 font-medium text-gray-600 dark:text-gray-400">Điểm bất thường</th>
                <th className="text-center px-5 py-3 font-medium text-gray-600 dark:text-gray-400">Tín hiệu</th>
                <th className="text-center px-5 py-3 font-medium text-gray-600 dark:text-gray-400">Dự báo</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {isLoading
                ? Array.from({ length: 5 }).map((_, i) => <TableRowSkeleton key={i} cols={5} />)
                : anomalies.length === 0
                  ? (
                    <tr>
                      <td colSpan={5} className="text-center py-10 text-gray-400">
                        Không phát hiện bất thường giá nào
                      </td>
                    </tr>
                  )
                  : anomalies.map((row) => (
                    <tr
                      key={row.product_id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
                      onClick={() => setPreviewId(row.product_id === previewId ? null : row.product_id)}
                    >
                      <td className="px-5 py-3 max-w-xs truncate font-medium">{row.product_name}</td>
                      <td className="px-5 py-3 text-right text-primary-600">{formatPrice(row.current_price)}</td>
                      <td className="px-5 py-3 text-right">
                        <span className={`font-semibold ${row.anomaly_score > 0.85 ? 'text-red-500' : 'text-amber-500'}`}>
                          {(row.anomaly_score * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td className="px-5 py-3 text-center">
                        <BuySignalBadge signal={row.buy_signal} />
                      </td>
                      <td className="px-5 py-3 text-center text-xs text-blue-500 underline">
                        {row.product_id === previewId ? 'Ẩn' : 'Xem dự báo'}
                      </td>
                    </tr>
                  ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Price Prediction Preview */}
      {previewId && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h2 className="text-lg font-semibold mb-4">Dự báo giá 7 ngày tới</h2>
          {predictions.length > 0
            ? <PricePredictionChart history={[]} predictions={predictions} />
            : <p className="text-center text-gray-400 py-10">Đang tải dự báo...</p>
          }
        </div>
      )}

      {/* Buy Signal Summary */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <h2 className="text-lg font-semibold mb-4">Tóm tắt tín hiệu mua</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { signal: 'strong_buy', label: 'Mua mạnh', color: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' },
            { signal: 'buy', label: 'Nên mua', color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300' },
            { signal: 'hold', label: 'Giữ', color: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300' },
            { signal: 'wait', label: 'Chờ đợi', color: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300' },
          ].map(({ signal, label, color }) => {
            const count = anomalies.filter((a) => a.buy_signal === signal).length
            return (
              <div key={signal} className={`rounded-lg p-4 text-center ${color}`}>
                <div className="text-3xl font-bold">{count}</div>
                <div className="text-sm mt-1 font-medium">{label}</div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
