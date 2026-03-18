import { Star } from 'lucide-react'

export default function RatingStars({ rating, count, size = 'sm' }) {
  const stars = Math.round(rating || 0)
  const iconSize = size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'

  return (
    <div className="flex items-center gap-1">
      <div className="flex">
        {[1, 2, 3, 4, 5].map((i) => (
          <Star
            key={i}
            className={`${iconSize} ${i <= stars ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300 dark:text-gray-600'}`}
          />
        ))}
      </div>
      {count != null && (
        <span className="text-xs text-gray-500 dark:text-gray-400">({count.toLocaleString()})</span>
      )}
    </div>
  )
}
