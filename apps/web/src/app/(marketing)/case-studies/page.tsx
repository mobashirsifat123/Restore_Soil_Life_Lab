import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Case Studies",
  description: "Real-world results from Bio Soil's soil food web approach across six continents.",
};

export default function CaseStudiesPage() {
  return (
    <div className="min-h-screen bg-[#f5efdf]">
      <section className="content-auto bg-dark-earth px-6 py-20 text-center">
        <div className="mx-auto max-w-[700px]">
          <p className="editorial-kicker text-[#a8cc8a] mb-4">Proven in the field</p>
          <h1 className="font-serif text-[3rem] md:text-[4rem] text-white leading-tight tracking-[-0.04em] mb-5">
            Case Studies
          </h1>
          <p className="text-[#9ab88a] text-lg leading-8">
            Real results from farms and restoration projects across 6 continents using the Bio Soil
            approach.
          </p>
        </div>
      </section>
      <section className="content-auto px-6 py-20 text-center">
        <div className="mx-auto max-w-[600px]">
          <p className="font-serif text-2xl text-[#1e3318] mb-4">Case studies coming soon</p>
          <p className="text-[#5a6e50] leading-7 mb-8">
            We are compiling detailed case studies from our global community. In the meantime,
            explore the science or calculate your soil health.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/science"
              className="button-glow rounded-full bg-[#3a5c2f] px-6 py-3.5 font-semibold text-white hover:bg-[#1e3318] transition-colors"
            >
              Read the Science
            </Link>
            <Link
              href="/silksoil"
              className="button-glow rounded-full border border-[rgba(58,92,47,0.2)] px-6 py-3.5 font-semibold text-[#3a5c2f] hover:bg-[rgba(58,92,47,0.06)] transition-colors"
            >
              Free Soil Health Calculator
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
