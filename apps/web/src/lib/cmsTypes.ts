export interface CmsPage {
  id: string;
  slug: string;
  title: string;
  meta_description?: string | null;
  hero_kicker?: string | null;
  hero_heading?: string | null;
  hero_subheading?: string | null;
  hero_image_url?: string | null;
  updated_at: string;
}

export interface BlogPostSummary {
  id: string;
  slug: string;
  category: string;
  title: string;
  excerpt?: string | null;
  cover_image_url?: string | null;
  author?: string | null;
  published_at?: string | null;
  is_featured: boolean;
  read_time_minutes?: number | null;
  created_at: string;
  updated_at: string;
}

export interface BlogPostDetail extends BlogPostSummary {
  body_markdown?: string | null;
}

export interface CalculatorWeight {
  weight: number;
  optimal_min: number;
  optimal_max: number;
  description: string;
}

export interface ScoreBand {
  min: number;
  max: number;
  label: string;
  color: string;
  description: string;
}

export interface CalculatorEquationDefinition {
  key: string;
  label: string;
  expression: string;
  description?: string;
  category?: "chemistry" | "habitat" | "biology" | "balance" | "overall";
  max_points?: number;
  weight?: number;
}

export interface CalculatorWorkbookImportMeta {
  file_name?: string;
  sheet_names?: string[];
  imported_at?: string;
  parser_version?: string;
  workbook_mode?: string;
  supported_features?: string[];
  compatibility_notes?: string[];
}

export interface CalculatorFormulaPayload {
  version?: string;
  name?: string;
  description?: string;
  research_background?: string;
  research_sources?: string[];
  target_systems?: string[];
  validation_notes?: string;
  supported_indicators?: string[];
  workbook_import?: CalculatorWorkbookImportMeta;
  equations?: CalculatorEquationDefinition[];
  weights: Record<string, CalculatorWeight>;
  score_bands: ScoreBand[];
}

export interface CalculatorFormula {
  id: string;
  name: string;
  is_active: boolean;
  formula_json: CalculatorFormulaPayload;
  changelog?: string | null;
  created_at: string;
  updated_at: string;
}

export interface MediaAsset {
  id: string;
  filename: string;
  url: string;
  alt_text?: string | null;
  mime_type?: string | null;
  byte_size?: number | null;
  uploaded_at: string;
}

export interface CmsPageResponse<TSections = Record<string, unknown>> {
  page: CmsPage;
  sections: TSections;
}

export type StatTile = { n: string; label: string };
export type Milestone = { year: string; text: string };
export type TeamMember = { name: string; role: string; bio: string; emoji?: string };
export type AboutFounder = {
  eyebrow?: string;
  label?: string;
  name?: string;
  image_url?: string;
  image_alt?: string;
  paragraph_one?: string;
  paragraph_two?: string;
  paragraph_three?: string;
  question_heading?: string;
  question_cta_label?: string;
  question_cta_link?: string;
};
export type AboutCredential = { text: string };
export type AboutIntroLegacy = {
  kicker?: string;
  heading?: string;
  image_url?: string;
  paragraphs?: string[];
};
export type HomeProblem = {
  title: string;
  subtitle: string;
  body: string;
  icon: string;
  link: string;
};
export type HomeStat = {
  number: string;
  label: string;
  sub: string;
};
export type Testimonial = {
  quote: string;
  author: string;
  role: string;
};
export type ScienceLevel = {
  level: number;
  name: string;
  members: string;
  color: string;
  description: string;
};
export type ScienceConcept = {
  id: string;
  icon: string;
  title: string;
  subtitle: string;
  body: string;
  detail: string;
};

export interface AboutSections {
  founder?: AboutFounder;
  founder_credentials?: AboutCredential[];
  team?: TeamMember[];
  milestones?: Milestone[];
  stats?: StatTile[];
  intro?: AboutIntroLegacy;
}

export interface ScienceSections {
  concepts?: ScienceConcept[];
  food_web_levels?: ScienceLevel[];
  stats?: StatTile[];
}

export interface HomeSections {
  problems?: HomeProblem[];
  stats?: HomeStat[];
  testimonials?: Testimonial[];
  calculator_spotlight?: Record<string, string>;
  about_section?: Record<string, string>;
}
