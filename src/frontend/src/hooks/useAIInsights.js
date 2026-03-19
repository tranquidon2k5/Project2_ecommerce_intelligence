import { useQuery } from '@tanstack/react-query'
import { aiService } from '../services/aiService'

export function usePricePrediction(productId, days = 7) {
  return useQuery({
    queryKey: ['ai', 'predict-price', productId, days],
    queryFn: () => aiService.predictPrice(productId, days),
    enabled: !!productId,
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}

export function useAnomalies(limit = 20) {
  return useQuery({
    queryKey: ['ai', 'anomalies', limit],
    queryFn: () => aiService.getAnomalies(limit),
    staleTime: 1000 * 60 * 5,
  })
}
