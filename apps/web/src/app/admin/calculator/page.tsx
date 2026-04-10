"use client";

import type { ChangeEvent } from "react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { AdminAsyncState } from "@/components/admin/AdminAsyncState";
import { cmsApi } from "@/lib/cmsApi";
import type {
  CalculatorFormula,
  CalculatorFormulaPayload,
  CalculatorWeight,
  ScoreBand,
} from "@/lib/cmsTypes";
import { importCalculatorWorkbook } from "@/features/silksoil/formula-import";

const SUPPORTED_INDICATORS = [
  "ph",
  "organic_matter",
  "microbial_activity",
  "fungal_bacterial_ratio",
  "moisture",
  "temperature",
] as const;

const DEFAULT_FORMULA_TEMPLATE: CalculatorFormulaPayload = {
  version: "2.0",
  name: "Research Candidate",
  description:
    "Candidate SilkSoil scoring model. Tune this draft before activating it for live calculator use.",
  research_background: "",
  research_sources: [],
  target_systems: ["Pasture", "Annual row crop"],
  validation_notes: "",
  supported_indicators: [...SUPPORTED_INDICATORS],
  weights: {
    ph: {
      weight: 0.15,
      optimal_min: 6.0,
      optimal_max: 7.0,
      description: "pH reference band for biologically active agricultural soils.",
    },
    organic_matter: {
      weight: 0.2,
      optimal_min: 3.0,
      optimal_max: 8.0,
      description: "Organic matter supporting carbon habitat, aggregation, and water holding.",
    },
    microbial_activity: {
      weight: 0.25,
      optimal_min: 60,
      optimal_max: 100,
      description:
        "Composite microbial abundance signal from bacteria, fungi, protozoa, and nematodes.",
    },
    fungal_bacterial_ratio: {
      weight: 0.2,
      optimal_min: 1.0,
      optimal_max: 5.0,
      description: "Fungal:bacterial balance reference band.",
    },
    moisture: {
      weight: 0.1,
      optimal_min: 30,
      optimal_max: 60,
      description:
        "Moisture band broadly supportive of microbial activity without saturation stress.",
    },
    temperature: {
      weight: 0.1,
      optimal_min: 18,
      optimal_max: 28,
      description: "Temperature band where field biological activity is typically strong.",
    },
  },
  score_bands: [
    {
      min: 0,
      max: 39,
      label: "Severely constrained",
      color: "#bf4b3e",
      description: "The soil food web is heavily constrained.",
    },
    {
      min: 40,
      max: 59,
      label: "Recovering",
      color: "#c98036",
      description: "Biology is present but several limiting factors remain.",
    },
    {
      min: 60,
      max: 74,
      label: "Functional",
      color: "#baa14d",
      description: "The soil is functioning, with room to improve resilience.",
    },
    {
      min: 75,
      max: 89,
      label: "Strong",
      color: "#5d8b3f",
      description: "The soil food web is active and resilient.",
    },
    {
      min: 90,
      max: 100,
      label: "Highly resilient",
      color: "#2f7d46",
      description: "The biological engine is strong and balanced.",
    },
  ],
};

type FormulaDraft = {
  id: string | null;
  name: string;
  is_active: boolean;
  changelog: string;
  formula_json: CalculatorFormulaPayload;
};

function cloneFormulaPayload(payload?: CalculatorFormulaPayload): CalculatorFormulaPayload {
  return JSON.parse(
    JSON.stringify({
      ...DEFAULT_FORMULA_TEMPLATE,
      ...payload,
      supported_indicators: payload?.supported_indicators?.length
        ? payload.supported_indicators
        : [...SUPPORTED_INDICATORS],
      weights: {
        ...DEFAULT_FORMULA_TEMPLATE.weights,
        ...(payload?.weights ?? {}),
      },
      score_bands: payload?.score_bands?.length
        ? payload.score_bands
        : DEFAULT_FORMULA_TEMPLATE.score_bands,
    }),
  ) as CalculatorFormulaPayload;
}

