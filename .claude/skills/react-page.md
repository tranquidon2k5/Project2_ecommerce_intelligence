---
name: React Page
description: How to create a new React page with hooks, services, routing, and TailwindCSS
---

# React Page Skill

## When to Use
When you need to add a new page to the ShopSmart Analytics frontend.

## Steps

### 1. Create Page Component

File: `frontend/src/pages/<PageName>.jsx`

```jsx
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchItems } from "../services/<domain>Service";
import ProductCard from "../components/common/ProductCard";
import LoadingSpinner from "../components/common/LoadingSpinner";
import Pagination from "../components/common/Pagination";

export default function PageName() {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({});

  const { data, isLoading, error } = useQuery({
    queryKey: ["items", page, filters],
    queryFn: () => fetchItems({ page, ...filters }),
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <div className="text-red-500">Error: {error.message}</div>;

  const { data: items, meta } = data;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        Page Title
      </h1>

      {/* Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {items.map((item) => (
          <ProductCard key={item.id} product={item} />
        ))}
      </div>

      {/* Empty State */}
      {items.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          Không tìm thấy kết quả
        </div>
      )}

      {/* Pagination */}
      {meta && (
        <Pagination
          currentPage={meta.page}
          totalPages={meta.total_pages}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
```

### 2. Create API Service

File: `frontend/src/services/<domain>Service.js`

```javascript
import api from "./api"; // Axios instance

export const fetchItems = async (params = {}) => {
  const { data } = await api.get("/api/v1/<domain>", { params });
  return data; // { success, data, meta, message }
};

export const fetchItemById = async (id) => {
  const { data } = await api.get(`/api/v1/<domain>/${id}`);
  return data;
};
```

### 3. Create React Query Hook

File: `frontend/src/hooks/use<Domain>.js`

```javascript
import { useQuery } from "@tanstack/react-query";
import { fetchItems, fetchItemById } from "../services/<domain>Service";

export function useItems(params) {
  return useQuery({
    queryKey: ["items", params],
    queryFn: () => fetchItems(params),
    staleTime: 5 * 60 * 1000, // 5 min
  });
}

export function useItem(id) {
  return useQuery({
    queryKey: ["item", id],
    queryFn: () => fetchItemById(id),
    enabled: !!id,
  });
}
```

### 4. Add Route

File: `frontend/src/App.jsx`

```jsx
import PageName from "./pages/PageName";

// Inside <Routes>:
<Route path="/new-page" element={<PageName />} />
```

### 5. Add Navigation Link

File: `frontend/src/components/layout/Sidebar.jsx` or `Header.jsx`

```jsx
<NavLink to="/new-page" className={({ isActive }) =>
  clsx("px-4 py-2 rounded-lg", isActive ? "bg-blue-100 text-blue-700" : "text-gray-600 hover:bg-gray-100")
}>
  New Page
</NavLink>
```

### 6. Add Zustand Store (if needed)

File: `frontend/src/store/use<Domain>Store.js`

```javascript
import { create } from "zustand";

const useDomainStore = create((set) => ({
  selectedFilter: null,
  setSelectedFilter: (filter) => set({ selectedFilter: filter }),
  reset: () => set({ selectedFilter: null }),
}));

export default useDomainStore;
```

## Styling Conventions

- Use **TailwindCSS** utility classes exclusively
- Support **dark mode**: always add `dark:` variants for colors
  - Background: `bg-white dark:bg-gray-800`
  - Text: `text-gray-900 dark:text-white`
  - Border: `border-gray-200 dark:border-gray-700`
- Responsive grid: `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`
- VND price formatting: use `formatPrice()` from `utils/formatPrice.js`

## Verify

1. Run `npm run dev` in `frontend/`
2. Navigate to the new route
3. Check responsive design on mobile/tablet/desktop
4. Check dark mode toggle works
5. Verify API data loads correctly
