import { create } from 'zustand';

interface ScrollState {
  progress: number;
  setProgress: (progress: number) => void;
}

export const useScrollStore = create<ScrollState>((set) => ({
  progress: 0,
  setProgress: (progress) => set({ progress }),
}));
