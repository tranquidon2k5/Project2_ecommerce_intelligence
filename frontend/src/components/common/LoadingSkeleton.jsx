export function CardSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 animate-pulse">
      <div className="h-40 bg-gray-200 dark:bg-gray-700 rounded-lg mb-3" />
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2 w-3/4" />
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2 w-1/2" />
      <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
    </div>
  )
}

export function StatSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 animate-pulse">
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-3 w-1/2" />
      <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-2/3" />
    </div>
  )
}

export function TableRowSkeleton({ cols = 4 }) {
  return (
    <tr className="animate-pulse">
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
        </td>
      ))}
    </tr>
  )
}