function draftFromFormula(formula: CalculatorFormula): FormulaDraft {
  return {
    id: formula.id,
    name: formula.name,
    is_active: formula.is_active,
    changelog: formula.changelog ?? "",
    formula_json: cloneFormulaPayload(formula.formula_json),
  };
}

function createBlankDraft(formulaCount: number): FormulaDraft {
  return {
    id: null,
    name: `Research Candidate ${formulaCount + 1}`,
    is_active: false,
    changelog: "New draft created from admin panel.",
    formula_json: cloneFormulaPayload({
      ...DEFAULT_FORMULA_TEMPLATE,
      version: `2.${formulaCount + 1}`,
      name: `Research Candidate ${formulaCount + 1}`,
    }),
  };
}

function validationWarnings(formula: FormulaDraft) {
  const warnings: string[] = [];
  const weights = formula.formula_json.weights;
  const scoreBands = formula.formula_json.score_bands;
  const totalWeight = Object.values(weights).reduce((sum, weight) => sum + weight.weight, 0);

  if (Math.abs(totalWeight - 1) > 0.001) {
    warnings.push(
      `Weights total ${(totalWeight * 100).toFixed(1)}%. Adjust to 100% before activation.`,
    );
  }

  for (const key of SUPPORTED_INDICATORS) {
    if (!weights[key]) {
      warnings.push(`Missing supported indicator: ${key.replace(/_/g, " ")}.`);
    }
  }

  if (!formula.formula_json.research_background?.trim()) {
    warnings.push("Add a research background so other researchers know why this formula exists.");
  }

  if (!formula.formula_json.research_sources?.length) {
    warnings.push("Add at least one research source or validation reference.");
  }

  if (!formula.formula_json.target_systems?.length) {
    warnings.push("Add at least one target production system.");
  }

  scoreBands.forEach((band, index) => {
    if (band.max < band.min) {
      warnings.push(`Score band "${band.label}" has max below min.`);
    }

    if (index > 0 && band.min > scoreBands[index - 1].max + 1) {
      warnings.push(`Score bands have a gap before "${band.label}".`);
    }
  });

  return warnings;
}

function SectionTitle({
  eyebrow,
  title,
  detail,
}: {
  eyebrow: string;
  title: string;
  detail?: string;
}) {
  return (
    <div className="mb-5">
      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050]">
        {eyebrow}
      </p>
      <h2 className="font-serif text-xl text-white">{title}</h2>
      {detail ? <p className="mt-2 max-w-3xl text-sm leading-6 text-[#5a7050]">{detail}</p> : null}
    </div>
  );
}

