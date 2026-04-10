import * as XLSX from "xlsx";

import type {
  CalculatorEquationDefinition,
  CalculatorFormulaPayload,
  CalculatorWeight,
  ScoreBand,
} from "@/lib/cmsTypes";

const DEFAULT_SUPPORTED_INDICATORS = [
  "ph",
  "organic_matter",
  "microbial_activity",
  "fungal_bacterial_ratio",
  "moisture",
  "temperature",
] as const;

type SheetRow = Record<string, string | number | boolean | null | undefined>;
type WorkbookAliases = Record<string, string>;

function normalizeKey(value: string) {
  return value
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_")
    .replace(/[^a-z0-9_]/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_|_$/g, "");
}

function valueAsString(value: unknown) {
  if (value == null) return "";
  return String(value).trim();
}

function valueAsNumber(value: unknown, fallback = 0) {
  const parsed = Number(String(value ?? "").trim());
  return Number.isFinite(parsed) ? parsed : fallback;
}

function rowsForSheet(workbook: XLSX.WorkBook, sheetName: string): SheetRow[] {
  const sheet = workbook.Sheets[sheetName];
  if (!sheet) return [];
  return XLSX.utils.sheet_to_json<SheetRow>(sheet, {
    defval: "",
    raw: false,
  });
}

function metadataFromSheet(rows: SheetRow[]) {
  const metadata: Record<string, string> = {};
  for (const row of rows) {
    const key = normalizeKey(valueAsString(row.key ?? row.Key ?? row.field ?? row.Field));
    const value = valueAsString(row.value ?? row.Value ?? row.setting ?? row.Setting);
    if (key) {
      metadata[key] = value;
    }
  }
  return metadata;
}

function parseWeights(rows: SheetRow[]): Record<string, CalculatorWeight> {
  const weights: Record<string, CalculatorWeight> = {};
  for (const row of rows) {
    const indicator = normalizeKey(
      valueAsString(row.indicator ?? row.parameter ?? row.metric ?? row.name),
    );
    if (!indicator) continue;
    const weightPercent = valueAsNumber(row.weight ?? row.weight_percent ?? row.weight_pct, 0);
    weights[indicator] = {
      weight: weightPercent > 1 ? weightPercent / 100 : weightPercent,
      optimal_min: valueAsNumber(row.optimal_min ?? row.min ?? row.minimum, 0),
      optimal_max: valueAsNumber(row.optimal_max ?? row.max ?? row.maximum, 100),
      description: valueAsString(row.description ?? row.notes ?? row.note),
    };
  }
  return weights;
}

function parseScoreBands(rows: SheetRow[]): ScoreBand[] {
  return rows
    .map((row) => ({
      min: valueAsNumber(row.min ?? row.minimum, 0),
      max: valueAsNumber(row.max ?? row.maximum, 100),
      label: valueAsString(row.label ?? row.band ?? row.name) || "Band",
      color: valueAsString(row.color ?? row.hex) || "#5d8b3f",
      description: valueAsString(row.description ?? row.notes ?? row.note),
    }))
    .filter((band) => band.label);
}

function parseEquations(rows: SheetRow[]): CalculatorEquationDefinition[] {
  const equations: CalculatorEquationDefinition[] = [];
  for (const row of rows) {
    const key = normalizeKey(valueAsString(row.key ?? row.metric ?? row.name));
    let expression = valueAsString(row.expression ?? row.formula ?? row.equation);
    if (!key || !expression) continue;
    if (expression.startsWith("=")) {
      expression = expression.slice(1);
    }

    const normalizedCategory = normalizeKey(valueAsString(row.category));
    const category =
      normalizedCategory === "chemistry" ||
      normalizedCategory === "habitat" ||
      normalizedCategory === "biology" ||
      normalizedCategory === "balance" ||
      normalizedCategory === "overall"
        ? normalizedCategory
        : undefined;

    equations.push({
      key,
      label: valueAsString(row.label ?? row.metric ?? row.name) || key,
      expression,
      description: valueAsString(row.description ?? row.notes ?? row.note) || undefined,
      category,
      max_points: row.max_points != null ? valueAsNumber(row.max_points, 100) : undefined,
      weight: row.weight != null ? valueAsNumber(row.weight, 0) : undefined,
    });
  }
  return equations;
}

function parseAliases(rows: SheetRow[]): WorkbookAliases {
  const aliases: WorkbookAliases = {};
  for (const row of rows) {
    const alias = normalizeKey(valueAsString(row.alias ?? row.input ?? row.variable ?? row.name));
    const target = normalizeKey(
      valueAsString(row.target ?? row.maps_to ?? row.field ?? row.metric),
    );
    if (alias && target) {
      aliases[alias] = target;
    }
  }
  return aliases;
}

