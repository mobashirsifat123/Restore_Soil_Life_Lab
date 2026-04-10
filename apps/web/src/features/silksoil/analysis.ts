import type {
  CalculatorEquationDefinition,
  CalculatorFormulaPayload,
  ScoreBand,
} from "@/lib/cmsTypes";

export type ProductionSystemKey =
  | "annual_row_crop"
  | "vegetables"
  | "pasture"
  | "orchard_perennial"
  | "vineyard"
  | "forestry_restoration";

export type SoilTextureKey = "sand" | "loam" | "clay";

export type SilkSoilInputs = {
  productionSystem: ProductionSystemKey;
  soilTexture: SoilTextureKey;
  ph: number;
  organicMatter: number;
  moisture: number;
  temperature: number;
  bacteria: number;
  fungi: number;
  protozoa: number;
  nematodes: number;
  compaction: number;
  nitrateN: number;
};

export type ScoreComponent = {
  key: string;
  name: string;
  score: number;
  max: number;
  note: string;
  category: "chemistry" | "habitat" | "biology" | "balance";
  status: "strong" | "watch" | "weak";
};

export type HealthInsight = {
  title: string;
  detail: string;
  tone: "positive" | "watch" | "critical";
};

export type HealthRecommendation = {
  title: string;
  detail: string;
  priority: "High" | "Medium" | "Maintain";
};

export type HealthScore = {
  total: number;
  grade: string;
  label: string;
  color: string;
  bandDescription: string;
  confidence: string;
  summary: string;
  microbialCondition: string;
  habitatCondition: string;
  primaryConstraint: string;
  ratio: number;
  ratioTarget: string;
  components: ScoreComponent[];
  insights: HealthInsight[];
  recommendations: HealthRecommendation[];
};

type Range = [number, number];

type ProductionProfile = {
  label: string;
  fungalBacterialRatio: Range;
  bacteria: Range;
  fungi: Range;
  nitrate: Range;
  summary: string;
};

type TextureProfile = {
  label: string;
  moisture: Range;
  organicMatter: Range;
  compactionIdealMax: number;
  compactionSevere: number;
};

const DEFAULT_FORMULA: CalculatorFormulaPayload = {
  version: "2.0",
  name: "SilkSoil Reference Model",
  description:
    "Weighted composite score from chemistry, habitat, microbial abundance, and fungal:bacterial balance.",
  weights: {
    ph: {
      weight: 0.15,
      optimal_min: 6,
      optimal_max: 7,
      description: "Soil pH reference band for most biologically active agricultural soils.",
    },
    organic_matter: {
      weight: 0.2,
      optimal_min: 3,
      optimal_max: 8,
      description:
        "Organic matter range supporting stable aggregation, water holding, and food-web recovery.",
    },
    microbial_activity: {
      weight: 0.25,
      optimal_min: 60,
      optimal_max: 100,
      description:
        "Composite microbial abundance score from bacteria, fungi, protozoa, and nematodes.",
    },
    fungal_bacterial_ratio: {
      weight: 0.2,
      optimal_min: 1,
      optimal_max: 5,
      description: "Fungal:bacterial balance relative to land-use intensity and crop system.",
    },
    moisture: {
      weight: 0.1,
      optimal_min: 30,
      optimal_max: 60,
      description:
        "Moisture band broad enough to support oxygen and microbial cycling without saturation stress.",
    },
    temperature: {
      weight: 0.1,
      optimal_min: 18,
      optimal_max: 28,
      description:
        "Typical range where soil biological activity remains strong in field conditions.",
    },
  },
  score_bands: [
    {
      min: 0,
      max: 39,
      label: "Severely constrained",
      color: "#bf4b3e",
      description:
        "The soil food web is heavily constrained. Address structure, carbon, and biology together.",
    },
    {
      min: 40,
      max: 59,
      label: "Recovering",
      color: "#c98036",
      description:
        "Biology is present but several limiting factors are suppressing consistent nutrient cycling.",
    },
    {
      min: 60,
      max: 74,
      label: "Functional",
      color: "#baa14d",
      description:
        "The soil is functioning, but targeted management can still improve resilience and food-web balance.",
    },
    {
      min: 75,
      max: 89,
      label: "Strong",
      color: "#5d8b3f",
      description:
        "The soil food web is active and resilient. Focus on protecting gains and refining balance.",
    },
    {
      min: 90,
      max: 100,
      label: "Highly resilient",
      color: "#2f7d46",
      description:
        "The biological engine is strong and balanced for the selected production system.",
    },
  ],
};

