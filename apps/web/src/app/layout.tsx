import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Playfair_Display } from "next/font/google";
import type { PropsWithChildren } from "react";

import { AppProviders } from "../providers/app-providers";

import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://biosoil.local"),
  title: {
    default: "Bio Soil — Regenerating Soil Through Science",
    template: "%s | Bio Soil",
  },
  description:
    "Bio Soil brings together soil food web science, simulation workflows, and a precision soil health calculator to help farmers and consultants restore biology and increase yields.",
};

export default function RootLayout({ children }: PropsWithChildren) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${playfair.variable} ${jetbrainsMono.variable} site-aura min-h-screen antialiased`}
      >
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
