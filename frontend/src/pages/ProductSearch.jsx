import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useProducts } from '../hooks/useProducts'
import { useFilterStore } from '../store/useFilterStore'
import { useDebounce } from '../hooks/useDebounce'
import ProductCard from '../components/common/ProductCard'
import SearchBar from '../components/common/SearchBar'
import Pagination from '../components/common/Pagination'
import { CardSkeleton } from '../components/common/LoadingSkeleton'
import { SORT_OPTIONS } from '../utils/constants'

export default function ProductSearch() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [q, setQ] = useState(searchParams.get('q') || '')
  const debouncedQ = useDebounce(q, 300)
  const [page, setPage] = useState(1)
  const { platform, minPrice, maxPrice, minRating, sortBy, sortOrder, setFilter } = useFilterStore()

  useEffect(() => {
    if (searchParams.get('q') !== q) setPage(1)
  }, [debouncedQ])

  const params = {
    q: debouncedQ || undefined,
    platform: platform || undefined,
    min_price: minPrice || undefined,
    max_price: maxPrice || undefined,
    min_rating: minRating || undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
    page,
    per_page: 20,
  }

  const { data, isLoading, isError } = useProducts(params)
  const products = data?.data || []
  const meta = data?.meta || {}

  const handleSort = (value) => {
    const [field, order] = value.split(':')
    setFilter('sortBy', field)
    setFilter('sortOrder', order)
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Tìm kiếm sản phẩm</h1>

      <div className="flex gap-3 flex-wrap">
        <SearchBar
          value={q}
          onChange={(v) => { setQ(v); setPage(1) }}
          onClear={() => { setQ(''); setPage(1) }}
          className="flex-1 min-w-60"
        />

        <select
          value={`${sortBy}:${sortOrder}`}
          onChange={(e) => handleSort(e.target.value)}
          className="px-3 py-2 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>

        <select
          value={platform}
          onChange={(e) => { setFilter('platform', e.target.value); setPage(1) }}
          className="px-3 py-2 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
        >
          <option value="">Tất cả sàn</option>
          <option value="tiki">Tiki</option>
          <option value="shopee">Shopee</option>
          <option value="lazada">Lazada</option>
        </select>
      </div>

      {meta.total != null && (
        <p className="text-sm text-gray-500">Tìm thấy {meta.total?.toLocaleString()} sản phẩm</p>
      )}

      {isError && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 text-sm text-red-700 dark:text-red-400">
          Không thể tải dữ liệu. Kiểm tra backend có đang chạy không.
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {isLoading
          ? Array.from({ length: 20 }).map((_, i) => <CardSkeleton key={i} />)
          : products.map((p) => <ProductCard key={p.id} product={p} />)
        }
      </div>

      {!isLoading && products.length === 0 && !isError && (
        <div className="text-center py-16 text-gray-400">
          <p className="text-lg">Không tìm thấy sản phẩm</p>
          <p className="text-sm mt-1">Thử tìm kiếm với từ khóa khác</p>
        </div>
      )}

      <Pagination
        page={meta.page || page}
        totalPages={meta.total_pages || 1}
        onPageChange={setPage}
      />
    </div>
  )
}