const PRODUCTION_PROFILES: Record<ProductionSystemKey, ProductionProfile> = {
  annual_row_crop: {
    label: "Annual row crop",
    fungalBacterialRatio: [0.3, 0.9],
    bacteria: [90, 180],
    fungi: [70, 160],
    nitrate: [12, 28],
    summary:
      "Annual row crops typically perform best with strong bacterial cycling and a restrained fungal load.",
  },
  vegetables: {
    label: "Vegetables",
    fungalBacterialRatio: [0.4, 1.1],
    bacteria: [95, 190],
    fungi: [90, 180],
    nitrate: [15, 35],
    summary:
      "Vegetable systems benefit from quick bacterial cycling, but still need enough fungal structure to prevent collapse.",
  },
  pasture: {
    label: "Pasture",
    fungalBacterialRatio: [0.8, 1.8],
    bacteria: [80, 160],
    fungi: [120, 240],
    nitrate: [8, 24],
    summary: "Pasture soils generally perform best with a more even bacterial and fungal balance.",
  },
  orchard_perennial: {
    label: "Orchard or perennial crop",
    fungalBacterialRatio: [1.5, 4],
    bacteria: [70, 150],
    fungi: [180, 320],
    nitrate: [8, 22],
    summary: "Perennial systems usually benefit from a distinctly fungal-leaning soil food web.",
  },
  vineyard: {
    label: "Vineyard",
    fungalBacterialRatio: [1.2, 3.5],
    bacteria: [70, 150],
    fungi: [160, 300],
    nitrate: [8, 22],
    summary:
      "Vineyard soils often perform better when fungi help stabilize structure and moderate nitrogen release.",
  },
  forestry_restoration: {
    label: "Forestry or restoration",
    fungalBacterialRatio: [3, 10],
    bacteria: [60, 130],
    fungi: [220, 380],
    nitrate: [5, 18],
    summary:
      "Low-disturbance restoration soils tend to be strongly fungal-dominant and slower-cycling.",
  },
};

const TEXTURE_PROFILES: Record<SoilTextureKey, TextureProfile> = {
  sand: {
    label: "Sandy soil",
    moisture: [20, 45],
    organicMatter: [2.5, 5],
    compactionIdealMax: 250,
    compactionSevere: 450,
  },
  loam: {
    label: "Loam",
    moisture: [30, 55],
    organicMatter: [3.5, 6.5],
    compactionIdealMax: 300,
    compactionSevere: 500,
  },
  clay: {
    label: "Clay soil",
    moisture: [35, 60],
    organicMatter: [4, 8],
    compactionIdealMax: 350,
    compactionSevere: 550,
  },
};

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function round(value: number) {
  return Math.round(value);
}

function resolveFormula(formula?: CalculatorFormulaPayload | null) {
  if (!formula?.weights || !formula?.score_bands?.length) {
    return DEFAULT_FORMULA;
  }

  return {
    ...DEFAULT_FORMULA,
    ...formula,
    weights: {
      ...DEFAULT_FORMULA.weights,
      ...formula.weights,
    },
    score_bands: formula.score_bands,
  };
}

type EquationContext = Record<string, number | string>;

function toSafeIdentifier(value: string) {
  return value.replace(/[^a-zA-Z0-9_$]/g, "_");
}

