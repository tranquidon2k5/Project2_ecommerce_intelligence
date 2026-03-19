import { formatPrice } from '../../utils/formatPrice'

export default function PriceTag({ price, originalPrice, discountPercent, size = 'md' }) {
  const sizeClasses = {
    sm: 'text-base',
    md: 'text-lg',
    lg: 'text-2xl',
  }

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className={`font-bold text-red-600 dark:text-red-400 ${sizeClasses[size]}`}>
        {formatPrice(price)}
      </span>
      {originalPrice && originalPrice > price && (
        <span className="text-sm text-gray-400 line-through">{formatPrice(originalPrice)}</span>
      )}
      {discountPercent && (
        <span className="text-xs bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300 px-1.5 py-0.5 rounded font-medium">
          -{Math.round(discountPercent)}%
        </span>
      )}
    </div>
  )
}
