import { useHealth, useSystemStats, useCrawlLogs } from '../hooks/useSystem'
import { StatSkeleton, TableRowSkeleton } from '../components/common/LoadingSkeleton'
import { Activity, Database, Server, Wifi, Clock, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

function formatUptime(seconds) {
  if (!seconds && seconds !== 0) return '--'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  if (h > 0) return `${h}h ${m}m`
  return `${m}m`
}

function formatDateTime(iso) {
  if (!iso) return '--'
  return new Date(iso).toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function StatusDot({ ok }) {
  return (
    <span
      className={`inline-block w-3 h-3 rounded-full ${ok ? 'bg-green-500' : 'bg-red-500'}`}
      aria-label={ok ? 'OK' : 'Error'}
    />
  )
}

function StatusBadge({ status }) {
  const map = {
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    completed: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
    failed: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    running: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
    partial: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
  }
  const cls = map[status] || 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {status}
    </span>
  )
}

function FreshnessBanner({ freshness }) {
  if (!freshness || freshness.minutes_since_last_crawl == null) {
    return (
      <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-4 flex items-center gap-3">
        <AlertTriangle className="w-5 h-5 text-gray-400" />
        <span className="text-sm text-gray-500 dark:text-gray-400">
          Chưa có dữ liệu crawl
        </span>
      </div>
    )
  }

  const mins = freshness.minutes_since_last_crawl
  let colorClass = 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
  let IconComp = CheckCircle
  if (mins > 360) {
    colorClass = 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
    IconComp = XCircle
  } else if (mins > 60) {
    colorClass = 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
    IconComp = AlertTriangle
  }

  return (
    <div className={`rounded-xl p-4 flex items-center gap-3 ${colorClass}`}>
      <IconComp className="w-5 h-5" />
      <span className="text-sm font-medium">
        Lần crawl cuối: {Math.round(mins).toLocaleString('vi-VN')} phút trước
      </span>
    </div>
  )
}

export default function SystemStatus() {
  const { data: healthData, isLoading: healthLoading, isError: healthError } = useHealth()
  const { data: statsData, isLoading: statsLoading, isError: statsError } = useSystemStats()
  const { data: crawlData, isLoading: crawlLoading, isError: crawlError } = useCrawlLogs()

  const health = healthData?.data
  const stats = statsData?.data
  const crawlLogs = crawlData?.data ?? []

  const checks = health?.checks ?? {}
  const counts = stats?.counts ?? {}
  const apiMetrics = stats?.api_metrics ?? {}
  const freshness = stats?.data_freshness ?? null

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Trạng thái hệ thống</h1>

      {/* Error banners */}
      {healthError && (
        <div className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-xl p-4 text-sm flex items-center gap-2">
          <XCircle className="w-4 h-4" />
          Không thể tải trạng thái health check
        </div>
      )}
      {statsError && (
        <div className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-xl p-4 text-sm flex items-center gap-2">
          <XCircle className="w-4 h-4" />
          Không thể tải thống kê hệ thống
        </div>
      )}

      {/* Health Status */}
      <section>
        <h2 className="text-lg font-semibold mb-3">Health Check</h2>
        {healthLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatSkeleton />
            <StatSkeleton />
            <StatSkeleton />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { key: 'api', label: 'API', icon: Server },
              { key: 'database', label: 'Database', icon: Database },
              { key: 'redis', label: 'Redis', icon: Wifi },
            ].map(({ key, label, icon: Icon }) => {
              const ok = checks[key] === 'ok'
              return (
                <div
                  key={key}
                  className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 flex items-center gap-4"
                >
                  <Icon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-600 dark:text-gray-400">{label}</div>
                    <div className="text-base font-semibold capitalize">{checks[key] ?? '--'}</div>
                  </div>
                  <StatusDot ok={ok} />
                </div>
              )
            })}
          </div>
        )}
      </section>

      {/* System Metrics */}
      <section>
        <h2 className="text-lg font-semibold mb-3">Thống kê dữ liệu</h2>
        {statsLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatSkeleton />
            <StatSkeleton />
            <StatSkeleton />
            <StatSkeleton />
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Sản phẩm', value: counts.products },
              { label: 'Lịch sử giá', value: counts.price_history_records },
              { label: 'Đánh giá', value: counts.reviews },
              { label: 'Uptime', value: formatUptime(apiMetrics.uptime_seconds), raw: true },
            ].map(({ label, value, raw }) => (
              <div
                key={label}
                className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4"
              >
                <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">{label}</div>
                <div className="text-2xl font-bold">
                  {raw ? value : (value != null ? Number(value).toLocaleString('vi-VN') : '--')}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Data Freshness */}
      <section>
        <h2 className="text-lg font-semibold mb-3">Độ mới dữ liệu</h2>
        {statsLoading ? <StatSkeleton /> : <FreshnessBanner freshness={freshness} />}
      </section>

      {/* API Performance */}
      <section>
        <h2 className="text-lg font-semibold mb-3">API Performance</h2>
        {statsLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatSkeleton />
            <StatSkeleton />
            <StatSkeleton />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { label: 'Total Requests', value: apiMetrics.total_requests != null ? Number(apiMetrics.total_requests).toLocaleString('vi-VN') : '--' },
              { label: 'Error Rate', value: apiMetrics.error_rate_percent != null ? `${apiMetrics.error_rate_percent.toFixed(2)}%` : '--' },
              { label: 'Avg Latency', value: apiMetrics.avg_latency_ms != null ? `${apiMetrics.avg_latency_ms.toFixed(1)} ms` : '--' },
            ].map(({ label, value }) => (
              <div
                key={label}
                className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4"
              >
                <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">{label}</div>
                <div className="text-2xl font-bold">{value}</div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Crawl Logs Table */}
      <section>
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold">Crawl Logs</h2>
            <p className="text-sm text-gray-500 mt-0.5">Lịch sử các phiên thu thập dữ liệu</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 dark:bg-gray-900/50">
                <tr>
                  <th className="text-left px-5 py-3 font-medium text-gray-600 dark:text-gray-400">Spider</th>
                  <th className="text-center px-5 py-3 font-medium text-gray-600 dark:text-gray-400">Status</th>
                  <th className="text-right px-5 py-3 font-medium text-gray-600 dark:text-gray-400">Crawled</th>
                  <th className="text-right px-5 py-3 font-medium text-gray-600 dark:text-gray-400">New</th>
                  <th className="text-right px-5 py-3 font-medium text-gray-600 dark:text-gray-400">Errors</th>
                  <th className="text-right px-5 py-3 font-medium text-gray-600 dark:text-gray-400">Duration</th>
                  <th className="text-left px-5 py-3 font-medium text-gray-600 dark:text-gray-400">Started At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                {crawlLoading
                  ? Array.from({ length: 5 }).map((_, i) => <TableRowSkeleton key={i} cols={7} />)
                  : crawlError
                    ? (
                      <tr>
                        <td colSpan={7} className="text-center py-10 text-red-500">
                          Lỗi tải dữ liệu crawl logs
                        </td>
                      </tr>
                    )
                    : crawlLogs.length === 0
                      ? (
                        <tr>
                          <td colSpan={7} className="text-center py-10 text-gray-400">
                            Chưa có dữ liệu crawl
                          </td>
                        </tr>
                      )
                      : crawlLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                          <td className="px-5 py-3 font-medium">{log.spider_name}</td>
                          <td className="px-5 py-3 text-center">
                            <StatusBadge status={log.status} />
                          </td>
                          <td className="px-5 py-3 text-right">
                            {log.products_crawled != null ? Number(log.products_crawled).toLocaleString('vi-VN') : '--'}
                          </td>
                          <td className="px-5 py-3 text-right">
                            {log.products_new != null ? Number(log.products_new).toLocaleString('vi-VN') : '--'}
                          </td>
                          <td className="px-5 py-3 text-right">
                            {log.errors_count != null ? Number(log.errors_count).toLocaleString('vi-VN') : '--'}
                          </td>
                          <td className="px-5 py-3 text-right">
                            {log.duration_seconds != null ? `${log.duration_seconds}s` : '--'}
                          </td>
                          <td className="px-5 py-3">{formatDateTime(log.started_at)}</td>
                        </tr>
                      ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  )
}
