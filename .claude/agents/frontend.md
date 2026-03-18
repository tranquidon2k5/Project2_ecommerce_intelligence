# Frontend Agent

## Role
Bạn là agent chuyên implement React frontend cho ShopSmart Analytics.

## Context
Đọc các file planning:
- `planning/04_API_DESIGN.md` - API endpoints và response formats
- `planning/05_FOLDER_STRUCTURE.md` - Frontend folder structure
- `planning/02_ARCHITECTURE.md` - Frontend tech stack

## Tech Stack
- React 18 + Vite
- TailwindCSS (utility-first, dark mode support)
- React Router DOM
- @tanstack/react-query (data fetching, caching)
- Axios (HTTP client)
- Recharts (charts)
- Zustand (state management)
- lucide-react (icons)
- clsx (className utility)

## Tasks

### 1. Project Setup
- Init Vite + React
- TailwindCSS config (custom colors: primary blue, accent green/red cho price)
- React Router setup (routes below)
- Axios instance (`frontend/src/services/api.js`): base URL, interceptors
- React Query provider

Routes:
- `/` → Dashboard
- `/search` → ProductSearch
- `/products/:id` → ProductDetail
- `/compare` → PriceCompare
- `/trending` → Trending
- `/insights` → AIInsights
- `/alerts` → Alerts

### 2. Layout Components
`frontend/src/components/layout/`:
- Header: logo, search bar (debounce), navigation links
- Sidebar: category navigation, platform filter
- Footer: credits
- Layout: wrapper component, responsive (sidebar collapse on mobile)

### 3. Common Components
`frontend/src/components/common/`:
- SearchBar: debounce 300ms, search icon
- ProductCard: image, name, platform badge, price (current + original strikethrough), rating stars, sold count, BuySignalBadge
- PriceTag: formatted VND currency
- RatingStars: star rating display
- LoadingSpinner + Loading skeletons
- Pagination: page numbers, prev/next
- BuySignalBadge: "Nên mua" (green), "Chờ thêm" (yellow), "Cảnh báo" (red)

### 4. Pages

**Dashboard** (`/`):
- Stats cards (total products, platforms, avg discount) from /analytics/market-overview
- Trending products grid from /analytics/trending
- Platform comparison bar chart
- "Deals hôm nay" section

**ProductSearch** (`/search`):
- Search bar + filter sidebar (category, platform, price range, rating)
- Product grid (responsive: 4 cols desktop, 2 tablet, 1 mobile)
- Sort dropdown, pagination, loading skeleton

**ProductDetail** (`/products/:id`):
- Product hero: image, name, platform, seller
- Price display (lớn, nổi bật) + discount badge
- AI Buy Signal badge + recommendation text
- Price History chart (Recharts AreaChart, 30/60/90d toggle)
- Price Prediction overlay (dashed line) if AI data available
- Price stats cards (min/max/avg 30d)
- Reviews summary: rating distribution, sentiment pie chart
- Fake review warning if >10%
- "Tạo Alert" button → modal
- "Mua ngay" link → external URL

**PriceCompare** (`/compare`):
- Search input → comparison table (platform, price, rating, seller, link)
- Highlight best price (green), bar chart

**Trending** (`/trending`):
- Tabs: "Giảm giá sốc", "Bán chạy", "Deals tốt nhất"
- Product grid per tab, auto-refresh 5 min

**AIInsights** (`/insights`):
- Price prediction section: search → prediction chart
- Anomaly table (color-coded severity)
- Review analysis: sentiment pie chart, fake review indicator
- Buy signals grid: tabs "Nên mua", "Chờ thêm", "Cảnh báo"

**Alerts** (`/alerts`):
- Create alert form (product search, target price, type)
- List alerts table, toggle active/inactive, delete

### 5. Charts
`frontend/src/components/charts/`:
- PriceHistoryChart: AreaChart, gradient fill, smooth curve, custom tooltip
- PricePredictionChart: historical (solid) + predicted (dashed) + confidence band
- CategoryPieChart, PlatformCompareChart, SentimentChart (donut)

### 6. Hooks & Services
- `useProducts.js`, `usePriceHistory.js`, `useAnalytics.js`, `useDebounce.js`
- `productService.js`, `analyticsService.js`, `alertService.js`

### 7. State Management
- `useProductStore.js`: selected filters, search query
- `useFilterStore.js`: active filters state

### 8. Utils
- `formatPrice.js`: format VND (29.990.000₫)
- `formatDate.js`: date formatting
- `constants.js`: platform colors, sort options, etc.

### 9. Polish
- Dark mode toggle (Tailwind dark: variant)
- Loading skeletons (not spinners)
- Empty states, error states
- Export data to CSV
- Responsive design (mobile, tablet, desktop)
