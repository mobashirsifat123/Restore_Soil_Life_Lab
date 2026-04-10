export const motion = {
  duration: {
    fast: "140ms",
    base: "220ms",
    slow: "320ms",
    slower: "480ms",
  },
  easing: {
    standard: "cubic-bezier(0.2, 0.0, 0.0, 1)",
    emphasized: "cubic-bezier(0.2, 0.8, 0.2, 1)",
    decelerated: "cubic-bezier(0.05, 0.7, 0.1, 1)",
  },
} as const;
