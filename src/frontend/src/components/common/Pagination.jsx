import { ChevronLeft, ChevronRight } from 'lucide-react'
import clsx from 'clsx'

export default function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) return null

  const pages = []
  const start = Math.max(1, page - 2)
  const end = Math.min(totalPages, page + 2)
  for (let i = start; i <= end; i++) pages.push(i)

  return (
    <div className="flex items-center justify-center gap-1 mt-6">
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-40"
      >
        <ChevronLeft className="w-4 h-4" />
      </button>

      {start > 1 && (
        <>
          <button onClick={() => onPageChange(1)} className="px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-sm">1</button>
          {start > 2 && <span className="px-2 text-gray-400">…</span>}
        </>
      )}

      {pages.map((p) => (
        <button
          key={p}
          onClick={() => onPageChange(p)}
          className={clsx(
            'px-3 py-1.5 rounded-lg text-sm font-medium',
            p === page
              ? 'bg-primary-600 text-white'
              : 'hover:bg-gray-100 dark:hover:bg-gray-700'
          )}
        >
          {p}
        </button>
      ))}

      {end < totalPages && (
        <>
          {end < totalPages - 1 && <span className="px-2 text-gray-400">…</span>}
          <button onClick={() => onPageChange(totalPages)} className="px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-sm">{totalPages}</button>
        </>
      )}

      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-40"
      >
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  )
}
