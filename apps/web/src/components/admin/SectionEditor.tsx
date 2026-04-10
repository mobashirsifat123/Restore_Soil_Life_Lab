"use client";

import { useState } from "react";

type Item = Record<string, string | number | boolean>;

interface SectionField {
  key: string;
  label: string;
  multiline?: boolean;
  type?: "text" | "number" | "boolean";
}

interface SectionEditorProps {
  title: string;
  items: Item[];
  fields: SectionField[];
  onSave: (items: Item[]) => Promise<void>;
  addLabel?: string;
}

export function SectionEditor({
  title,
  items: initialItems,
  fields,
  onSave,
  addLabel = "Add Item",
}: SectionEditorProps) {
  const [items, setItems] = useState<Item[]>(initialItems);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function updateItem(index: number, key: string, value: string | number | boolean) {
    setItems(items.map((item, i) => (i === index ? { ...item, [key]: value } : item)));
  }

  function addItem() {
    const blank: Item = {};
    fields.forEach((f) => {
      blank[f.key] = "";
    });
    setItems([...items, blank]);
  }

  function removeItem(index: number) {
    setItems(items.filter((_, i) => i !== index));
  }

  function moveItem(index: number, dir: 1 | -1) {
    const next = [...items];
    const target = index + dir;
    if (target < 0 || target >= next.length) return;
    [next[index], next[target]] = [next[target], next[index]];
    setItems(next);
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      await onSave(items);
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
      <h3 className="font-serif text-lg text-white mb-5">{title}</h3>
      <div className="space-y-4">
        {items.map((item, idx) => (
          <div
            key={idx}
            className="rounded-xl border border-[rgba(168,204,138,0.1)] bg-[rgba(255,255,255,0.03)] p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-[#5a8050] uppercase tracking-wider">
                Item {idx + 1}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => moveItem(idx, -1)}
                  className="text-[#5a7050] hover:text-white text-xs px-2 py-1 rounded transition-colors"
                >
                  ↑
                </button>
                <button
                  onClick={() => moveItem(idx, 1)}
                  className="text-[#5a7050] hover:text-white text-xs px-2 py-1 rounded transition-colors"
                >
                  ↓
                </button>
                <button
                  onClick={() => removeItem(idx)}
                  className="text-red-500/60 hover:text-red-400 text-xs px-2 py-1 rounded transition-colors"
                >
                  Remove
                </button>
              </div>
            </div>
            <div className="grid gap-3">
              {fields.map((f) => (
                <div key={f.key}>
                  <label className="block text-xs text-[#5a7050] mb-1">{f.label}</label>
                  {f.type === "boolean" ? (
                    <input
                      type="checkbox"
                      checked={!!item[f.key]}
                      onChange={(e) => updateItem(idx, f.key, e.target.checked)}
                      className="w-4 h-4 accent-[#a8cc8a]"
                    />
                  ) : f.multiline ? (
                    <textarea
                      rows={3}
                      className="w-full bg-[rgba(255,255,255,0.04)] border border-[rgba(168,204,138,0.12)] rounded-lg px-3 py-2 text-white text-sm resize-y focus:outline-none focus:border-[#a8cc8a] transition-colors"
                      value={String(item[f.key] ?? "")}
                      onChange={(e) => updateItem(idx, f.key, e.target.value)}
                    />
                  ) : (
                    <input
                      type={f.type === "number" ? "number" : "text"}
                      className="w-full bg-[rgba(255,255,255,0.04)] border border-[rgba(168,204,138,0.12)] rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-[#a8cc8a] transition-colors"
                      value={String(item[f.key] ?? "")}
                      onChange={(e) =>
                        updateItem(
                          idx,
                          f.key,
                          f.type === "number" ? Number(e.target.value) : e.target.value,
                        )
                      }
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <button
        onClick={addItem}
        className="mt-4 w-full py-2.5 border border-dashed border-[rgba(168,204,138,0.2)] rounded-xl text-[#5a8050] text-sm hover:border-[#a8cc8a] hover:text-[#a8cc8a] transition-colors"
      >
        + {addLabel}
      </button>
      <div className="mt-5 flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-5 py-2.5 rounded-xl bg-[#3a5c2f] hover:bg-[#4a7a3a] text-white text-sm font-semibold transition-colors disabled:opacity-50"
        >
          {saving ? "Saving…" : "Save All"}
        </button>
        {saved && <span className="text-sm text-[#a8cc8a]">✓ Saved</span>}
        {error && <span className="text-sm text-red-400">✗ {error}</span>}
      </div>
    </div>
  );
}
