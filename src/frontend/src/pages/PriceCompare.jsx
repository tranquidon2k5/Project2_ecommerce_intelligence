import { useState } from 'react'
import { usePriceComparison } from '../hooks/useAnalytics'
import SearchBar from '../components/common/SearchBar'
import { formatPrice } from '../utils/formatPrice'
import { PLATFORM_LABELS, PLATFORM_COLORS } from '../utils/constants'
import { ExternalLink, TrendingDown } from 'lucide-react'
import clsx from 'clsx'

export default function PriceCompare() {
  const [q, setQ] = useState('')
  const [submittedQ, setSubmittedQ] = useState('')

  const { data, isLoading } = usePriceComparison(submittedQ)
  const comparisons = data?.data?.comparisons || []

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold">So sánh giá</h1>
      <p className="text-sm text-gray-500">Tìm sản phẩm để so sánh giá giữa các sàn thương mại điện tử</p>

      <div className="flex gap-3">
        <SearchBar
          value={q}
          onChange={setQ}
          onClear={() => { setQ(''); setSubmittedQ('') }}
          placeholder="Nhập tên sản phẩm (vd: iphone 15)..."
          className="flex-1"
        />
        <button
          onClick={() => setSubmittedQ(q)}
          disabled={!q.trim()}
          className="px-5 py-2.5 bg-primary-600 text-white rounded-xl text-sm font-medium disabled:opacity-50 hover:bg-primary-700"
        >
          So sánh
        </button>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded-xl animate-pulse" />
          ))}
        </div>
      )}

      {!isLoading && submittedQ && comparisons.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <p>Không tìm thấy kết quả cho "{submittedQ}"</p>
        </div>
      )}

      <div className="space-y-4">
        {comparisons.map((comp, idx) => {
          const minPrice = Math.min(...comp.platforms.map((p) => p.price))
          return (
            <div key={idx} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="px-5 py-3 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
                <h3 className="font-medium text-sm line-clamp-1">{comp.product_name}</h3>
                {comp.price_diff_percent > 0 && (
                  <span className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400 font-medium">
                    <TrendingDown className="w-3.5 h-3.5" />
                    Chênh lệch {comp.price_diff_percent.toFixed(1)}%
                  </span>
                )}
              </div>
              <div className="divide-y divide-gray-100 dark:divide-gray-700">
                {comp.platforms.map((p, pi) => (
                  <div key={pi} className={clsx(
                    'flex items-center gap-4 px-5 py-3',
                    p.price === minPrice && 'bg-green-50 dark:bg-green-900/10'
                  )}>
                    <span
                      className="text-xs font-bold text-white px-2 py-0.5 rounded w-20 text-center shrink-0"
                      style={{ backgroundColor: PLATFORM_COLORS[p.platform] || '#666' }}
                    >
                      {PLATFORM_LABELS[p.platform] || p.platform}
                    </span>
                    <span className={clsx(
                      'font-bold text-sm flex-1',
                      p.price === minPrice ? 'text-green-700 dark:text-green-400' : ''
                    )}>
                      {formatPrice(p.price)}
                      {p.price === minPrice && <span className="ml-2 text-xs font-medium">✓ Rẻ nhất</span>}
                    </span>
                    {p.rating && <span className="text-sm text-yellow-500">★ {p.rating.toFixed(1)}</span>}
                    <a href={p.url} target="_blank" rel="noopener noreferrer"
                      className="text-primary-600 hover:text-primary-700">
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
