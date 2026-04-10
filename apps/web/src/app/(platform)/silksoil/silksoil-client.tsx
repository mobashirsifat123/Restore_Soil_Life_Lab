"use client";

import Link from "next/link";
import { useState } from "react";

import type { CalculatorFormula } from "@/lib/cmsTypes";
import {
  calculateSoilHealth,
  silkSoilOptions,
  type HealthRecommendation,
  type SilkSoilInputs,
} from "@/features/silksoil/analysis";

type SilkSoilClientProps = {
  userName: string | null;
  activeFormula: CalculatorFormula | null;
};

type NumericFieldName = Exclude<keyof SilkSoilInputs, "productionSystem" | "soilTexture">;

const defaultInputs: SilkSoilInputs = {
  productionSystem: "pasture",
  soilTexture: "loam",
  ph: 6.4,
  organicMatter: 4.6,
  moisture: 42,
  temperature: 21,
  bacteria: 115,
  fungi: 145,
  protozoa: 8,
  nematodes: 85,
  compaction: 250,
  nitrateN: 18,
};

function ScoreBar({ score, max, color }: { score: number; max: number; color: string }) {
  return (
    <div className="overflow-hidden rounded-full bg-[#e8e0cc]">
      <div
        className="h-2.5 rounded-full transition-all duration-700"
        style={{
          width: `${Math.min(100, (score / Math.max(max, 1)) * 100)}%`,
          backgroundColor: color,
        }}
      />
    </div>
  );
}

