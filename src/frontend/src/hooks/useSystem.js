import { useQuery } from '@tanstack/react-query'
import { systemService } from '../services/systemService'

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => systemService.getHealth(),
    refetchInterval: 30000,
  })
}

export function useSystemStats() {
  return useQuery({
    queryKey: ['system-stats'],
    queryFn: () => systemService.getSystemStats(),
    refetchInterval: 30000,
  })
}

export function useCrawlLogs() {
  return useQuery({
    queryKey: ['crawl-logs'],
    queryFn: () => systemService.getCrawlLogs(),
    refetchInterval: 30000,
  })
}
