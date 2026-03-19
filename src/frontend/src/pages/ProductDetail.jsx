import { useParams } from 'react-router-dom'
import { useState } from 'react'
import { ExternalLink, Bell, TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react'
import { useProduct } from '../hooks/useProducts'
import { usePriceHistory } from '../hooks/usePriceHistory'
import { alertService } from '../services/alertService'
import PriceTag from '../components/common/PriceTag'
import RatingStars from '../components/common/RatingStars'
import BuySignalBadge from '../components/common/BuySignalBadge'
import PriceHistoryChart from '../components/charts/PriceHistoryChart'
import { CardSkeleton } from '../components/common/LoadingSkeleton'
import { formatPrice } from '../utils/formatPrice'
import { formatRelativeTime } from '../utils/formatDate'
import { PLATFORM_LABELS, PERIOD_OPTIONS } from '../utils/constants'

function AlertModal({ productId, productName, onClose }) {
  const [email, setEmail] = useState('')
  const [targetPrice, setTargetPrice] = useState('')
  const [alertType, setAlertType] = useState('below')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await alertService.create({
        product_id: productId,
        user_email: email,
        target_price: parseInt(targetPrice),
        alert_type: alertType,
      })
      setSuccess(true)
    } catch (err) {
      alert('Lỗi: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md shadow-xl">
        <h3 className="font-bold text-lg mb-4">Tạo Alert giá</h3>
        <p className="text-sm text-gray-500 mb-4 line-clamp-2">{productName}</p>

        {success ? (
          <div className="text-center py-4">
            <p className="text-green-600 font-medium">✓ Alert đã được tạo!</p>
            <button onClick={onClose} className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm">Đóng</button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3">
            <input
              type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="Email của bạn" className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 text-sm"
            />
            <input
              type="number" required value={targetPrice} onChange={(e) => setTargetPrice(e.target.value)}
              placeholder="Giá mục tiêu (VND)" className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 text-sm"
            />
            <select
              value={alertType} onChange={(e) => setAlertType(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 text-sm"
            >
              <option value="below">Thông báo khi giá dưới</option>
              <option value="above">Thông báo khi giá trên</option>
              <option value="any_change">Bất kỳ thay đổi nào</option>
            </select>
            <div className="flex gap-2 pt-2">
              <button type="button" onClick={onClose} className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm">Hủy</button>
              <button type="submit" disabled={loading} className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm disabled:opacity-50">
                {loading ? 'Đang lưu...' : 'Tạo Alert'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

export default function ProductDetail() {
  const { id } = useParams()
  const [period, setPeriod] = useState('30d')
  const [showAlert, setShowAlert] = useState(false)

  const { data: productData, isLoading } = useProduct(id)
  const { data: historyData, isLoading: histLoading } = usePriceHistory(id, period)

  if (isLoading) return (
    <div className="space-y-4">
      <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3 animate-pulse" />
      <CardSkeleton />
    </div>
  )

  const product = productData?.data
  if (!product) return <p className="text-gray-400">Không tìm thấy sản phẩm</p>

  const history = historyData?.data || []
  const ai = product.ai_insights || {}
  const priceStats = product.price_stats || {}

  const TrendIcon = ai.trend_direction === 'up' ? TrendingUp
    : ai.trend_direction === 'down' ? TrendingDown : Minus

  return (
    <div className="space-y-5 max-w-4xl">
      {showAlert && <AlertModal productId={product.id} productName={product.name} onClose={() => setShowAlert(false)} />}

      {/* Hero */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <div className="flex gap-5 flex-col md:flex-row">
          {product.image_url && (
            <img src={product.image_url} alt={product.name} className="w-full md:w-48 h-48 object-cover rounded-lg shrink-0" />
          )}
          <div className="flex-1 space-y-3">
            <div>
              <span className="text-xs text-gray-400 uppercase font-medium">{PLATFORM_LABELS[product.platform] || product.platform}</span>
              <h1 className="text-xl font-bold leading-snug mt-0.5">{product.name}</h1>
              {product.seller_name && <p className="text-sm text-gray-500">Người bán: {product.seller_name}</p>}
            </div>

            <PriceTag price={product.current_price} originalPrice={product.original_price} discountPercent={product.discount_percent} size="lg" />

            {product.rating_avg && <RatingStars rating={product.rating_avg} count={product.rating_count} size="md" />}

            {ai.buy_signal && (
              <div className="flex items-center gap-2">
                <BuySignalBadge signal={ai.buy_signal} />
                <TrendIcon className="w-4 h-4 text-gray-500" />
                {ai.trend_direction && <span className="text-sm text-gray-500">Xu hướng: {ai.trend_direction}</span>}
              </div>
            )}

            <div className="flex gap-2 pt-1">
              <a href={product.url} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium">
                <ExternalLink className="w-4 h-4" /> Mua ngay
              </a>
              <button onClick={() => setShowAlert(true)}
                className="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-700">
                <Bell className="w-4 h-4" /> Tạo Alert
              </button>
            </div>

            {product.last_crawled_at && (
              <p className="text-xs text-gray-400">Cập nhật: {formatRelativeTime(product.last_crawled_at)}</p>
            )}
          </div>
        </div>
      </div>

      {/* Price Stats */}
      {(priceStats.min_30d || priceStats.max_30d || priceStats.avg_30d) && (
        <div className="grid grid-cols-3 gap-3">
          {[['Thấp nhất 30d', priceStats.min_30d], ['Cao nhất 30d', priceStats.max_30d], ['Trung bình 30d', priceStats.avg_30d]].map(([label, val]) => (
            <div key={label} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 text-center">
              <p className="text-xs text-gray-500 mb-1">{label}</p>
              <p className="font-bold text-sm">{formatPrice(val)}</p>
            </div>
          ))}
        </div>
      )}

      {/* Price History Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold">Lịch sử giá</h2>
          <div className="flex gap-1">
            {PERIOD_OPTIONS.map((p) => (
              <button key={p.value} onClick={() => setPeriod(p.value)}
                className={`px-3 py-1 rounded text-xs font-medium ${period === p.value ? 'bg-primary-600 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}>
                {p.label}
              </button>
            ))}
          </div>
        </div>
        {histLoading
          ? <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse" />
          : history.length > 0
            ? <PriceHistoryChart data={history} minPrice={priceStats.min_30d} />
            : <p className="text-center text-gray-400 py-12">Chưa có dữ liệu lịch sử giá</p>
        }
      </div>

      {/* Fake review warning */}
      {product.fake_review_percent > 10 && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4 flex gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-600 shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-yellow-800 dark:text-yellow-300">Cảnh báo đánh giá</p>
            <p className="text-sm text-yellow-700 dark:text-yellow-400">{Math.round(product.fake_review_percent)}% đánh giá có thể không xác thực</p>
          </div>
        </div>
      )}
    </div>
  )
}
