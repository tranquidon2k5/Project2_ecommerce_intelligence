import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { alertService } from '../services/alertService'
import { Bell, Trash2, CheckCircle, Clock } from 'lucide-react'
import { formatPrice } from '../utils/formatPrice'
import { formatDate } from '../utils/formatDate'
import { useProducts } from '../hooks/useProducts'
import { useDebounce } from '../hooks/useDebounce'

export default function Alerts() {
  const [email, setEmail] = useState('')
  const [submittedEmail, setSubmittedEmail] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [productSearch, setProductSearch] = useState('')
  const debouncedSearch = useDebounce(productSearch, 400)
  const queryClient = useQueryClient()

  // Form state
  const [form, setForm] = useState({ product_id: '', target_price: '', alert_type: 'below' })
  const [selectedProduct, setSelectedProduct] = useState(null)

  // Product search for form
  const { data: productData } = useProducts(
    debouncedSearch ? { q: debouncedSearch, per_page: 5 } : null
  )
  const searchResults = debouncedSearch ? (productData?.data || []) : []

  // Alerts list
  const { data: alertsData, isLoading } = useQuery({
    queryKey: ['alerts', submittedEmail],
    queryFn: () => alertService.list(submittedEmail),
    enabled: !!submittedEmail,
  })
  const alerts = alertsData?.data || []

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: alertService.delete,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts', submittedEmail] }),
  })

  // Create mutation
  const createMutation = useMutation({
    mutationFn: alertService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts', submittedEmail] })
      setShowForm(false)
      setForm({ product_id: '', target_price: '', alert_type: 'below' })
      setSelectedProduct(null)
      setProductSearch('')
    },
  })

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!selectedProduct) return alert('Chọn sản phẩm')
    createMutation.mutate({
      product_id: selectedProduct.id,
      user_email: submittedEmail,
      target_price: parseInt(form.target_price),
      alert_type: form.alert_type,
    })
  }

  return (
    <div className="space-y-5 max-w-2xl">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Price Alerts</h1>
      </div>

      {/* Email lookup */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <h2 className="font-medium mb-3">Xem alerts của bạn</h2>
        <div className="flex gap-2">
          <input
            type="email" value={email} onChange={(e) => setEmail(e.target.value)}
            placeholder="Nhập email..."
            className="flex-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 text-sm"
          />
          <button
            onClick={() => { setSubmittedEmail(email); setShowForm(true) }}
            disabled={!email}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm disabled:opacity-50 hover:bg-primary-700"
          >
            Tìm kiếm
          </button>
        </div>
      </div>

      {/* Create Alert Form */}
      {showForm && submittedEmail && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-medium">Tạo Alert mới</h2>
          </div>
          <form onSubmit={handleCreate} className="space-y-3">
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Sản phẩm</label>
              <input
                value={productSearch}
                onChange={(e) => { setProductSearch(e.target.value); setSelectedProduct(null) }}
                placeholder="Tìm sản phẩm..."
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 text-sm"
              />
              {searchResults.length > 0 && !selectedProduct && (
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg mt-1 overflow-hidden">
                  {searchResults.map((p) => (
                    <button
                      key={p.id} type="button"
                      onClick={() => { setSelectedProduct(p); setProductSearch(p.name) }}
                      className="w-full text-left px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm border-b border-gray-100 dark:border-gray-700 last:border-0"
                    >
                      <p className="line-clamp-1">{p.name}</p>
                      <p className="text-xs text-primary-600">{formatPrice(p.current_price)}</p>
                    </button>
                  ))}
                </div>
              )}
              {selectedProduct && (
                <p className="text-xs text-green-600 mt-1">✓ Đã chọn: {selectedProduct.name.slice(0, 60)}...</p>
              )}
            </div>

            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Loại alert</label>
              <select
                value={form.alert_type}
                onChange={(e) => setForm({ ...form, alert_type: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 text-sm"
              >
                <option value="below">Khi giá dưới mốc</option>
                <option value="above">Khi giá trên mốc</option>
                <option value="any_change">Bất kỳ thay đổi nào</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Giá mục tiêu (VND)</label>
              <input
                type="number" required
                value={form.target_price}
                onChange={(e) => setForm({ ...form, target_price: e.target.value })}
                placeholder="vd: 15000000"
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 text-sm"
              />
            </div>

            <button
              type="submit" disabled={createMutation.isPending}
              className="w-full py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Đang lưu...' : 'Tạo Alert'}
            </button>
          </form>
        </div>
      )}

      {/* Alerts List */}
      {isLoading && <div className="text-center py-8 text-gray-400">Đang tải...</div>}

      {!isLoading && submittedEmail && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-medium">Alerts ({alerts.length})</h2>
          </div>

          {alerts.length === 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center text-gray-400">
              <Bell className="w-8 h-8 mx-auto mb-2 opacity-40" />
              <p>Chưa có alert nào</p>
            </div>
          )}

          {alerts.map((alert) => (
            <div key={alert.id} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 flex items-start gap-3">
              <div className={`p-2 rounded-lg shrink-0 ${alert.is_triggered ? 'bg-green-100 dark:bg-green-900/30' : 'bg-gray-100 dark:bg-gray-700'}`}>
                {alert.is_triggered
                  ? <CheckCircle className="w-4 h-4 text-green-600" />
                  : <Clock className="w-4 h-4 text-gray-500" />
                }
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium line-clamp-1">{alert.product_name || `Sản phẩm #${alert.product_id}`}</p>
                <p className="text-xs text-gray-500">
                  {alert.alert_type === 'below' ? 'Khi giá dưới' : alert.alert_type === 'above' ? 'Khi giá trên' : 'Khi có thay đổi'} {formatPrice(alert.target_price)}
                </p>
                <p className="text-xs text-gray-400">Tạo: {formatDate(alert.created_at)}</p>
              </div>
              <button
                onClick={() => deleteMutation.mutate(alert.id)}
                disabled={deleteMutation.isPending}
                className="p-1.5 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg text-gray-400 hover:text-red-500 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
