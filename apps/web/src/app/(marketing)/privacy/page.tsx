import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Bio Soil privacy policy.",
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-[#f5efdf]">
      <section className="bg-dark-earth py-16 px-6 text-center">
        <h1 className="font-serif text-[2.8rem] text-white">Privacy Policy</h1>
      </section>
      <section className="py-16 px-6">
        <div className="mx-auto max-w-[800px] prose prose-stone">
          <h2 className="font-serif text-2xl text-[#1e3318] mb-4">Your Privacy Matters</h2>
          <p className="text-[#4a5e40] leading-8 mb-4">
            Bio Soil is committed to protecting your personal data. This policy explains how we
            collect, use, and safeguard your information.
          </p>
          <p className="text-[#4a5e40] leading-8 mb-4">
            We collect only the data necessary to provide our services — including account
            information, soil analysis inputs, and usage analytics. We never sell your personal data
            to third parties.
          </p>
          <p className="text-[#4a5e40] leading-8">
            For questions, contact us at{" "}
            <a href="mailto:privacy@biosoil.com" className="text-[#3a5c2f] underline">
              privacy@biosoil.com
            </a>
            .
          </p>
        </div>
      </section>
    </div>
  );
}
