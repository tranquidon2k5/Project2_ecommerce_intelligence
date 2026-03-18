---
name: React Chart
description: How to create a Recharts chart component for price data visualization
---

# React Chart Skill

## When to Use
When you need to create a new chart or graph component for the dashboard.

## Steps

### 1. Create Chart Component

File: `frontend/src/components/charts/<ChartName>.jsx`

#### Area Chart (Price History)

```jsx
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";
import { formatPrice } from "../../utils/formatPrice";

export default function PriceAreaChart({ data, height = 300 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 0 }}>
        <defs>
          <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
        <XAxis dataKey="date" fontSize={12} tickLine={false} />
        <YAxis
          tickFormatter={(val) => formatPrice(val, true)}
          fontSize={12}
          tickLine={false}
          width={80}
        />
        <Tooltip content={<CustomTooltip />} />
        <Area
          type="monotone"
          dataKey="avg"
          stroke="#3B82F6"
          fill="url(#priceGradient)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-lg font-bold text-blue-600">
        {formatPrice(payload[0].value)}
      </p>
    </div>
  );
}
```

#### Bar Chart (Platform Compare)

```jsx
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const PLATFORM_COLORS = {
  shopee: "#EE4D2D",
  tiki: "#1A94FF",
  lazada: "#0F146D",
};

export default function PlatformCompareChart({ data, height = 300 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
        <XAxis dataKey="platform" />
        <YAxis tickFormatter={(val) => formatPrice(val, true)} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="price" radius={[4, 4, 0, 0]}>
          {data.map((entry) => (
            <Cell key={entry.platform} fill={PLATFORM_COLORS[entry.platform] || "#8884d8"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
```

#### Donut Chart (Sentiment)

```jsx
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

const SENTIMENT_COLORS = { positive: "#22C55E", neutral: "#F59E0B", negative: "#EF4444" };

export default function SentimentChart({ data, height = 250 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={80}
          dataKey="value"
          nameKey="name"
          paddingAngle={5}
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={SENTIMENT_COLORS[entry.name] || "#8884d8"} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
```

### 2. Price Prediction Overlay Pattern

Combine historical (solid) + predicted (dashed) lines:

```jsx
<AreaChart data={[...historicalData, ...predictionData]}>
  {/* Historical - solid line */}
  <Area type="monotone" dataKey="actual" stroke="#3B82F6" fill="url(#priceGradient)" strokeWidth={2} />
  {/* Predicted - dashed line */}
  <Area type="monotone" dataKey="predicted" stroke="#F59E0B" fill="none" strokeWidth={2} strokeDasharray="5 5" />
  {/* Confidence band */}
  <Area type="monotone" dataKey="upperBound" stroke="none" fill="#F59E0B" fillOpacity={0.1} />
  <Area type="monotone" dataKey="lowerBound" stroke="none" fill="#F59E0B" fillOpacity={0.1} />
</AreaChart>
```

Data format:
```javascript
// Historical points have `actual`, predicted points have `predicted`
const data = [
  { date: "2025-01-10", actual: 28990000 },
  { date: "2025-01-11", actual: 28800000 },
  // ... transition point
  { date: "2025-01-15", actual: 28500000, predicted: 28500000 },
  // prediction only
  { date: "2025-01-16", predicted: 28300000, upperBound: 28800000, lowerBound: 27800000 },
  { date: "2025-01-17", predicted: 28100000, upperBound: 28700000, lowerBound: 27500000 },
];
```

## VND Price Formatting

Use the shared utility:

```javascript
// frontend/src/utils/formatPrice.js
export function formatPrice(value, compact = false) {
  if (!value && value !== 0) return "N/A";
  if (compact) {
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}tr`;
    if (value >= 1_000) return `${(value / 1_000).toFixed(0)}k`;
  }
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(value);
}
```

## Verify

1. Chart renders without errors in browser
2. Responsive on different screen sizes
3. Tooltip shows correct VND formatted values
4. Dark mode colors are readable
5. Empty state handled when no data