function evaluateExpression(expression: string, context: EquationContext) {
  if (!expression.trim()) return 0;

  const allowedPattern = /^[a-zA-Z0-9_+\-*/().,<>=!?: %|&[\]]+$/;
  if (!allowedPattern.test(expression)) {
    throw new Error(`Unsupported expression syntax: ${expression}`);
  }

  const helperEntries = Object.entries({
    min: Math.min,
    max: Math.max,
    abs: Math.abs,
    round: Math.round,
    roundFn: (value: number, decimals = 0) => {
      const factor = 10 ** decimals;
      return Math.round(value * factor) / factor;
    },
    floor: Math.floor,
    ceil: Math.ceil,
    sqrt: Math.sqrt,
    pow: Math.pow,
    sum: (...values: number[]) => values.reduce((acc, value) => acc + value, 0),
    avg: (...values: number[]) =>
      values.length ? values.reduce((acc, value) => acc + value, 0) / values.length : 0,
    ifFn: (condition: unknown, whenTrue: number, whenFalse: number) =>
      condition ? whenTrue : whenFalse,
    andFn: (...values: unknown[]) => values.every(Boolean),
    orFn: (...values: unknown[]) => values.some(Boolean),
    notFn: (value: unknown) => !value,
    clamp: (value: number, minValue: number, maxValue: number) =>
      Math.min(maxValue, Math.max(minValue, value)),
  });

  const variableEntries = Object.entries(context).map(
    ([key, value]) => [toSafeIdentifier(key), value] as const,
  );
  const argNames = [...helperEntries.map(([key]) => key), ...variableEntries.map(([key]) => key)];
  const argValues = [
    ...helperEntries.map(([, value]) => value),
    ...variableEntries.map(([, value]) => value),
  ];

  // Formulas are admin-authored only, and restricted to simple math + helper functions.
  const evaluator = new Function(...argNames, `return (${expression});`) as (
    ...args: unknown[]
  ) => unknown;
  const result = evaluator(...argValues);
  return typeof result === "number" && Number.isFinite(result) ? result : Number(result) || 0;
}

function evaluateImportedEquations(
  equations: CalculatorEquationDefinition[] | undefined,
  context: EquationContext,
) {
  const values: Record<string, number> = {};

  for (const equation of equations ?? []) {
    try {
      values[equation.key] = evaluateExpression(equation.expression, {
        ...context,
        ...values,
      });
    } catch {
      values[equation.key] = 0;
    }
  }

  return values;
}

function scoreRange(value: number, min: number, max: number, bufferMultiplier = 1.25) {
  const span = Math.max(max - min, 0.1);
  const lower = Math.max(0, min - span * bufferMultiplier);
  const upper = max + span * bufferMultiplier;

  if (value >= min && value <= max) {
    return 100;
  }

  if (value < min) {
    return round(clamp(((value - lower) / (min - lower)) * 100, 0, 100));
  }

  return round(clamp(((upper - value) / (upper - max)) * 100, 0, 100));
}

function scoreUpperBound(value: number, idealMax: number, severeMax: number) {
  if (value <= idealMax) {
    return 100;
  }

  if (value >= severeMax) {
    return 0;
  }

  return round(clamp(((severeMax - value) / (severeMax - idealMax)) * 100, 0, 100));
}

function weightedAverage(parts: Array<{ score: number; weight: number }>) {
  const totalWeight = parts.reduce((sum, item) => sum + item.weight, 0) || 1;
  const total = parts.reduce((sum, item) => sum + item.score * item.weight, 0);
  return total / totalWeight;
}

function statusFor(score: number): ScoreComponent["status"] {
  if (score >= 80) {
    return "strong";
  }

  if (score >= 60) {
    return "watch";
  }

  return "weak";
}

function gradeFor(total: number) {
  if (total >= 90) {
    return "A+";
  }

  if (total >= 80) {
    return "A";
  }

  if (total >= 70) {
    return "B";
  }

  if (total >= 60) {
    return "C";
  }

  if (total >= 45) {
    return "D";
  }

  return "F";
}

function bandFor(total: number, bands: ScoreBand[]) {
  return (
    bands.find((band) => total >= band.min && total <= band.max) ??
    bands[bands.length - 1] ??
    DEFAULT_FORMULA.score_bands[0]
  );
}

function pointsFor(score: number, maxPoints: number) {
  return round((score / 100) * maxPoints);
}