function NumberField({
  label,
  value,
  onChange,
  min,
  max,
  step,
  unit,
  hint,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step: number;
  unit: string;
  hint: string;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-xs font-semibold uppercase tracking-[0.15em] text-[#4a5e40]">
        {label}{" "}
        <span className="font-normal normal-case tracking-normal text-[#9ab88a]">{unit}</span>
      </label>
      <input
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number.parseFloat(event.target.value) || 0)}
        className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] bg-white px-4 py-3 font-medium text-[#1e3318] transition-all focus:border-[#3a5c2f] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30"
      />
      <p className="mt-1 text-xs text-[#8aaa7a]">{hint}</p>
    </div>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
  hint,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: Array<{ value: string; label: string }>;
  hint: string;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-xs font-semibold uppercase tracking-[0.15em] text-[#4a5e40]">
        {label}
      </label>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-xl border border-[rgba(58,92,47,0.2)] bg-white px-4 py-3 font-medium text-[#1e3318] transition-all focus:border-[#3a5c2f] focus:outline-none focus:ring-2 focus:ring-[#3a5c2f]/30"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <p className="mt-1 text-xs text-[#8aaa7a]">{hint}</p>
    </div>
  );
}

function recommendationStyles(priority: HealthRecommendation["priority"]) {
  if (priority === "High") {
    return "border-[rgba(191,75,62,0.18)] bg-[rgba(191,75,62,0.07)] text-[#8e352b]";
  }

  if (priority === "Medium") {
    return "border-[rgba(201,128,54,0.18)] bg-[rgba(201,128,54,0.08)] text-[#986028]";
  }

  return "border-[rgba(58,92,47,0.16)] bg-[rgba(58,92,47,0.06)] text-[#35542c]";
}

function componentStatusPill(status: "strong" | "watch" | "weak") {
  if (status === "strong") {
    return "bg-[rgba(47,125,70,0.12)] text-[#2f7d46]";
  }

  if (status === "watch") {
    return "bg-[rgba(201,128,54,0.12)] text-[#986028]";
  }

  return "bg-[rgba(191,75,62,0.12)] text-[#8e352b]";
}

function SilkSoilTeaser() {
  const indicators = [
    {
      icon: "🌡️",
      name: "Temperature",
      note: "Controls microbial activity and nutrient cycling speed.",
    },
    {
      icon: "🍄",
      name: "Fungi",
      note: "Supports aggregation, residue breakdown, and fungal-dominant systems.",
    },
    {
      icon: "🔬",
      name: "Protozoa",
      note: "Grazers help release nutrients that bacteria temporarily hold.",
    },
    { icon: "🦠", name: "Bacteria", note: "Drives fast nutrient turnover and residue processing." },
    {
      icon: "🪱",
      name: "Nematodes",
      note: "Signals whether the food web is moving beyond simple biomass.",
    },
    {
      icon: "🧱",
      name: "Compaction",
      note: "Aeration and pore space determine whether biology can function.",
    },
  ];

  return (
    <div className="min-h-[70vh]">
      <div className="relative mb-8 overflow-hidden rounded-3xl bg-[#1e3318] px-8 py-12 text-center text-white">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute right-0 top-0 h-64 w-64 rounded-full bg-[rgba(212,147,61,0.08)] blur-3xl" />
        </div>
        <div className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-full bg-[#3a5c2f] text-3xl">
          🔒
        </div>
        <p className="editorial-kicker mb-3 text-[#a8cc8a]">Member-exclusive tool</p>
        <h1 className="mb-4 font-serif text-[2.5rem] leading-tight tracking-[-0.04em] md:text-[3.2rem]">
          SilkSoil Analysis System
        </h1>
        <p className="mx-auto mb-8 max-w-2xl text-[#9ab88a] leading-8">
          SilkSoil interprets chemistry, physical habitat, microbial abundance, and food-web balance
          so farmers can see which soil constraints matter most and how to improve them.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            href="/login"
            className="rounded-full bg-[#d4933d] px-8 py-4 text-base font-semibold text-white shadow-md transition-colors hover:bg-[#b97849]"
          >
            Sign In to Access SilkSoil
          </Link>
          <Link
            href="/contact"
            className="rounded-full border border-white/20 px-8 py-4 text-base font-semibold text-white transition-colors hover:bg-white/10"
          >
            Request Membership
          </Link>
        </div>
      </div>

      <div className="mb-8 grid gap-6 lg:grid-cols-[1fr_340px]">
        <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-7">
          <p className="editorial-kicker mb-3 text-[#3a5c2f]">What SilkSoil analyses</p>
          <h2 className="mb-5 font-serif text-2xl text-[#1e3318]">
            Farmer-facing biological interpretation
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {indicators.map((indicator) => (
              <div
                key={indicator.name}
                className="flex items-start gap-3 rounded-2xl bg-[#f8f5ef] p-4"
              >
                <span className="shrink-0 text-2xl">{indicator.icon}</span>
                <div>
                  <p className="text-sm font-semibold text-[#1e3318]">{indicator.name}</p>
                  <p className="mt-0.5 text-xs leading-5 text-[#5a6e50]">{indicator.note}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-7">
          <p className="mb-4 font-mono text-xs uppercase tracking-widest text-[#5a7050]">
            What improves
          </p>
          <div className="space-y-4 text-sm leading-6 text-[#5a6e50]">
            <p>
              SilkSoil now adapts the fungal:bacterial target to the selected production system.
            </p>
            <p>
              It scores microbial abundance separately from habitat stress, so low biology is not
              confused with low fertility alone.
            </p>
            <p>
              Recommendations prioritize the constraints most likely to limit soil recovery first.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function SilkSoilCalculator({
  userName,
  activeFormula,
}: {
  userName: string;
  activeFormula: CalculatorFormula | null;
}) {
  const [inputs, setInputs] = useState(defaultInputs);
  const [result, setResult] = useState(() =>
    calculateSoilHealth(defaultInputs, activeFormula?.formula_json),
  );
  const [showResult, setShowResult] = useState(false);

  const activeModelName =
    activeFormula?.name ?? activeFormula?.formula_json.name ?? "SilkSoil Reference Model";

  function updateInputs(nextInputs: SilkSoilInputs) {
    setInputs(nextInputs);

    if (showResult) {
      setResult(calculateSoilHealth(nextInputs, activeFormula?.formula_json));
    }
  }

  function handleNumericChange(name: NumericFieldName, value: number) {
    updateInputs({ ...inputs, [name]: value });
  }

  function handleProductionSystemChange(value: string) {
    updateInputs({ ...inputs, productionSystem: value as SilkSoilInputs["productionSystem"] });
  }

  function handleSoilTextureChange(value: string) {
    updateInputs({ ...inputs, soilTexture: value as SilkSoilInputs["soilTexture"] });
  }

  function handleCalculate() {
    const nextResult = calculateSoilHealth(inputs, activeFormula?.formula_json);
    setResult(nextResult);
    setShowResult(true);
    setTimeout(() => {
      document
        .getElementById("silk-results")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
  }

  function handleReset() {
    setInputs(defaultInputs);
    setResult(calculateSoilHealth(defaultInputs, activeFormula?.formula_json));
    setShowResult(false);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-[rgba(58,92,47,0.12)] bg-[#f0f7ed] px-6 py-4">
        <span className="text-xl">🌱</span>
        <div className="mr-auto">
          <p className="text-sm font-semibold text-[#1e3318]">Welcome, {userName}</p>
          <p className="text-xs text-[#5a7050]">SilkSoil - member access unlocked</p>
        </div>
        <div className="rounded-full bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.15em] text-[#4a5e40]">
          Model: {activeModelName}
        </div>
      </div>

      {!activeFormula ? (
        <div className="rounded-2xl border border-[rgba(201,128,54,0.18)] bg-[rgba(201,128,54,0.08)] px-5 py-4 text-sm leading-6 text-[#7b5220]">
          <p className="font-semibold text-[#6e4615]">Using resilient local scoring defaults</p>
          <p className="mt-1">
            The live SilkSoil formula could not be loaded from the CMS, so this calculator is using
            the built-in reference model to keep the workflow available.
          </p>
        </div>
      ) : null}

      <div className="relative overflow-hidden rounded-3xl bg-[#1e3318] px-8 py-8 text-white">
        <div className="pointer-events-none absolute right-0 top-0 h-48 w-48 rounded-full bg-[rgba(212,147,61,0.08)] blur-3xl" />
        <p className="editorial-kicker mb-2 text-[#a8cc8a]">SILK Soil Analysis System</p>
        <h1 className="mb-2 font-serif text-[2rem] leading-tight tracking-[-0.04em]">SilkSoil</h1>
        <p className="max-w-3xl text-sm leading-7 text-[#9ab88a]">
          Enter field and lab measurements below. SilkSoil weighs chemistry, habitat, microbial
          abundance, and fungal:bacterial balance to estimate how well the soil food web is
          supporting production.
        </p>
      </div>

      <div className="grid items-start gap-8 lg:grid-cols-[1fr_430px]">
        <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-8 shadow-sm">
          <h2 className="mb-1 font-serif text-2xl text-[#1e3318]">Your Soil Measurements</h2>
          <p className="mb-8 text-sm text-[#6a8060]">
            Use the closest field or lab values you have. Production system and soil texture help
            SilkSoil avoid one-size-fits-all interpretation.
          </p>

          <div className="mb-8 grid gap-5 sm:grid-cols-2">
            <SelectField
              label="Production System"
              value={inputs.productionSystem}
              onChange={handleProductionSystemChange}
              options={silkSoilOptions.productionSystems}
              hint="Fungal:bacterial targets change with disturbance and crop type."
            />
            <SelectField
              label="Soil Texture"
              value={inputs.soilTexture}
              onChange={handleSoilTextureChange}
              options={silkSoilOptions.soilTextures}
              hint="Texture changes ideal moisture, compaction, and organic matter expectations."
            />
          </div>

          <div className="mb-8">
            <p className="mb-5 border-b border-[rgba(58,92,47,0.12)] pb-2 text-xs font-bold uppercase tracking-[0.2em] text-[#3a5c2f]">
              Soil Chemistry
            </p>
            <div className="grid gap-5 sm:grid-cols-2">
              <NumberField
                label="Soil pH"
                value={inputs.ph}
                onChange={(value) => handleNumericChange("ph", value)}
                min={3}
                max={10}
                step={0.1}
                unit="pH units"
                hint="Most biologically active mixed soils sit around pH 6.0-7.0."
              />
              <NumberField
                label="Organic Matter"
                value={inputs.organicMatter}
                onChange={(value) => handleNumericChange("organicMatter", value)}
                min={0}
                max={20}
                step={0.1}
                unit="%"
                hint="Higher organic matter usually means more microbial habitat and better structure."
              />
              <NumberField
                label="Nitrate-N"
                value={inputs.nitrateN}
                onChange={(value) => handleNumericChange("nitrateN", value)}
                min={0}
                max={200}
                step={1}
                unit="ppm"
                hint="Interpretation is adjusted to the selected production system."
              />
              <NumberField
                label="Temperature"
                value={inputs.temperature}
                onChange={(value) => handleNumericChange("temperature", value)}
                min={0}
                max={45}
                step={0.5}
                unit="C"
                hint="Large temperature swings can shut down otherwise good biology."
              />
            </div>
          </div>

          <div className="mb-8">
            <p className="mb-5 border-b border-[rgba(58,92,47,0.12)] pb-2 text-xs font-bold uppercase tracking-[0.2em] text-[#3a5c2f]">
              Physical Habitat
            </p>
            <div className="grid gap-5 sm:grid-cols-2">
              <NumberField
                label="Soil Moisture"
                value={inputs.moisture}
                onChange={(value) => handleNumericChange("moisture", value)}
                min={0}
                max={100}
                step={1}
                unit="%"
                hint="Moisture is interpreted against your selected soil texture."
              />
              <NumberField
                label="Compaction"
                value={inputs.compaction}
                onChange={(value) => handleNumericChange("compaction", value)}
                min={0}
                max={1000}
                step={10}
                unit="psi"
                hint="High penetrometer pressure often blocks aeration and root-driven recovery."
              />
            </div>
          </div>

          <div className="mb-10">
            <p className="mb-5 border-b border-[rgba(58,92,47,0.12)] pb-2 text-xs font-bold uppercase tracking-[0.2em] text-[#3a5c2f]">
              Biological Activity
            </p>
            <div className="grid gap-5 sm:grid-cols-2">
              <NumberField
                label="Total Bacteria"
                value={inputs.bacteria}
                onChange={(value) => handleNumericChange("bacteria", value)}
                min={0}
                max={500}
                step={1}
                unit="ug/g dry soil"
                hint="Higher is not always better. The right level depends on the production system."
              />
              <NumberField
                label="Total Fungi"
                value={inputs.fungi}
                onChange={(value) => handleNumericChange("fungi", value)}
                min={0}
                max={500}
                step={1}
                unit="ug/g dry soil"
                hint="Fungi support aggregation and tend to matter more in perennial systems."
              />
              <NumberField
                label="Protozoa"
                value={inputs.protozoa}
                onChange={(value) => handleNumericChange("protozoa", value)}
                min={0}
                max={50}
                step={0.5}
                unit="x 10^3/g"
                hint="Grazers help convert biomass into plant-available nutrients."
              />
              <NumberField
                label="Nematodes"
                value={inputs.nematodes}
                onChange={(value) => handleNumericChange("nematodes", value)}
                min={0}
                max={500}
                step={5}
                unit="/100g soil"
                hint="Counts alone are useful, but taxonomy still matters for full diagnosis."
              />
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={handleCalculate}
              className="flex-1 rounded-full bg-[#3a5c2f] py-4 text-base font-semibold text-white shadow-md transition-colors hover:bg-[#1e3318]"
            >
              Run SILK Analysis
            </button>
            <button
              onClick={handleReset}
              className="rounded-full border border-[rgba(58,92,47,0.2)] px-6 py-4 text-sm font-medium text-[#4a5e40] transition-colors hover:bg-[rgba(58,92,47,0.06)]"
            >
              Reset
            </button>
          </div>
        </div>

        <div id="silk-results" className="space-y-5">
          {!showResult ? (
            <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-8 text-center">
              <div className="mb-5 text-5xl">🔬</div>
              <h3 className="mb-2 font-serif text-xl text-[#1e3318]">Ready to analyse</h3>
              <p className="text-sm leading-6 text-[#6a8060]">
                SilkSoil will combine your measurements into an overall resilience score, a
                microbial condition summary, and a prioritized management roadmap.
              </p>
            </div>
          ) : (
            <>
              <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-8 text-center shadow-sm">
                <p className="editorial-kicker mb-2 text-[#3a5c2f]">SILK Soil Health Score</p>
                <div
                  className="mb-1 font-serif text-[6rem] font-bold leading-none"
                  style={{ color: result.color }}
                >
                  {result.total}
                </div>
                <div className="mb-4 flex items-center justify-center gap-3">
                  <span className="font-serif text-2xl font-bold" style={{ color: result.color }}>
                    {result.grade}
                  </span>
                  <span className="text-lg font-medium text-[#1e3318]">{result.label}</span>
                </div>
                <div className="mx-auto mb-2 max-w-[220px] overflow-hidden rounded-full bg-[#e8e0cc]">
                  <div
                    className="h-3 rounded-full"
                    style={{ width: `${result.total}%`, backgroundColor: result.color }}
                  />
                </div>
                <p className="text-sm leading-6 text-[#5a7050]">{result.bandDescription}</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-[#f0f7ed] p-6">
                  <p className="editorial-kicker mb-2 text-[#3a5c2f]">Microbial condition</p>
                  <h3 className="font-serif text-2xl text-[#1e3318]">
                    {result.microbialCondition}
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-[#5a7050]">{result.summary}</p>
                </div>
                <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-6">
                  <p className="editorial-kicker mb-2 text-[#3a5c2f]">Habitat and confidence</p>
                  <p className="font-serif text-2xl text-[#1e3318]">{result.primaryConstraint}</p>
                  <p className="mt-3 text-sm leading-6 text-[#5a7050]">{result.habitatCondition}</p>
                  <p className="mt-4 text-xs leading-5 text-[#7b8e72]">{result.confidence}</p>
                </div>
              </div>

              <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-7 shadow-sm">
                <div className="mb-5 flex items-start justify-between gap-4">
                  <div>
                    <p className="editorial-kicker mb-2 text-[#3a5c2f]">Fungal : Bacterial Ratio</p>
                    <p className="font-serif text-4xl font-bold text-[#1e3318]">
                      {result.ratio.toFixed(1)}:1
                    </p>
                  </div>
                  <div className="rounded-2xl bg-[#f8f5ef] px-4 py-3 text-right">
                    <p className="text-xs uppercase tracking-[0.15em] text-[#6a8060]">
                      Target band
                    </p>
                    <p className="mt-1 text-sm font-semibold text-[#1e3318]">
                      {result.ratioTarget}
                    </p>
                  </div>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  {result.insights.map((insight) => (
                    <div
                      key={insight.title}
                      className={`rounded-2xl border p-4 ${
                        insight.tone === "positive"
                          ? "border-[rgba(47,125,70,0.12)] bg-[rgba(47,125,70,0.05)]"
                          : insight.tone === "critical"
                            ? "border-[rgba(191,75,62,0.12)] bg-[rgba(191,75,62,0.05)]"
                            : "border-[rgba(201,128,54,0.12)] bg-[rgba(201,128,54,0.05)]"
                      }`}
                    >
                      <p className="text-sm font-semibold text-[#1e3318]">{insight.title}</p>
                      <p className="mt-2 text-sm leading-6 text-[#5a7050]">{insight.detail}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-3xl border border-[rgba(58,92,47,0.12)] bg-white p-7 shadow-sm">
                <h3 className="mb-5 font-serif text-lg text-[#1e3318]">Indicator breakdown</h3>
                <div className="space-y-4">
                  {result.components.map((component) => (
                    <div key={component.key}>
                      <div className="mb-1.5 flex items-start justify-between gap-4 text-xs">
                        <div>
                          <span className="font-medium text-[#3d5035]">{component.name}</span>
                          <span
                            className={`ml-2 inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] ${componentStatusPill(component.status)}`}
                          >
                            {component.status}
                          </span>
                        </div>
                        <span className="text-right text-[#6a8060]">
                          <span className="font-semibold text-[#1e3318]">{component.score}</span>/
                          {component.max} - {component.note}
                        </span>
                      </div>
                      <ScoreBar score={component.score} max={component.max} color={result.color} />
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-3xl bg-[#1e3318] p-7 shadow-sm">
                <h3 className="mb-4 font-serif text-lg text-white">Priority management advice</h3>
                <div className="space-y-3">
                  {result.recommendations.map((recommendation, index) => (
                    <div
                      key={`${recommendation.title}-${index}`}
                      className={`rounded-2xl border p-4 ${recommendationStyles(recommendation.priority)}`}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-semibold">{recommendation.title}</p>
                        <span className="rounded-full bg-white/70 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.12em]">
                          {recommendation.priority}
                        </span>
                      </div>
                      <p className="mt-2 text-sm leading-6">{recommendation.detail}</p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export function SilkSoilClient({ userName, activeFormula }: SilkSoilClientProps) {
  if (!userName) {
    return <SilkSoilTeaser />;
  }

  return <SilkSoilCalculator userName={userName} activeFormula={activeFormula} />;
}
