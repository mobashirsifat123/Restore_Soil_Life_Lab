import type { Metadata } from "next";
import { ScienceArticleReader } from "@/components/science/science-article-reader";

export const metadata: Metadata = {
  title: "From China to Brazil: Two Paths, One Wisdom | Bio Soil Science",
};

export default function ChinaBrazilArticle() {
  return (
    <ScienceArticleReader
      title="From China to Brazil: Two Paths, One Wisdom"
      kicker="Comparative Study"
      excerpt="Chinese soil scientist Guangjiong Hou and Swiss agroforester Ernst Goetsch worked in different contexts but arrived at the same biological principle: cooperate with nature."
      published="August 29, 2025"
      readTime="10 min read"
      pageImageBase="/articles/rendered/china-brazil-two-paths"
      pageCount={7}
    />
  );
}
