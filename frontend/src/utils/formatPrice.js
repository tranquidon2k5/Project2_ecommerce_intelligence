export function formatPrice(price) {
  if (price == null) return '—'
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(price)
}

export function formatPriceShort(price) {
  if (price == null) return '—'
  if (price >= 1_000_000) return `${(price / 1_000_000).toFixed(1)}tr₫`
  if (price >= 1_000) return `${(price / 1_000).toFixed(0)}k₫`
  return `${price}₫`
}
