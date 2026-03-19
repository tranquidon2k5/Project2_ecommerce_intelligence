import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Search, TrendingUp, BarChart2, Bell } from 'lucide-react'
import clsx from 'clsx'

const NAV_ITEMS = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', end: true },
  { to: '/search', icon: Search, label: 'Tìm kiếm' },
  { to: '/trending', icon: TrendingUp, label: 'Trending' },
  { to: '/compare', icon: BarChart2, label: 'So sánh giá' },
  { to: '/alerts', icon: Bell, label: 'Price Alerts' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 hidden lg:block border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 min-h-full">
      <nav className="p-3 space-y-1">
        {NAV_ITEMS.map(({ to, icon: Icon, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => clsx(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              isActive
                ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
