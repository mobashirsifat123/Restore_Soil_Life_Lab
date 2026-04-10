import type { BlogPostDetail, BlogPostSummary } from "./cmsTypes";

export type MarketingBlogPost = {
  slug: string;
  category: string;
  title: string;
  excerpt: string;
  date: string;
  readTimeMinutes: number;
  author: string;
  bodyMarkdown?: string;
};

export const FALLBACK_MARKETING_POSTS: MarketingBlogPost[] = [
  {
    slug: "mycorrhizal-fungi-nutrient-cycling",
    category: "Science",
    title: "How Mycorrhizal Fungi Networks Drive Nutrient Cycling",
    excerpt:
      "Underground fungal highways transport nutrients between plants and microorganisms in ways that still astonish soil scientists today.",
    date: "2026-04-03",
    readTimeMinutes: 6,
    author: "Dr. Sarah Greenfield",
    bodyMarkdown:
      "# Fungal Networks in Living Soil\n\nMycorrhizal fungi create underground exchange channels that connect roots and microbial communities.\n\nThese networks support nutrient movement, moisture balance, and plant signaling in ways synthetic inputs cannot replicate.",
  },
  {
    slug: "pakistani-farm-soil-restored",
    category: "Case Studies",
    title: "Pakistani Farm Soil Restored in One Season with Bio Approach",
    excerpt:
      "Wild Soils UK and TrashIt demonstrate how the soil food web approach transformed degraded farmland in Pakistan, achieving a 120% yield increase.",
    date: "2026-03-28",
    readTimeMinutes: 8,
    author: "Marcus Chen",
    bodyMarkdown:
      "# One-Season Regeneration\n\nThe case showed major gains in biological activity and yield after a focused restoration protocol.\n\nMeasured outcomes improved where root-zone biology, organic matter, and moisture dynamics were rebuilt together.",
  },
  {
    slug: "silksoil-microbiome-scoring",
    category: "Updates",
    title: "SilkSoil: New Microbiome Scoring Module Released",
    excerpt:
      "Our latest calculator update adds fungal-to-bacterial ratio scoring and a predictive yield improvement estimate based on 5 years of field data.",
    date: "2026-03-20",
    readTimeMinutes: 4,
    author: "Bio Soil Team",
    bodyMarkdown:
      "# SilkSoil Update\n\nThe new release adds clearer microbial balance scoring and stronger interpretation support.\n\nGrowers can now understand biology trends faster and map them to practical field actions.",
  },
  {
    slug: "carbon-sequestration-biological-restoration",
    category: "Science",
    title: "Carbon Sequestration Through Biological Soil Restoration",
    excerpt:
      "New research confirms that restoring the soil food web can sequester carbon at rates that could meaningfully reverse atmospheric CO2 levels.",
    date: "2026-03-10",
    readTimeMinutes: 9,
    author: "Dr. Amara Diallo",
    bodyMarkdown:
      "# Carbon Through Biology\n\nBiologically active soils stabilize carbon by increasing root exudates and durable organic compounds.\n\nThis approach supports both climate outcomes and long-term farm resilience.",
  },
  {
    slug: "soil-food-web-webinar-series",
    category: "Events",
    title: "Free Webinar Series: A Living Legacy - The Science of the Soil Food Web",
    excerpt:
      "Join us for a 6-part free webinar series exploring the foundational science behind the soil food web approach, from bacteria to food chains.",
    date: "2026-02-28",
    readTimeMinutes: 3,
    author: "Bio Soil Team",
    bodyMarkdown:
      "# Webinar Series\n\nThis series covers the practical science behind regenerative soil biology.\n\nEach session translates core mechanisms into decisions growers can apply quickly.",
  },
  {
    slug: "bio-soil-certified-consultants-q1-2026",
    category: "Community",
    title: "Bio Soil Welcomes 500 New Certified Consultants in Q1 2026",
    excerpt:
      "Our community of certified soil consultants grew by 500 members this quarter, now spanning 48 countries on 6 continents.",
    date: "2026-02-15",
    readTimeMinutes: 3,
    author: "Bio Soil Team",
    bodyMarkdown:
      "# Global Community Growth\n\nThe network of certified consultants expanded across diverse climates and production systems.\n\nThis broadens local support capacity for farmers adopting biology-first practices.",
  },
];

export function dateLabel(dateValue?: string | null) {
  if (!dateValue) {
    return "Recently";
  }
  const parsed = new Date(dateValue);
  if (Number.isNaN(parsed.getTime())) {
    return dateValue;
  }
  return parsed.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
}

export function normalizeBlogSummary(post: BlogPostSummary): MarketingBlogPost {
  return {
    slug: post.slug || post.id,
    category: post.category || "Updates",
    title: post.title,
    excerpt: post.excerpt ?? "Read the latest update from the Bio Soil team.",
    date: post.published_at ?? post.updated_at ?? post.created_at,
    readTimeMinutes: post.read_time_minutes ?? 5,
    author: post.author ?? "Bio Soil Team",
  };
}

export function normalizeBlogDetail(post: BlogPostDetail): MarketingBlogPost {
  return {
    ...normalizeBlogSummary(post),
    bodyMarkdown: post.body_markdown ?? undefined,
  };
}
