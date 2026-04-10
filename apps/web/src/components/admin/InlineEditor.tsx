"use client";

import { useState } from "react";

interface Field {
  key: string;
  label: string;
  multiline?: boolean;
}

interface InlineEditorProps {
  fields: Field[];
  initialValues: Record<string, string>;
  onSave: (values: Record<string, string>) => Promise<void>;
  title?: string;
}

export function InlineEditor({ fields, initialValues, onSave, title }: InlineEditorProps) {
  const [values, setValues] = useState(initialValues);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      await onSave(values);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (error: unknown) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Save failed");
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-6">
      {title && <h3 className="font-serif text-lg text-white mb-5">{title}</h3>}
      <div className="space-y-4">
        {fields.map((f) => (
          <div key={f.key}>
            <label className="block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050] mb-1.5">
              {f.label}
            </label>
            {f.multiline ? (
              <textarea
                rows={4}
                className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm resize-y focus:outline-none focus:border-[#a8cc8a] transition-colors"
                value={values[f.key] ?? ""}
                onChange={(e) => setValues({ ...values, [f.key]: e.target.value })}
              />
            ) : (
              <input
                type="text"
                className="w-full bg-[rgba(255,255,255,0.05)] border border-[rgba(168,204,138,0.15)] rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-[#a8cc8a] transition-colors"
                value={values[f.key] ?? ""}
                onChange={(e) => setValues({ ...values, [f.key]: e.target.value })}
              />
            )}
          </div>
        ))}
      </div>
      <div className="mt-5 flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-5 py-2.5 rounded-xl bg-[#3a5c2f] hover:bg-[#4a7a3a] text-white text-sm font-semibold transition-colors disabled:opacity-50"
        >
          {saving ? "Saving…" : "Save Changes"}
        </button>
        {saved && <span className="text-sm text-[#a8cc8a]">✓ Saved</span>}
        {error && <span className="text-sm text-red-400">✗ {error}</span>}
      </div>
    </div>
  );
}
