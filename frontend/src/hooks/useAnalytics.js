import { useQuery } from '@tanstack/react-query'
import { analyticsService } from '../services/analyticsService'

export function useMarketOverview() {
  return useQuery({
    queryKey: ['market-overview'],
    queryFn: () => analyticsService.getMarketOverview(),
    staleTime: 60_000,
  })
}

export function useTrending(params) {
  return useQuery({
    queryKey: ['trending', params],
    queryFn: () => analyticsService.getTrending(params),
    staleTime: 300_000,
    refetchInterval: 300_000,
  })
}

export function usePriceComparison(q) {
  return useQuery({
    queryKey: ['price-comparison', q],
    queryFn: () => analyticsService.getPriceComparison({ q }),
    enabled: !!q && q.length >= 2,
  })
}
