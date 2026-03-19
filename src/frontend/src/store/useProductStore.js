import { create } from 'zustand'

export const useProductStore = create((set) => ({
  searchQuery: '',
  setSearchQuery: (q) => set({ searchQuery: q }),
  selectedProduct: null,
  setSelectedProduct: (p) => set({ selectedProduct: p }),
}))
