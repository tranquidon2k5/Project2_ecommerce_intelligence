export const PLATFORM_COLORS = {
  tiki: '#0D5CB6',
  shopee: '#EE4D2D',
  lazada: '#0F146D',
}

export const PLATFORM_LABELS = {
  tiki: 'Tiki',
  shopee: 'Shopee',
  lazada: 'Lazada',
}

export const SORT_OPTIONS = [
  { value: 'last_crawled_at:desc', label: 'Mới nhất' },
  { value: 'current_price:asc', label: 'Giá tăng dần' },
  { value: 'current_price:desc', label: 'Giá giảm dần' },
  { value: 'discount_percent:desc', label: 'Giảm giá nhiều nhất' },
  { value: 'rating_avg:desc', label: 'Đánh giá cao nhất' },
]

export const BUY_SIGNAL_CONFIG = {
  strong_buy: { label: 'Nên mua ngay', color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' },
  buy: { label: 'Nên mua', color: 'bg-green-50 text-green-700 dark:bg-green-800 dark:text-green-300' },
  hold: { label: 'Chờ thêm', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' },
  wait: { label: 'Chờ thêm', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' },
  sell: { label: 'Cảnh báo', color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' },
}

export const PERIOD_OPTIONS = [
  { value: '7d', label: '7 ngày' },
  { value: '30d', label: '30 ngày' },
  { value: '90d', label: '90 ngày' },
]
