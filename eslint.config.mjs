import js from "@eslint/js";
import nextPlugin from "@next/eslint-plugin-next";
import reactHooksPlugin from "eslint-plugin-react-hooks";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: [
      "**/.next/**",
      "**/.turbo/**",
      "**/coverage/**",
      "**/dist/**",
      "**/node_modules/**",
      "**/.pnpm-store/**",
      "**/*.d.ts",
      "infra/terraform/**",
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{js,mjs,cjs,ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: {
        ...globals.node,
      },
    },
  },
  {
    files: ["apps/web/**/*.{ts,tsx}"],
    plugins: {
      "@next/next": nextPlugin,
      "react-hooks": reactHooksPlugin,
    },
    settings: {
      next: {
        rootDir: ["apps/web/"],
      },
    },
    rules: {
      ...nextPlugin.configs.recommended.rules,
      ...nextPlugin.configs["core-web-vitals"].rules,
    },
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
  },
);
