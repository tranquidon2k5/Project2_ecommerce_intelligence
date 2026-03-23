import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import ProductSearch from './pages/ProductSearch'
import ProductDetail from './pages/ProductDetail'
import PriceCompare from './pages/PriceCompare'
import Trending from './pages/Trending'
import Alerts from './pages/Alerts'
import AIInsights from './pages/AIInsights'
import SystemStatus from './pages/SystemStatus'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="search" element={<ProductSearch />} />
        <Route path="products/:id" element={<ProductDetail />} />
        <Route path="compare" element={<PriceCompare />} />
        <Route path="trending" element={<Trending />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="insights" element={<AIInsights />} />
        <Route path="system" element={<SystemStatus />} />
      </Route>
    </Routes>
  )
}
