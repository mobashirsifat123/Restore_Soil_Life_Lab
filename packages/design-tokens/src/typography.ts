export const fontFamily = {
  editorial: ['"Playfair Display"', "Georgia", "serif"],
  sans: ['"Inter"', '"Segoe UI"', "system-ui", "sans-serif"],
  mono: ['"JetBrains Mono"', '"SFMono-Regular"', "ui-monospace", "monospace"],
} as const;

export const fontSize = {
  display: ["4.5rem", { lineHeight: "4.75rem", letterSpacing: "-0.04em", fontWeight: "500" }],
  hero: ["3.5rem", { lineHeight: "3.9rem", letterSpacing: "-0.035em", fontWeight: "500" }],
  h1: ["2.75rem", { lineHeight: "3rem", letterSpacing: "-0.03em", fontWeight: "600" }],
  h2: ["2rem", { lineHeight: "2.35rem", letterSpacing: "-0.02em", fontWeight: "600" }],
  h3: ["1.5rem", { lineHeight: "1.9rem", letterSpacing: "-0.015em", fontWeight: "600" }],
  title: ["1.125rem", { lineHeight: "1.6rem", letterSpacing: "-0.01em", fontWeight: "600" }],
  body: ["1rem", { lineHeight: "1.65rem", letterSpacing: "-0.005em", fontWeight: "400" }],
  bodySm: ["0.9375rem", { lineHeight: "1.45rem", letterSpacing: "-0.003em", fontWeight: "400" }],
  label: ["0.8125rem", { lineHeight: "1.1rem", letterSpacing: "0.04em", fontWeight: "600" }],
  caption: ["0.75rem", { lineHeight: "1rem", letterSpacing: "0.02em", fontWeight: "500" }],
  numeric: ["0.875rem", { lineHeight: "1.25rem", letterSpacing: "0em", fontWeight: "500" }],
} as const;

export const fontWeight = {
  regular: "400",
  medium: "500",
  semibold: "600",
  bold: "700",
} as const;
