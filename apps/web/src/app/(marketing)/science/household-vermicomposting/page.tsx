import type { Metadata } from "next";
import { ScienceArticleReader } from "@/components/science/science-article-reader";

export const metadata: Metadata = {
  title: "Turning Waste into Life: Household Vermicomposting | Bio Soil Science",
};

export default function VermicompostingArticle() {
  return (
    <ScienceArticleReader
      title="Turning Waste into Life: Household Vermicomposting"
      kicker="Practice Guide"
      excerpt="Every kitchen generates soil gold. This guide explains how household vermicomposting turns organic scraps into biologically active compost."
      published="October 25, 2025"
      readTime="7 min read"
      pageImageBase="/articles/rendered/household-vermicomposting"
      pageCount={6}
    />
  );
}
