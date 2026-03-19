import { useQuery } from '@tanstack/react-query'
import { productService } from '../services/productService'

export function usePriceHistory(productId, period = '30d') {
  return useQuery({
    queryKey: ['price-history', productId, period],
    queryFn: () => productService.getPriceHistory(productId, { period }),
    enabled: !!productId,
  })
}
