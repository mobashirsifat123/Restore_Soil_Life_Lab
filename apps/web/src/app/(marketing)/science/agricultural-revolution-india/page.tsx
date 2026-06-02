import type { Metadata } from "next";
import { ScienceArticleReader } from "@/components/science/science-article-reader";

export const metadata: Metadata = {
  title: "An Agricultural Revolution Is Unfolding in India | Bio Soil Science",
};

export default function IndiaRevolutionArticle() {
  return (
    <ScienceArticleReader
      title="An Agricultural Revolution Is Unfolding in India"
      kicker="Case Study"
      excerpt="How Andhra Pradesh's APCNF program reached hundreds of thousands of farming households by working with nature instead of against it."
      published="August 21, 2025"
      readTime="8 min read"
      pageImageBase="/articles/rendered/agricultural-revolution-india"
      pageCount={5}
    />
  );
}
