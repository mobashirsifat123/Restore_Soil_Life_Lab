import type { Metadata } from "next";
import { ScienceArticleReader } from "@/components/science/science-article-reader";

export const metadata: Metadata = {
  title: "From Kitchen Scraps to Soil Gold | Bio Soil Science",
};

export default function SeedlingArticle() {
  return (
    <ScienceArticleReader
      title="From Kitchen Scraps to Soil Gold"
      kicker="Home Practice"
      excerpt="A seedling growing from dark organic soil tells a story of regeneration. Use the article to set up your first worm bin and build living soil at home."
      published="October 25, 2025"
      readTime="6 min read"
      pageImageBase="/articles/rendered/soil-organic-matter-seedling"
      pageCount={6}
    />
  );
}