function normalizeExcelExpression(expression: string, aliases: WorkbookAliases) {
  let normalized = expression.trim();
  if (normalized.startsWith("=")) {
    normalized = normalized.slice(1);
  }

  const replacements: Array<[RegExp, string]> = [
    [/\^/g, "**"],
    [/<>/g, "!="],
    [/\bIF\s*\(/gi, "ifFn("],
    [/\bMIN\s*\(/gi, "min("],
    [/\bMAX\s*\(/gi, "max("],
    [/\bABS\s*\(/gi, "abs("],
    [/\bROUND\s*\(/gi, "roundFn("],
    [/\bAVERAGE\s*\(/gi, "avg("],
    [/\bSUM\s*\(/gi, "sum("],
    [/\bAND\s*\(/gi, "andFn("],
    [/\bOR\s*\(/gi, "orFn("],
    [/\bNOT\s*\(/gi, "notFn("],
  ];

  for (const [pattern, replacement] of replacements) {
    normalized = normalized.replace(pattern, replacement);
  }

  for (const [alias, target] of Object.entries(aliases)) {
    const escaped = alias.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    normalized = normalized.replace(new RegExp(`\\b${escaped}\\b`, "gi"), target);
  }

  return normalized;
}

function fallbackPayload(fileName: string): CalculatorFormulaPayload {
  return {
    version: "excel-import",
    name: fileName.replace(/\.[^.]+$/, ""),
    description: "Imported from spreadsheet calculator workbook.",
    research_background: "",
    research_sources: [],
    target_systems: [],
    validation_notes: "",
    supported_indicators: [...DEFAULT_SUPPORTED_INDICATORS],
    weights: {},
    score_bands: [],
    equations: [],
    workbook_import: {
      file_name: fileName,
      parser_version: "1.0",
      imported_at: new Date().toISOString(),
      workbook_mode: "spreadsheet-import",
      sheet_names: [],
    },
  };
}

function rowsForLikelySheet(workbook: XLSX.WorkBook, candidates: string[]) {
  const matched = workbook.SheetNames.find((sheetName) =>
    candidates.includes(normalizeKey(sheetName)),
  );
  if (!matched) return [];
  return rowsForSheet(workbook, matched);
}

export async function importCalculatorWorkbook(file: File): Promise<CalculatorFormulaPayload> {
  const bytes = await file.arrayBuffer();
  const workbook = XLSX.read(bytes, { type: "array", cellFormula: true });

  const payload = fallbackPayload(file.name);
  payload.workbook_import = {
    ...payload.workbook_import,
    sheet_names: workbook.SheetNames,
    parser_version: "1.1",
    supported_features: [
      "metadata",
      "weights",
      "score_bands",
      "equations",
      "aliases",
      "excel-style IF/MIN/MAX/SUM/AVERAGE/ROUND support",
      "total_score override",
    ],
    compatibility_notes: [],
  };

  const metadataRows = rowsForLikelySheet(workbook, ["metadata", "meta", "settings"]);
  const weightRows = rowsForLikelySheet(workbook, ["weights", "indicators", "parameters"]);
  const scoreBandRows = rowsForLikelySheet(workbook, ["score_bands", "bands", "scorebands"]);
  const equationRows = rowsForLikelySheet(workbook, ["equations", "formulas", "calculator"]);
  const aliasRows = rowsForLikelySheet(workbook, ["aliases", "inputs", "input_map", "mapping"]);

  const metadata = metadataFromSheet(metadataRows);
  const weights = parseWeights(weightRows);
  const scoreBands = parseScoreBands(scoreBandRows);
  const aliases = parseAliases(aliasRows);
  const equations = parseEquations(equationRows).map((equation) => ({
    ...equation,
    expression: normalizeExcelExpression(equation.expression, aliases),
  }));

  payload.version = metadata.version || payload.version;
  payload.name = metadata.name || payload.name;
  payload.description = metadata.description || payload.description;
  payload.research_background = metadata.research_background || "";
  payload.validation_notes = metadata.validation_notes || "";
  payload.target_systems = metadata.target_systems
    ? metadata.target_systems
        .split(/[,;\n]/)
        .map((item) => item.trim())
        .filter(Boolean)
    : [];
  payload.research_sources = metadata.research_sources
    ? metadata.research_sources
        .split(/\n|;/)
        .map((item) => item.trim())
        .filter(Boolean)
    : [];
  payload.supported_indicators = metadata.supported_indicators
    ?.split(/[,;\n]/)
    .map((item) => normalizeKey(item))
    .filter(Boolean) ?? [...DEFAULT_SUPPORTED_INDICATORS];
  payload.weights =
    Object.keys(weights).length > 0
      ? weights
      : {
          ph: {
            weight: 0.15,
            optimal_min: 6,
            optimal_max: 7,
            description: "Default pH scoring band",
          },
        };
  payload.score_bands =
    scoreBands.length > 0
      ? scoreBands
      : [
          {
            min: 0,
            max: 59,
            label: "Needs attention",
            color: "#bf4b3e",
            description: "The imported workbook did not define score bands.",
          },
          {
            min: 60,
            max: 100,
            label: "Operational",
            color: "#2f7d46",
            description: "Default fallback band after workbook import.",
          },
        ];
  payload.equations = equations;
  if (!equationRows.length) {
    payload.workbook_import.compatibility_notes?.push(
      "No equations sheet detected. The imported calculator will rely on weights and score bands only.",
    );
  }
  if (aliasRows.length) {
    payload.workbook_import.compatibility_notes?.push(
      `Mapped ${Object.keys(aliases).length} workbook aliases onto SilkSoil variables.`,
    );
  }
  if (!weightRows.length) {
    payload.workbook_import.compatibility_notes?.push(
      "No weights sheet detected. Fallback weights were applied.",
    );
  }

  return payload;
}
