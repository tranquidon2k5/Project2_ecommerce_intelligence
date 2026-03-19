import { create } from 'zustand'

export const useFilterStore = create((set) => ({
  platform: '',
  categoryId: null,
  minPrice: '',
  maxPrice: '',
  minRating: '',
  sortBy: 'last_crawled_at',
  sortOrder: 'desc',
  setFilter: (key, value) => set({ [key]: value }),
  resetFilters: () => set({
    platform: '', categoryId: null, minPrice: '', maxPrice: '', minRating: '',
    sortBy: 'last_crawled_at', sortOrder: 'desc',
  }),
}))
