import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms & Conditions",
  description: "Bio Soil terms and conditions.",
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-[#f5efdf]">
      <section className="bg-dark-earth py-16 px-6 text-center">
        <h1 className="font-serif text-[2.8rem] text-white">Terms & Conditions</h1>
      </section>
      <section className="py-16 px-6">
        <div className="mx-auto max-w-[800px]">
          <h2 className="font-serif text-2xl text-[#1e3318] mb-4">Use of Bio Soil Services</h2>
          <p className="text-[#4a5e40] leading-8 mb-4">
            By using Bio Soil, you agree to use our platform for lawful purposes only and in a way
            that does not infringe the rights of others. Our tools are provided for educational and
            analytical purposes.
          </p>
          <p className="text-[#4a5e40] leading-8 mb-4">
            Soil Health Calculator results are indicative only and should not replace professional
            soil laboratory analysis for commercial decisions.
          </p>
          <p className="text-[#4a5e40] leading-8">
            For questions, contact us at{" "}
            <a href="mailto:legal@biosoil.com" className="text-[#3a5c2f] underline">
              legal@biosoil.com
            </a>
            .
          </p>
        </div>
      </section>
    </div>
  );
}
