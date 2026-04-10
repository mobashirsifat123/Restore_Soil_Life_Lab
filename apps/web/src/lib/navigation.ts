export const marketingNavigation = [
  { href: "/", label: "Home", exact: true },
  { href: "/about", label: "About", exact: true },
  { href: "/silksoil", label: "SilkSoil", exact: true },
  {
    href: "/science",
    label: "Science",
    exact: false,
    children: [
      { href: "/science/soil-food-web", label: "How it Works" },
      { href: "/science/nutrient-cycling", label: "Nutrient Cycling" },
      { href: "/science/carbon-sequestration", label: "Carbon Sequestration" },
    ],
  },
  { href: "/blog", label: "Blog", exact: false },
  { href: "/contact", label: "Contact", exact: false },
] as const;

export const platformNavigation = [
  { href: "/dashboard", label: "Home", exact: true },
  { href: "/silksoil", label: "SilkSoil", exact: true },
  { href: "/projects", label: "Projects", exact: false },
  { href: "/runs", label: "Runs", exact: false },
  { href: "/settings", label: "Settings", exact: true },
  { href: "/", label: "Public Site", exact: true },
] as const;
