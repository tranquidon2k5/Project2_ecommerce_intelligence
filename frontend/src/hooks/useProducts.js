import { useQuery } from '@tanstack/react-query'
import { productService } from '../services/productService'

export function useProducts(params) {
  return useQuery({
    queryKey: ['products', params],
    queryFn: () => productService.search(params),
    placeholderData: (prev) => prev,
  })
}

export function useProduct(id) {
  return useQuery({
    queryKey: ['product', id],
    queryFn: () => productService.getById(id),
    enabled: !!id,
  })
}

export function useProductReviews(id, params) {
  return useQuery({
    queryKey: ['product-reviews', id, params],
    queryFn: () => productService.getReviews(id, params),
    enabled: !!id,
  })
}
