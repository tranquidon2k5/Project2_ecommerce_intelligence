import { Link } from 'react-router-dom'
import { ShoppingBag } from 'lucide-react'
import PriceTag from './PriceTag'
import RatingStars from './RatingStars'
import BuySignalBadge from './BuySignalBadge'
import { PLATFORM_COLORS, PLATFORM_LABELS } from '../../utils/constants'

export default function ProductCard({ product }) {
  const { id, name, platform, current_price, original_price, discount_percent,
    rating_avg, rating_count, total_sold, image_url, buy_signal } = product

  return (
    <Link to={`/products/${id}`} className="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-md transition-shadow flex flex-col">
      <div className="relative aspect-square bg-gray-100 dark:bg-gray-700">
        {image_url ? (
          <img
            src={image_url}
            alt={name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <ShoppingBag className="w-10 h-10 text-gray-400" />
          </div>
        )}
        {discount_percent && (
          <span className="absolute top-2 left-2 bg-red-500 text-white text-xs font-bold px-1.5 py-0.5 rounded">
            -{Math.round(discount_percent)}%
          </span>
        )}
        <span
          className="absolute top-2 right-2 text-white text-xs font-bold px-1.5 py-0.5 rounded"
          style={{ backgroundColor: PLATFORM_COLORS[platform] || '#666' }}
        >
          {PLATFORM_LABELS[platform] || platform}
        </span>
      </div>

      <div className="p-3 flex-1 flex flex-col gap-1.5">
        <p className="text-sm font-medium line-clamp-2 leading-snug">{name}</p>
        <PriceTag price={current_price} originalPrice={original_price} size="sm" />
        {rating_avg && <RatingStars rating={rating_avg} count={rating_count} />}
        {total_sold > 0 && (
          <p className="text-xs text-gray-500 dark:text-gray-400">Đã bán {total_sold.toLocaleString()}</p>
        )}
        {buy_signal && <BuySignalBadge signal={buy_signal} />}
      </div>
    </Link>
  )
}
