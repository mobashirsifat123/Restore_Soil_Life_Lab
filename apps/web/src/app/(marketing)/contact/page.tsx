"use client";

import Link from "next/link";
import { useState } from "react";

export default function ContactPage() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [status, setStatus] = useState<"idle" | "prepared">("idle");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) {
      return;
    }

    const subject = `[Bio Soil] ${form.subject}`;
    const body = `Name: ${form.name}\nEmail: ${form.email}\n\n${form.message}`;

    setSubmitting(true);
    setError(null);

    try {
      if (typeof window !== "undefined") {
        window.location.href = `mailto:info@biosoil.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      }
      setStatus("prepared");
    } catch {
      setError("We could not open your mail app. Please email info@biosoil.com directly.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f5efdf]">
      {/* Hero */}
      <section className="content-auto bg-dark-earth px-6 py-20">
        <div className="mx-auto max-w-[700px] text-center">
          <p className="editorial-kicker text-[#a8cc8a] mb-4">We&apos;re here to help</p>
          <h1 className="font-serif text-[3rem] md:text-[4rem] text-white leading-tight tracking-[-0.04em] mb-5">
            Contact Us
          </h1>
          <p className="text-[#9ab88a] text-lg leading-8">
            Have a question about soil health, our tools, or partnerships? Send us a message and
            we&apos;ll get back to you within one business day.
          </p>
        </div>
      </section>

      {/* Contact grid */}
      <section className="content-auto px-6 py-20">
        <div className="mx-auto max-w-[1100px] grid lg:grid-cols-[2fr_1fr] gap-12">
          {/* Form */}
          <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-8 md:p-10 shadow-sm">
            {status === "prepared" ? (
              <div className="text-center py-12">
                <div className="text-5xl mb-6">🌱</div>
                <h2 className="font-serif text-2xl text-[#1e3318] mb-3">Your message is ready</h2>
                <p className="text-[#5a6e50] leading-7">
                  We opened your default mail app with the message prefilled for{" "}
                  <span className="font-semibold text-[#1e3318]">info@biosoil.com</span>. Send it
                  there and our team will reply within one business day.
                </p>
                <button
                  onClick={() => {
                    setForm({ name: "", email: "", subject: "", message: "" });
                    setStatus("idle");
                  }}
                  className="mt-8 rounded-full bg-[#3a5c2f] px-7 py-3.5 text-sm font-semibold text-white hover:bg-[#1e3318] transition-colors"
                >
                  Prepare Another Message
                </button>
              </div>
            ) : (
              <>
                <h2 className="font-serif text-2xl text-[#1e3318] mb-2">Send a Message</h2>
                <p className="text-sm text-[#6a8060] mb-8">
                  All fields are required. We&apos;ll open your mail app with everything filled in.
                </p>
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div className="grid sm:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#4a5e40] mb-1.5">
                        Your Name
                      </label>
                      <input
                        type="text"
                        required
                        autoComplete="name"
                        value={form.name}
                        onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                        className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] bg-white px-4 py-3 text-[#1e3318] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30 focus:border-[#3a5c2f] transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#4a5e40] mb-1.5">
                        Email Address
                      </label>
                      <input
                        type="email"
                        required
                        autoComplete="email"
                        value={form.email}
                        onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
                        className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] bg-white px-4 py-3 text-[#1e3318] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30 focus:border-[#3a5c2f] transition-all"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#4a5e40] mb-1.5">
                      Subject
                    </label>
                    <select
                      required
                      value={form.subject}
                      onChange={(e) => setForm((p) => ({ ...p, subject: e.target.value }))}
                      className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] bg-white px-4 py-3 text-[#1e3318] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30 focus:border-[#3a5c2f] transition-all"
                    >
                      <option value="">Select a topic…</option>
                      <option>SilkSoil</option>
                      <option>Member Platform</option>
                      <option>Scientific Consulting</option>
                      <option>Partnership / Collaboration</option>
                      <option>Media Enquiry</option>
                      <option>General Question</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#4a5e40] mb-1.5">
                      Message
                    </label>
                    <textarea
                      required
                      rows={6}
                      autoComplete="off"
                      value={form.message}
                      onChange={(e) => setForm((p) => ({ ...p, message: e.target.value }))}
                      className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] bg-white px-4 py-3 text-[#1e3318] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30 focus:border-[#3a5c2f] transition-all resize-none"
                    />
                  </div>
                  {error ? (
                    <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                      {error}
                    </div>
                  ) : null}
                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full rounded-full bg-[#3a5c2f] py-4 text-base font-semibold text-white hover:bg-[#1e3318] transition-colors shadow-md"
                  >
                    {submitting ? "Preparing..." : "Open Email Draft"}
                  </button>
                </form>
              </>
            )}
          </div>

          {/* Info sidebar */}
          <div className="space-y-5">
            {[
              {
                icon: "📍",
                title: "Our Address",
                body: "PO Box 287\nCorvallis, OR 97330\nUnited States",
              },
              {
                icon: "✉️",
                title: "Email Us",
                body: "info@biosoil.com\nFor urgent enquiries:\nsupport@biosoil.com",
              },
              {
                icon: "🕐",
                title: "Response Time",
                body: "We aim to respond to all enquiries within 1 business day.",
              },
            ].map((card) => (
              <div
                key={card.title}
                className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-6"
              >
                <span className="text-2xl block mb-3">{card.icon}</span>
                <h3 className="font-serif text-lg text-[#1e3318] mb-2">{card.title}</h3>
                <p className="text-sm text-[#5a6e50] whitespace-pre-line leading-7">{card.body}</p>
              </div>
            ))}

            <div className="rounded-3xl bg-[#1e3318] p-6">
              <p className="editorial-kicker text-[#a8cc8a] mb-3">Quick tools</p>
              <h3 className="font-serif text-lg text-white mb-2">Try the Calculator First</h3>
              <p className="text-sm text-[#9ab88a] leading-6 mb-4">
                Many questions can be answered instantly with our free SilkSoil.
              </p>
              <Link
                href="/silksoil"
                className="block text-center rounded-full bg-[#d4933d] py-3 text-sm font-semibold text-white hover:bg-[#b97849] transition-colors"
              >
                Open Calculator →
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
