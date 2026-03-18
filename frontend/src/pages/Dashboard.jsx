import { Package, BarChart2, TrendingDown, RefreshCw } from 'lucide-react'
import { useMarketOverview, useTrending } from '../hooks/useAnalytics'
import ProductCard from '../components/common/ProductCard'
import { CardSkeleton, StatSkeleton } from '../components/common/LoadingSkeleton'
import { formatRelativeTime } from '../utils/formatDate'

function StatCard({ icon: Icon, label, value, sub, color = 'text-primary-600' }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
      <div className="flex items-center gap-3 mb-2">
        <div className={`p-2 rounded-lg bg-primary-50 dark:bg-primary-900/30 ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
        <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const { data: overview, isLoading: overviewLoading } = useMarketOverview()
  const { data: trending, isLoading: trendingLoading } = useTrending({ type: 'best_deal', limit: 8 })

  const stats = overview?.data
  const products = trending?.data || []

  const platformChartData = stats
    ? Object.entries(stats.platforms).map(([name, v]) => ({
        platform: name,
        avg_price: 0,
        product_count: v.products,
        avg_discount: v.avg_discount,
      }))
    : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        {stats?.last_updated && (
          <p className="text-sm text-gray-400">Cập nhật: {formatRelativeTime(stats.last_updated)}</p>
        )}
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {overviewLoading ? (
          Array.from({ length: 4 }).map((_, i) => <StatSkeleton key={i} />)
        ) : (
          <>
            <StatCard icon={Package} label="Sản phẩm theo dõi" value={stats?.total_products_tracked?.toLocaleString() || '—'} />
            <StatCard icon={BarChart2} label="Điểm giá thu thập" value={stats?.total_price_points?.toLocaleString() || '—'} />
            <StatCard
              icon={TrendingDown}
              label="Sàn đang theo dõi"
              value={Object.keys(stats?.platforms || {}).length}
              sub={Object.keys(stats?.platforms || {}).join(', ')}
            />
            <StatCard
              icon={RefreshCw}
              label="Top danh mục giảm giá"
              value={stats?.top_categories_by_discount?.[0]?.name || '—'}
              sub={stats?.top_categories_by_discount?.[0] ? `-${stats.top_categories_by_discount[0].avg_discount}% TB` : ''}
            />
          </>
        )}
      </div>

      {/* Platform Overview */}
      {!overviewLoading && platformChartData.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <h2 className="text-base font-semibold mb-4">Phân bố theo sàn</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {platformChartData.map((p) => (
              <div key={p.platform} className="text-center">
                <p className="text-lg font-bold">{p.product_count.toLocaleString()}</p>
                <p className="text-sm text-gray-500 capitalize">{p.platform}</p>
                {p.avg_discount > 0 && <p className="text-xs text-green-600">-{p.avg_discount}% TB</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Best Deals */}
      <div>
        <h2 className="text-base font-semibold mb-3">Deals tốt nhất hôm nay</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {trendingLoading
            ? Array.from({ length: 8 }).map((_, i) => <CardSkeleton key={i} />)
            : products.map((p) => <ProductCard key={p.id} product={p} />)
          }
        </div>
      </div>
    </div>
  )
}