export default function AdminCalculatorPage() {
  const [active, setActive] = useState<CalculatorFormula | null>(null);
  const [formulas, setFormulas] = useState<CalculatorFormula[]>([]);
  const [selectedFormulaId, setSelectedFormulaId] = useState<string | null>(null);
  const [draft, setDraft] = useState<FormulaDraft | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activating, setActivating] = useState(false);
  const [importing, setImporting] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [importMessage, setImportMessage] = useState<string | null>(null);

  const reload = useCallback(async (preferredId?: string | null) => {
    const [activeFormula, formulaList] = await Promise.all([
      cmsApi.getActiveFormula(),
      cmsApi.listFormulas(),
    ]);

    setActive(activeFormula);
    setFormulas(formulaList);

    const selected =
      formulaList.find((formula) => formula.id === preferredId) ??
      formulaList.find((formula) => formula.id === activeFormula.id) ??
      formulaList[0] ??
      null;

    setSelectedFormulaId(selected?.id ?? null);
    setDraft(selected ? draftFromFormula(selected) : createBlankDraft(formulaList.length));
  }, []);

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, [reload]);

  const warnings = useMemo(() => (draft ? validationWarnings(draft) : []), [draft]);

  const totalWeight = useMemo(() => {
    if (!draft) {
      return 0;
    }

    return Object.values(draft.formula_json.weights).reduce(
      (sum, weight) => sum + weight.weight,
      0,
    );
  }, [draft]);

  function selectFormula(formulaId: string) {
    const formula = formulas.find((item) => item.id === formulaId);
    if (!formula) {
      return;
    }

    setSelectedFormulaId(formulaId);
    setDraft(draftFromFormula(formula));
    setError(null);
    setSaved(false);
  }

  function updateDraft(updater: (current: FormulaDraft) => FormulaDraft) {
    setDraft((current) => (current ? updater(current) : current));
    setSaved(false);
  }

  function updateWeight(key: string, field: keyof CalculatorWeight, value: number | string) {
    updateDraft((current) => ({
      ...current,
      formula_json: {
        ...current.formula_json,
        weights: {
          ...current.formula_json.weights,
          [key]: {
            ...current.formula_json.weights[key],
            [field]: value,
          },
        },
      },
    }));
  }

  function updateBand(index: number, field: keyof ScoreBand, value: string | number) {
    updateDraft((current) => {
      const bands = [...current.formula_json.score_bands];
      bands[index] = { ...bands[index], [field]: value };

      return {
        ...current,
        formula_json: {
          ...current.formula_json,
          score_bands: bands,
        },
      };
    });
  }

  function updateMetadataField(
    field: "version" | "description" | "research_background" | "validation_notes",
    value: string,
  ) {
    updateDraft((current) => ({
      ...current,
      formula_json: {
        ...current.formula_json,
        [field]: value,
      },
    }));
  }

  function updateStringListField(field: "research_sources" | "target_systems", value: string) {
    updateDraft((current) => ({
      ...current,
      formula_json: {
        ...current.formula_json,
        [field]: value
          .split("\n")
          .map((item) => item.trim())
          .filter(Boolean),
      },
    }));
  }

  function handleCreateNew() {
    setSelectedFormulaId(null);
    setDraft(createBlankDraft(formulas.length));
    setError(null);
    setSaved(false);
  }

  function handleDuplicate() {
    if (!draft) {
      return;
    }

    setSelectedFormulaId(null);
    setDraft({
      ...draft,
      id: null,
      is_active: false,
      name: `${draft.name} Copy`,
      changelog: `Duplicated from ${draft.name}.`,
      formula_json: {
        ...cloneFormulaPayload(draft.formula_json),
        name: `${draft.name} Copy`,
      },
    });
    setError(null);
    setSaved(false);
  }

  async function handleWorkbookImport(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;

    setImporting(true);
    setError(null);
    setImportMessage(null);

    try {
      const importedFormula = await importCalculatorWorkbook(file);
      setSelectedFormulaId(null);
      setDraft({
        id: null,
        name: importedFormula.name ?? file.name.replace(/\.[^.]+$/, ""),
        is_active: false,
        changelog: `Imported from workbook ${file.name}.`,
        formula_json: cloneFormulaPayload(importedFormula),
      });
      setImportMessage(
        `Imported ${file.name}. Review the equations, weights, and score bands before activating it.`,
      );
      setSaved(false);
    } catch (importError: unknown) {
      setError(importError instanceof Error ? importError.message : "Failed to import workbook.");
    } finally {
      setImporting(false);
    }
  }

  async function handleSave() {
    if (!draft) {
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const payload = {
        name: draft.name,
        formula_json: draft.formula_json,
        changelog: draft.changelog,
      };

      if (draft.id) {
        await cmsApi.updateFormula(draft.id, payload);
        await reload(draft.id);
      } else {
        const created = (await cmsApi.createFormula(payload)) as CalculatorFormula;
        await reload(created.id);
      }

      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (saveError: unknown) {
      setError(saveError instanceof Error ? saveError.message : "Failed to save formula.");
    } finally {
      setSaving(false);
    }
  }

  async function handleActivate() {
    if (!draft?.id) {
      setError("Save the formula first before activating it.");
      return;
    }

    setActivating(true);
    setError(null);

    try {
      await cmsApi.activateFormula(draft.id);
      await reload(draft.id);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (activateError: unknown) {
      setError(
        activateError instanceof Error ? activateError.message : "Failed to activate formula.",
      );
    } finally {
      setActivating(false);
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="Loading calculator formulas"
          description="Fetching the live model and saved formula candidates."
        />
      </div>
    );
  }

  if (!draft) {
    return (
      <div className="p-8">
        <AdminAsyncState
          title="No calculator formula data found"
          description="The formula lab could not find a draft or active model. Check CMS/API connectivity and retry."
          variant="error"
        />
      </div>
    );
  }

  return (
    <div className="max-w-[1380px] p-8">
      <div className="mb-10 flex flex-wrap items-start justify-between gap-6">
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-[#5a8050]">
            Calculator
          </p>
          <h1 className="font-serif text-4xl text-white">SilkSoil Formula Lab</h1>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-[#5a7050]">
            Researchers can keep multiple formula candidates, attach research reasoning, and
            activate the chosen model only when it is ready for the live calculator.
          </p>
        </div>
        <div className="rounded-2xl border border-[rgba(168,204,138,0.08)] bg-[rgba(58,92,47,0.1)] px-5 py-4 text-right">
          <p className="text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050]">
            Live calculator model
          </p>
          <p className="mt-2 font-serif text-xl text-[#a8cc8a]">{active?.name ?? "None"}</p>
          <p className="mt-1 text-xs text-[#6a7d61]">
            The public calculator always uses the active formula only.
          </p>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[320px_1fr]">
        <aside className="space-y-6">
          <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-5">
            <SectionTitle
              eyebrow="Formula library"
              title="Choose a candidate"
              detail="Researchers can switch between saved formula versions without touching the live one."
            />
            <label className="mb-5 flex cursor-pointer flex-col gap-2 rounded-2xl border border-dashed border-[rgba(168,204,138,0.22)] bg-[rgba(58,92,47,0.08)] px-4 py-4 text-sm text-[#c6dbb2] transition-colors hover:bg-[rgba(58,92,47,0.14)]">
              <span className="font-semibold text-white">
                {importing ? "Importing workbook..." : "Import spreadsheet calculator"}
              </span>
              <span className="text-xs leading-5 text-[#89a27d]">
                Upload `.xlsx`, `.xls`, or `.csv`. Use sheets like `metadata`, `weights`,
                `score_bands`, and `equations` to map an existing Excel calculator into SilkSoil.
              </span>
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                className="hidden"
                onChange={handleWorkbookImport}
              />
            </label>
            <div className="space-y-3">
              {formulas.map((formula) => {
                const selected = selectedFormulaId === formula.id;
                return (
                  <button
                    key={formula.id}
                    onClick={() => selectFormula(formula.id)}
                    className={`w-full rounded-2xl border p-4 text-left transition-all ${
                      selected
                        ? "border-[rgba(168,204,138,0.32)] bg-[rgba(58,92,47,0.2)]"
                        : "border-[rgba(168,204,138,0.08)] bg-[rgba(255,255,255,0.02)] hover:bg-[rgba(58,92,47,0.12)]"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-white">{formula.name}</p>
                        <p className="mt-1 text-xs text-[#6d8163]">
                          Version {formula.formula_json.version ?? "n/a"}
                        </p>
                      </div>
                      {formula.is_active ? (
                        <span className="rounded-full bg-[rgba(168,204,138,0.14)] px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.12em] text-[#a8cc8a]">
                          Active
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-3 text-xs leading-5 text-[#5f7456]">
                      {formula.formula_json.description ?? "No description yet."}
                    </p>
                  </button>
                );
              })}
            </div>

            <div className="mt-5 grid gap-3">
              <button
                onClick={handleCreateNew}
                className="rounded-xl bg-[#3a5c2f] px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#4a7a3a]"
              >
                New Formula Draft
              </button>
              <button
                onClick={handleDuplicate}
                className="rounded-xl border border-[rgba(168,204,138,0.15)] px-4 py-3 text-sm font-semibold text-[#c6dbb2] transition-colors hover:bg-[rgba(255,255,255,0.05)]"
              >
                Duplicate Current Draft
              </button>
            </div>
            {importMessage ? (
              <p className="mt-4 text-xs leading-6 text-[#a8cc8a]">{importMessage}</p>
            ) : null}
          </div>

          <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-5">
            <SectionTitle
              eyebrow="Activation checks"
              title="Research guardrails"
              detail="Before activating a formula, make sure the evidence and tuning notes are complete."
            />
            <div className="space-y-3">
              {warnings.length ? (
                warnings.map((warning) => (
                  <div
                    key={warning}
                    className="rounded-xl border border-[rgba(201,128,54,0.16)] bg-[rgba(201,128,54,0.08)] px-4 py-3 text-sm leading-6 text-[#d9ba8e]"
                  >
                    {warning}
                  </div>
                ))
              ) : (
                <div className="rounded-xl border border-[rgba(168,204,138,0.16)] bg-[rgba(58,92,47,0.14)] px-4 py-3 text-sm leading-6 text-[#c6dbb2]">
                  This formula is ready for researcher review and activation.
                </div>
              )}
            </div>
          </div>
        </aside>

        <div className="space-y-6">
          <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-6">
            <SectionTitle
              eyebrow="Formula identity"
              title="Research context"
              detail="Use this section to document what the formula is for, what evidence shaped it, and which production systems it targets."
            />
            <div className="grid gap-5 lg:grid-cols-2">
              <div>
                <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050]">
                  Formula Name
                </label>
                <input
                  className="w-full rounded-xl border border-[rgba(168,204,138,0.15)] bg-[rgba(255,255,255,0.05)] px-4 py-3 text-sm text-white focus:border-[#a8cc8a] focus:outline-none"
                  value={draft.name}
                  onChange={(event) =>
                    updateDraft((current) => ({ ...current, name: event.target.value }))
                  }
                />
              </div>
              <div>
                <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050]">
                  Version Tag
                </label>
                <input
                  className="w-full rounded-xl border border-[rgba(168,204,138,0.15)] bg-[rgba(255,255,255,0.05)] px-4 py-3 text-sm text-white focus:border-[#a8cc8a] focus:outline-none"
                  value={draft.formula_json.version ?? ""}
                  onChange={(event) => updateMetadataField("version", event.target.value)}
                  placeholder="Example: 2.1-field-trial"
                />
              </div>
            </div>

            <div className="mt-5">
              <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050]">
                Formula Description
              </label>
              <textarea
                className="min-h-28 w-full rounded-xl border border-[rgba(168,204,138,0.15)] bg-[rgba(255,255,255,0.05)] px-4 py-3 text-sm leading-6 text-white focus:border-[#a8cc8a] focus:outline-none"
                value={draft.formula_json.description ?? ""}
                onChange={(event) => updateMetadataField("description", event.target.value)}
                placeholder="What this formula emphasizes and how it differs from other candidates."
              />
            </div>

            <div className="mt-5">
              <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050]">
                Research Background
              </label>
              <textarea
                className="min-h-36 w-full rounded-xl border border-[rgba(168,204,138,0.15)] bg-[rgba(255,255,255,0.05)] px-4 py-3 text-sm leading-6 text-white focus:border-[#a8cc8a] focus:outline-none"
                value={draft.formula_json.research_background ?? ""}
                onChange={(event) => updateMetadataField("research_background", event.target.value)}
                placeholder="Summarize the biological logic, trial work, or field observations behind this formula."
              />
            </div>

            <div className="mt-5 grid gap-5 lg:grid-cols-2">
              <div>
                <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050]">
                  Research Sources
                </label>
                <textarea
                  className="min-h-32 w-full rounded-xl border border-[rgba(168,204,138,0.15)] bg-[rgba(255,255,255,0.05)] px-4 py-3 text-sm leading-6 text-white focus:border-[#a8cc8a] focus:outline-none"
                  value={(draft.formula_json.research_sources ?? []).join("\n")}
                  onChange={(event) =>
                    updateStringListField("research_sources", event.target.value)
                  }
                  placeholder="One citation or source per line"
                />
              </div>
              <div>
                <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050]">
                  Target Systems
                </label>
                <textarea
                  className="min-h-32 w-full rounded-xl border border-[rgba(168,204,138,0.15)] bg-[rgba(255,255,255,0.05)] px-4 py-3 text-sm leading-6 text-white focus:border-[#a8cc8a] focus:outline-none"
                  value={(draft.formula_json.target_systems ?? []).join("\n")}
                  onChange={(event) => updateStringListField("target_systems", event.target.value)}
                  placeholder="One production system per line"
                />
              </div>
            </div>

            <div className="mt-5">
              <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050]">
                Validation Notes
              </label>
              <textarea
                className="min-h-28 w-full rounded-xl border border-[rgba(168,204,138,0.15)] bg-[rgba(255,255,255,0.05)] px-4 py-3 text-sm leading-6 text-white focus:border-[#a8cc8a] focus:outline-none"
                value={draft.formula_json.validation_notes ?? ""}
                onChange={(event) => updateMetadataField("validation_notes", event.target.value)}
                placeholder="Field trial notes, sample size, consultant feedback, or known limitations."
              />
            </div>
          </div>

          <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-6">
            <SectionTitle
              eyebrow="Indicator tuning"
              title="Supported calculator indicators"
              detail="These are the indicators the live SilkSoil calculator currently understands. Researchers can tune weights and ranges for each one."
            />
            {draft.formula_json.workbook_import?.file_name ? (
              <div className="mb-5 rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(58,92,47,0.12)] px-4 py-3 text-sm text-[#c6dbb2]">
                Imported from{" "}
                <span className="font-semibold text-white">
                  {draft.formula_json.workbook_import.file_name}
                </span>
                .
                {draft.formula_json.workbook_import.sheet_names?.length ? (
                  <span className="block text-xs text-[#89a27d]">
                    Sheets detected: {draft.formula_json.workbook_import.sheet_names.join(", ")}
                  </span>
                ) : null}
                {draft.formula_json.workbook_import.supported_features?.length ? (
                  <span className="mt-2 block text-xs text-[#89a27d]">
                    Parser features:{" "}
                    {draft.formula_json.workbook_import.supported_features.join(", ")}
                  </span>
                ) : null}
                {draft.formula_json.workbook_import.compatibility_notes?.length ? (
                  <span className="mt-2 block text-xs leading-5 text-[#c6dbb2]">
                    {draft.formula_json.workbook_import.compatibility_notes.join(" ")}
                  </span>
                ) : null}
              </div>
            ) : null}
            <div className="mb-4 flex flex-wrap gap-2">
              {SUPPORTED_INDICATORS.map((indicator) => (
                <span
                  key={indicator}
                  className="rounded-full bg-[rgba(58,92,47,0.16)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-[#c6dbb2]"
                >
                  {indicator.replace(/_/g, " ")}
                </span>
              ))}
            </div>
            <div className="mb-5 flex items-center justify-between">
              <h3 className="font-serif text-lg text-white">Scoring Weights</h3>
              <span
                className={`text-sm font-semibold ${
                  Math.abs(totalWeight - 1) < 0.001 ? "text-[#a8cc8a]" : "text-yellow-400"
                }`}
              >
                Total: {(totalWeight * 100).toFixed(0)}%{" "}
                {Math.abs(totalWeight - 1) < 0.001 ? "✓" : "(should = 100%)"}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full min-w-[840px]">
                <thead>
                  <tr className="border-b border-[rgba(168,204,138,0.08)]">
                    {["Parameter", "Weight (%)", "Optimal Min", "Optimal Max", "Description"].map(
                      (heading) => (
                        <th
                          key={heading}
                          className="pb-3 pr-4 text-left text-xs font-semibold uppercase tracking-wider text-[#5a8050]"
                        >
                          {heading}
                        </th>
                      ),
                    )}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(draft.formula_json.weights).map(([key, weight]) => (
                    <tr key={key} className="border-b border-[rgba(168,204,138,0.05)]">
                      <td className="py-3 pr-4 text-sm font-medium text-white capitalize">
                        {key.replace(/_/g, " ")}
                      </td>
                      <td className="py-3 pr-4">
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          max="100"
                          className="w-24 rounded-lg border border-[rgba(168,204,138,0.15)] bg-[rgba(255,255,255,0.05)] px-2 py-1.5 text-sm text-white focus:border-[#a8cc8a] focus:outline-none"
                          value={(weight.weight * 100).toFixed(1)}
                          onChange={(event) =>
                            updateWeight(key, "weight", Number(event.target.value) / 100)
                          }
                        />
                      </td>
                      <td className="py-3 pr-4">
                        <input
                          type="number"
                          className="w-24 rounded-lg border border-[rgba(168,204,138,0.15)] bg-[rgba(255,255,255,0.05)] px-2 py-1.5 text-sm text-white focus:border-[#a8cc8a] focus:outline-none"
                          value={weight.optimal_min}
                          onChange={(event) =>
                            updateWeight(key, "optimal_min", Number(event.target.value))
                          }
                        />
                      </td>
                      <td className="py-3 pr-4">
                        <input
                          type="number"
                          className="w-24 rounded-lg border border-[rgba(168,204,138,0.15)] bg-[rgba(255,255,255,0.05)] px-2 py-1.5 text-sm text-white focus:border-[#a8cc8a] focus:outline-none"
                          value={weight.optimal_max}
                          onChange={(event) =>
                            updateWeight(key, "optimal_max", Number(event.target.value))
                          }
                        />
                      </td>
                      <td className="py-3">
                        <input
                          className="w-full rounded-lg border border-[rgba(168,204,138,0.1)] bg-[rgba(255,255,255,0.04)] px-2 py-1.5 text-xs text-[#c8dbb6] focus:border-[#a8cc8a] focus:outline-none"
                          value={weight.description}
                          onChange={(event) => updateWeight(key, "description", event.target.value)}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-6">
            <SectionTitle
              eyebrow="Formulas"
              title="Mathematical equations"
              detail="Define the dynamic mathematical formulas used by the engine."
            />
            <div className="space-y-4">
              {draft.formula_json.equations?.map((equation, index) => (
                <div
                  key={index}
                  className="grid gap-3 lg:grid-cols-[1fr_2fr_1fr] items-start border-b border-[rgba(168,204,138,0.12)] pb-4"
                >
                  <div>
                    <label className="mb-1 block text-xs text-[#5a7050]">Variable / Key</label>
                    <input
                      className="w-full rounded-lg border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.05)] px-2 py-1.5 text-sm text-white focus:border-[#a8cc8a] focus:outline-none"
                      value={equation.key}
                      onChange={(e) => {
                        const newEquations = [...(draft.formula_json.equations || [])];
                        newEquations[index].key = e.target.value;
                        updateDraft((c) => ({
                          ...c,
                          formula_json: { ...c.formula_json, equations: newEquations },
                        }));
                      }}
                      placeholder="e.g. decomposition_rate"
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs text-[#5a7050]">Expression</label>
                    <textarea
                      className="w-full rounded-lg border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.05)] px-2 py-1.5 text-sm text-white focus:border-[#a8cc8a] focus:outline-none font-mono"
                      rows={2}
                      value={equation.expression}
                      onChange={(e) => {
                        const newEquations = [...(draft.formula_json.equations || [])];
                        newEquations[index].expression = e.target.value;
                        updateDraft((c) => ({
                          ...c,
                          formula_json: { ...c.formula_json, equations: newEquations },
                        }));
                      }}
                      placeholder="e.g. initial_detritus * 0.05"
                    />
                  </div>
                  <div className="pt-5">
                    <button
                      onClick={() => {
                        const newEquations = [...(draft.formula_json.equations || [])];
                        newEquations.splice(index, 1);
                        updateDraft((c) => ({
                          ...c,
                          formula_json: { ...c.formula_json, equations: newEquations },
                        }));
                      }}
                      className="text-xs text-red-400 hover:text-red-300"
                    >
                      Remove Equation
                    </button>
                  </div>
                </div>
              ))}
              <button
                onClick={() => {
                  const newEquations = [...(draft.formula_json.equations || [])];
                  newEquations.push({
                    key: "",
                    label: "",
                    expression: "",
                    description: "",
                    category: "overall",
                  });
                  updateDraft((c) => ({
                    ...c,
                    formula_json: { ...c.formula_json, equations: newEquations },
                  }));
                }}
                className="text-sm text-[#a8cc8a] hover:underline"
              >
                + Add Mathematical Equation
              </button>
            </div>
          </div>

          <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-6">
            <SectionTitle
              eyebrow="Interpretation"
              title="Score bands"
              detail="Researchers can change the language and thresholds that farmers see after a score is generated."
            />
            <div className="space-y-3">
              {draft.formula_json.score_bands.map((band, index) => (
                <div key={`${band.label}-${index}`} className="grid gap-3 lg:grid-cols-6">
                  <div>
                    <label className="mb-1 block text-xs text-[#5a7050]">Label</label>
                    <input
                      className="w-full rounded-lg border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.05)] px-2 py-1.5 text-sm text-white focus:border-[#a8cc8a] focus:outline-none"
                      value={band.label}
                      onChange={(event) => updateBand(index, "label", event.target.value)}
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs text-[#5a7050]">Min</label>
                    <input
                      type="number"
                      className="w-full rounded-lg border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.05)] px-2 py-1.5 text-sm text-white focus:border-[#a8cc8a] focus:outline-none"
                      value={band.min}
                      onChange={(event) => updateBand(index, "min", Number(event.target.value))}
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs text-[#5a7050]">Max</label>
                    <input
                      type="number"
                      className="w-full rounded-lg border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.05)] px-2 py-1.5 text-sm text-white focus:border-[#a8cc8a] focus:outline-none"
                      value={band.max}
                      onChange={(event) => updateBand(index, "max", Number(event.target.value))}
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs text-[#5a7050]">Color</label>
                    <div className="flex items-center gap-2">
                      <span
                        className="h-6 w-6 shrink-0 rounded-full border border-white/10"
                        style={{ background: band.color }}
                      />
                      <input
                        className="w-full rounded-lg border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.05)] px-2 py-1.5 text-sm text-white focus:border-[#a8cc8a] focus:outline-none"
                        value={band.color}
                        onChange={(event) => updateBand(index, "color", event.target.value)}
                      />
                    </div>
                  </div>
                  <div className="lg:col-span-2">
                    <label className="mb-1 block text-xs text-[#5a7050]">Description</label>
                    <input
                      className="w-full rounded-lg border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.05)] px-2 py-1.5 text-sm text-white focus:border-[#a8cc8a] focus:outline-none"
                      value={band.description}
                      onChange={(event) => updateBand(index, "description", event.target.value)}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-[rgba(168,204,138,0.12)] bg-[rgba(255,255,255,0.03)] p-6">
            <SectionTitle
              eyebrow="Release note"
              title="Save or activate"
              detail="Researchers can save a draft repeatedly. Activation is a separate step so the live calculator only changes when you explicitly choose it."
            />
            <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-[#5a8050]">
              Changelog
            </label>
            <textarea
              className="min-h-28 w-full rounded-xl border border-[rgba(168,204,138,0.15)] bg-[rgba(255,255,255,0.05)] px-4 py-3 text-sm leading-6 text-white focus:border-[#a8cc8a] focus:outline-none"
              value={draft.changelog}
              onChange={(event) =>
                updateDraft((current) => ({ ...current, changelog: event.target.value }))
              }
              placeholder="What changed in this formula draft?"
            />

            {error ? <p className="mt-4 text-sm text-red-400">✗ {error}</p> : null}

            <div className="mt-5 flex flex-wrap items-center gap-3">
              <button
                onClick={handleSave}
                disabled={saving}
                className="rounded-xl bg-[#3a5c2f] px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#4a7a3a] disabled:opacity-50"
              >
                {saving ? "Saving…" : draft.id ? "Save Formula" : "Create Formula"}
              </button>
              <button
                onClick={handleActivate}
                disabled={activating || !draft.id || warnings.length > 0}
                className="rounded-xl border border-[rgba(168,204,138,0.2)] px-5 py-3 text-sm font-semibold text-[#c6dbb2] transition-colors hover:bg-[rgba(255,255,255,0.05)] disabled:cursor-not-allowed disabled:opacity-40"
              >
                {activating ? "Activating…" : "Activate for Live Calculator"}
              </button>
              {saved ? <span className="text-sm text-[#a8cc8a]">✓ Formula saved</span> : null}
              {draft.is_active ? (
                <span className="rounded-full bg-[rgba(168,204,138,0.14)] px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] text-[#a8cc8a]">
                  Currently active
                </span>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
