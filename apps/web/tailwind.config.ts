import type { Config } from "tailwindcss";

import { contentWidth, scientificTailwindTheme } from "@bio/design-tokens";

const extendedTheme = {
  ...scientificTailwindTheme,
  fontFamily: {
    editorial: [...scientificTailwindTheme.fontFamily.editorial],
    serif: [...scientificTailwindTheme.fontFamily.editorial],
    sans: [...scientificTailwindTheme.fontFamily.sans],
    mono: [...scientificTailwindTheme.fontFamily.mono],
  },
  maxWidth: contentWidth,
} as unknown as NonNullable<Config["theme"]>["extend"];

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}", "../../packages/ui/src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: extendedTheme,
  },
  plugins: [],
};

export default config;
