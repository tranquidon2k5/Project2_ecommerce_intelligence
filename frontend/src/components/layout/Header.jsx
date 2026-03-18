import { Link, useNavigate } from 'react-router-dom'
import { Search, Bell, Moon, Sun, TrendingUp } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Header() {
  const [dark, setDark] = useState(() => localStorage.getItem('theme') === 'dark')
  const [q, setQ] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  const handleSearch = (e) => {
    e.preventDefault()
    if (q.trim()) navigate(`/search?q=${encodeURIComponent(q.trim())}`)
  }

  return (
    <header className="sticky top-0 z-30 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div className="flex items-center gap-4 px-4 h-14">
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <TrendingUp className="w-6 h-6 text-primary-600" />
          <span className="font-bold text-lg text-primary-700 dark:text-primary-400">ShopSmart</span>
        </Link>

        <form onSubmit={handleSearch} className="flex-1 max-w-xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Tìm sản phẩm..."
              className="w-full pl-9 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </form>

        <nav className="hidden md:flex items-center gap-1 text-sm">
          <Link to="/" className="px-3 py-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700">Dashboard</Link>
          <Link to="/trending" className="px-3 py-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700">Trending</Link>
          <Link to="/compare" className="px-3 py-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700">So sánh</Link>
          <Link to="/alerts" className="px-3 py-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-1">
            <Bell className="w-4 h-4" /> Alerts
          </Link>
        </nav>

        <button
          onClick={() => setDark(!dark)}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>
    </header>
  )
}
