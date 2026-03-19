import { useState } from 'react'
import { useTrending } from '../hooks/useAnalytics'
import ProductCard from '../components/common/ProductCard'
import { CardSkeleton } from '../components/common/LoadingSkeleton'
import clsx from 'clsx'

const TABS = [
  { value: 'price_drop', label: 'Giảm giá sốc' },
  { value: 'best_seller', label: 'Bán chạy' },
  { value: 'best_deal', label: 'Deals tốt nhất' },
  { value: 'most_reviewed', label: 'Nhiều đánh giá' },
]

export default function Trending() {
  const [activeTab, setActiveTab] = useState('most_reviewed')
  const { data, isLoading } = useTrending({ type: activeTab, limit: 20 })
  const products = data?.data || []

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold">Trending</h1>

      <div className="flex gap-2 flex-wrap">
        {TABS.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setActiveTab(tab.value)}
            className={clsx(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === tab.value
                ? 'bg-primary-600 text-white'
                : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {isLoading
          ? Array.from({ length: 20 }).map((_, i) => <CardSkeleton key={i} />)
          : products.length > 0
            ? products.map((p) => <ProductCard key={p.id} product={p} />)
            : <p className="col-span-full text-center text-gray-400 py-12">Không có sản phẩm</p>
        }
      </div>
    </div>
  )
}