function maxPointsFor(value: number) {
  return Math.max(1, round(value));
}

function limitersFrom(components: ScoreComponent[]) {
  return [...components]
    .sort((left, right) => left.score / left.max - right.score / right.max)
    .slice(0, 3);
}

function strengthsFrom(components: ScoreComponent[]) {
  return [...components]
    .sort((left, right) => right.score / right.max - left.score / left.max)
    .slice(0, 2);
}

export const silkSoilOptions = {
  productionSystems: Object.entries(PRODUCTION_PROFILES).map(([value, profile]) => ({
    value: value as ProductionSystemKey,
    label: profile.label,
  })),
  soilTextures: Object.entries(TEXTURE_PROFILES).map(([value, profile]) => ({
    value: value as SoilTextureKey,
    label: profile.label,
  })),
};

export function calculateSoilHealth(
  inputs: SilkSoilInputs,
  formula?: CalculatorFormulaPayload | null,
): HealthScore {
  const activeFormula = resolveFormula(formula);
  const productionProfile = PRODUCTION_PROFILES[inputs.productionSystem];
  const textureProfile = TEXTURE_PROFILES[inputs.soilTexture];

  const ratio = inputs.fungi / Math.max(1, inputs.bacteria);
  const pHScore = scoreRange(
    inputs.ph,
    activeFormula.weights.ph.optimal_min,
    activeFormula.weights.ph.optimal_max,
    1.1,
  );
  const organicMatterScore = scoreRange(
    inputs.organicMatter,
    Math.max(activeFormula.weights.organic_matter.optimal_min, textureProfile.organicMatter[0]),
    Math.max(activeFormula.weights.organic_matter.optimal_max, textureProfile.organicMatter[1]),
    1.2,
  );
  const nitrateScore = scoreRange(
    inputs.nitrateN,
    productionProfile.nitrate[0],
    productionProfile.nitrate[1],
    1,
  );
  const moistureScore = scoreRange(
    inputs.moisture,
    textureProfile.moisture[0],
    textureProfile.moisture[1],
    0.9,
  );
  const compactionScore = scoreUpperBound(
    inputs.compaction,
    textureProfile.compactionIdealMax,
    textureProfile.compactionSevere,
  );
  const temperatureScore = scoreRange(
    inputs.temperature,
    activeFormula.weights.temperature.optimal_min,
    activeFormula.weights.temperature.optimal_max,
    0.8,
  );
  const bacteriaScore = scoreRange(
    inputs.bacteria,
    productionProfile.bacteria[0],
    productionProfile.bacteria[1],
    1.1,
  );
  const fungiScore = scoreRange(
    inputs.fungi,
    productionProfile.fungi[0],
    productionProfile.fungi[1],
    1.25,
  );
  const protozoaScore = scoreRange(inputs.protozoa, 5, 18, 1.6);
  const nematodeScore = scoreRange(inputs.nematodes, 40, 140, 1.4);
  const ratioScore = scoreRange(
    ratio,
    productionProfile.fungalBacterialRatio[0],
    productionProfile.fungalBacterialRatio[1],
    1.35,
  );

  const chemistryComposite = weightedAverage([
    { score: organicMatterScore, weight: 0.65 },
    { score: nitrateScore, weight: 0.35 },
  ]);
  const habitatComposite = weightedAverage([
    { score: moistureScore, weight: 0.6 },
    { score: compactionScore, weight: 0.4 },
  ]);
  const microbialActivityScore = weightedAverage([
    { score: bacteriaScore, weight: 0.28 },
    { score: fungiScore, weight: 0.32 },
    { score: protozoaScore, weight: 0.2 },
    { score: nematodeScore, weight: 0.2 },
  ]);

  const importedEquationValues = evaluateImportedEquations(activeFormula.equations, {
    ...inputs,
    ratio,
    pHScore,
    organicMatterScore,
    nitrateScore,
    moistureScore,
    compactionScore,
    temperatureScore,
    bacteriaScore,
    fungiScore,
    protozoaScore,
    nematodeScore,
    ratioScore,
    chemistryComposite,
    habitatComposite,
    microbialActivityScore,
  });

  const rawWeights = {
    ph: activeFormula.weights.ph.weight,
    chemistry: activeFormula.weights.organic_matter.weight,
    microbial: activeFormula.weights.microbial_activity.weight,
    ratio: activeFormula.weights.fungal_bacterial_ratio.weight,
    habitat: activeFormula.weights.moisture.weight,
    temperature: activeFormula.weights.temperature.weight,
  };

  const weightTotal = Object.values(rawWeights).reduce((sum, value) => sum + value, 0) || 1;
  const weights = Object.fromEntries(
    Object.entries(rawWeights).map(([key, value]) => [key, (value / weightTotal) * 100]),
  ) as Record<keyof typeof rawWeights, number>;

  const total = round(
    importedEquationValues.total_score ??
      weightedAverage([
        { score: pHScore, weight: weights.ph },
        { score: chemistryComposite, weight: weights.chemistry },
        { score: microbialActivityScore, weight: weights.microbial },
        { score: ratioScore, weight: weights.ratio },
        { score: habitatComposite, weight: weights.habitat },
        { score: temperatureScore, weight: weights.temperature },
      ]),
  );

  const band = bandFor(total, activeFormula.score_bands);

  const components: ScoreComponent[] = [
    {
      key: "ph",
      name: "Soil pH",
      score: pointsFor(pHScore, weights.ph),
      max: maxPointsFor(weights.ph),
      note: `pH ${inputs.ph.toFixed(1)}`,
      category: "chemistry",
      status: statusFor(pHScore),
    },
    {
      key: "organicMatter",
      name: "Organic Matter",
      score: pointsFor(organicMatterScore, weights.chemistry * 0.65),
      max: maxPointsFor(weights.chemistry * 0.65),
      note: `${inputs.organicMatter.toFixed(1)}%`,
      category: "chemistry",
      status: statusFor(organicMatterScore),
    },
    {
      key: "nitrateN",
      name: "Nitrate-N",
      score: pointsFor(nitrateScore, weights.chemistry * 0.35),
      max: maxPointsFor(weights.chemistry * 0.35),
      note: `${inputs.nitrateN.toFixed(0)} ppm`,
      category: "chemistry",
      status: statusFor(nitrateScore),
    },
    {
      key: "bacteria",
      name: "Bacteria",
      score: pointsFor(bacteriaScore, weights.microbial * 0.28),
      max: maxPointsFor(weights.microbial * 0.28),
      note: `${inputs.bacteria.toFixed(0)} ug/g dry soil`,
      category: "biology",
      status: statusFor(bacteriaScore),
    },
    {
      key: "fungi",
      name: "Fungi",
      score: pointsFor(fungiScore, weights.microbial * 0.32),
      max: maxPointsFor(weights.microbial * 0.32),
      note: `${inputs.fungi.toFixed(0)} ug/g dry soil`,
      category: "biology",
      status: statusFor(fungiScore),
    },
    {
      key: "protozoa",
      name: "Protozoa",
      score: pointsFor(protozoaScore, weights.microbial * 0.2),
      max: maxPointsFor(weights.microbial * 0.2),
      note: `${inputs.protozoa.toFixed(1)} x 10^3/g`,
      category: "biology",
      status: statusFor(protozoaScore),
    },
    {
      key: "nematodes",
      name: "Nematodes",
      score: pointsFor(nematodeScore, weights.microbial * 0.2),
      max: maxPointsFor(weights.microbial * 0.2),
      note: `${inputs.nematodes.toFixed(0)} /100g`,
      category: "biology",
      status: statusFor(nematodeScore),
    },
    {
      key: "fbRatio",
      name: "F:B Ratio",
      score: pointsFor(ratioScore, weights.ratio),
      max: maxPointsFor(weights.ratio),
      note: `${ratio.toFixed(1)}:1`,
      category: "balance",
      status: statusFor(ratioScore),
    },
    {
      key: "moisture",
      name: "Moisture",
      score: pointsFor(moistureScore, weights.habitat * 0.6),
      max: maxPointsFor(weights.habitat * 0.6),
      note: `${inputs.moisture.toFixed(0)}%`,
      category: "habitat",
      status: statusFor(moistureScore),
    },
    {
      key: "compaction",
      name: "Compaction",
      score: pointsFor(compactionScore, weights.habitat * 0.4),
      max: maxPointsFor(weights.habitat * 0.4),
      note: `${inputs.compaction.toFixed(0)} psi`,
      category: "habitat",
      status: statusFor(compactionScore),
    },
    {
      key: "temperature",
      name: "Temperature",
      score: pointsFor(temperatureScore, weights.temperature),
      max: maxPointsFor(weights.temperature),
      note: `${inputs.temperature.toFixed(1)} C`,
      category: "habitat",
      status: statusFor(temperatureScore),
    },
  ];

  const importedComponents: ScoreComponent[] = (activeFormula.equations ?? [])
    .filter((equation) => equation.category && equation.category !== "overall")
    .map((equation) => {
      const score = importedEquationValues[equation.key] ?? 0;
      const max = equation.max_points ?? 100;
      const category =
        equation.category && equation.category !== "overall" ? equation.category : "biology";
      return {
        key: equation.key,
        name: equation.label,
        score: round(score),
        max: round(max),
        note: equation.description ?? equation.expression,
        category,
        status: statusFor((score / Math.max(max, 1)) * 100),
      } satisfies ScoreComponent;
    });

  const visibleComponents = importedComponents.length ? importedComponents : components;

  const limiters = limitersFrom(visibleComponents);
  const strengths = strengthsFrom(visibleComponents);

  const microbialCondition =
    microbialActivityScore >= 85
      ? "Robust microbial engine"
      : microbialActivityScore >= 70
        ? "Active but uneven biology"
        : microbialActivityScore >= 55
          ? "Recovering microbial community"
          : "Biology is underpowered";

  const habitatCondition =
    habitatComposite >= 80
      ? "Pore space, moisture, and aeration are broadly supportive."
      : habitatComposite >= 60
        ? "Physical habitat is usable, but moisture or compaction is holding back consistency."
        : "Physical stress is suppressing respiration, rooting, and nutrient cycling.";

  const confidence =
    nematodeScore < 40 || protozoaScore < 40
      ? "Moderate confidence - counts are useful, but food-web diversity is likely under-described."
      : "Good screening confidence - the measurements are sufficient for field-level management decisions.";

  const insights: HealthInsight[] = [
    {
      title: "Production-system fit",
      detail: `${productionProfile.summary} Current ratio target for this system is ${productionProfile.fungalBacterialRatio[0]}-${productionProfile.fungalBacterialRatio[1]}:1.`,
      tone: ratioScore >= 70 ? "positive" : "watch",
    },
    {
      title: "Microbial condition",
      detail: `${microbialCondition}. Strongest signals: ${strengths.map((item) => item.name).join(" and ")}.`,
      tone:
        microbialActivityScore >= 75
          ? "positive"
          : microbialActivityScore >= 55
            ? "watch"
            : "critical",
    },
    {
      title: "Primary limits",
      detail: `The biggest constraints right now are ${limiters.map((item) => item.name.toLowerCase()).join(", ")}.`,
      tone: limiters[0]?.status === "weak" ? "critical" : "watch",
    },
  ];

  const recommendations: Array<HealthRecommendation & { severity: number }> = [];

  if (compactionScore < 65) {
    recommendations.push({
      priority: "High",
      severity: 100 - compactionScore,
      title: "Open pore space before expecting biology to rebound",
      detail:
        "Penetrometer pressure is high for this soil texture. Reduce traffic on wet ground, keep living roots in place, and use deep-rooted cover crops before relying on inoculants alone.",
    });
  }

  if (fungiScore < 65 || ratioScore < 60) {
    recommendations.push({
      priority: "High",
      severity: 100 - Math.min(fungiScore, ratioScore),
      title: "Rebuild fungal habitat",
      detail:
        "Use lower-disturbance management, retain residue, and add more lignified carbon such as mulches or composts that do not overly favor only fast bacterial flushes.",
    });
  }

  if (bacteriaScore < 65) {
    recommendations.push({
      priority: "High",
      severity: 100 - bacteriaScore,
      title: "Strengthen the bacterial engine",
      detail:
        "Keep roots actively feeding the rhizosphere, maintain residue cover, and avoid long bare-soil periods so bacterial nutrient cycling can recover.",
    });
  }

  if (protozoaScore < 60 || nematodeScore < 60) {
    recommendations.push({
      priority: "Medium",
      severity: 100 - Math.min(protozoaScore, nematodeScore),
      title: "Restore grazing pressure in the food web",
      detail:
        "Low grazer counts suggest bacteria and fungi may not be turning over efficiently. Prioritize mature composts, biologically active extracts, and reduced chemical shocks to support trophic recovery.",
    });
  }

  if (organicMatterScore < 65) {
    recommendations.push({
      priority: "High",
      severity: 100 - organicMatterScore,
      title: "Increase stable carbon inputs",
      detail:
        "Organic matter is below the reference band for this texture. Add compost, protect crop residues, and increase root duration with multispecies cover crops to build a larger biological habitat.",
    });
  }

  if (pHScore < 65) {
    recommendations.push({
      priority: "Medium",
      severity: 100 - pHScore,
      title: "Correct pH gradually",
      detail:
        inputs.ph < activeFormula.weights.ph.optimal_min
          ? "The soil is more acidic than the reference band. Correct gradually with a lime strategy that matches your buffer pH and crop tolerance."
          : "The soil is more alkaline than the reference band. Use acidifying amendments carefully and avoid chasing pH too quickly in a single season.",
    });
  }

  if (moistureScore < 65) {
    recommendations.push({
      priority: "High",
      severity: 100 - moistureScore,
      title: "Stabilize moisture swings",
      detail:
        inputs.moisture < textureProfile.moisture[0]
          ? "The soil is running too dry for consistent microbial cycling. Protect the surface, improve infiltration, and shorten the time between living-root inputs."
          : "Moisture is running high enough to threaten aeration. Improve drainage, reduce compaction, and avoid keeping the soil saturated for long periods.",
    });
  }

  if (nitrateScore < 60) {
    recommendations.push({
      priority: "Medium",
      severity: 100 - nitrateScore,
      title: "Rebalance nitrogen management",
      detail:
        inputs.nitrateN > productionProfile.nitrate[1]
          ? "Nitrate is high for the selected system. Ease off soluble nitrogen where possible and rely more on biology plus organic matter to moderate release."
          : "Nitrate is low for the selected system. Pair biology-building practices with a measured fertility plan so crops do not stall while the food web recovers.",
    });
  }

  if (temperatureScore < 60) {
    recommendations.push({
      priority: "Medium",
      severity: 100 - temperatureScore,
      title: "Protect microbial temperature stability",
      detail:
        "Temperature is outside the most biologically active range. Surface cover, mulch, and continuous canopy help prevent large swings that slow respiration and nutrient cycling.",
    });
  }

  if (!recommendations.length) {
    recommendations.push({
      priority: "Maintain",
      severity: 0,
      title: "Protect the biology you already have",
      detail:
        "The current data suggest a well-functioning soil food web for this system. Maintain living roots, avoid unnecessary disturbance, and retest seasonally to catch drift early.",
    });
  }

  recommendations.sort((left, right) => right.severity - left.severity);

  return {
    total,
    grade: gradeFor(total),
    label: band.label,
    color: band.color,
    bandDescription: band.description,
    confidence,
    summary: `${band.description} ${productionProfile.summary}`,
    microbialCondition,
    habitatCondition,
    primaryConstraint: limiters[0]?.name ?? "None",
    ratio,
    ratioTarget: `${productionProfile.fungalBacterialRatio[0]}-${productionProfile.fungalBacterialRatio[1]}:1`,
    components: visibleComponents,
    insights,
    recommendations: recommendations.map((recommendation) => ({
      title: recommendation.title,
      detail: recommendation.detail,
      priority: recommendation.priority,
    })),
  };
}
