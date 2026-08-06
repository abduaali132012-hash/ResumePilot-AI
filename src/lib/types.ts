/* ───── Analysis result types ───── */

export interface CategoryScores {
  keywords: number;
  experience: number;
  format: number;
  impact: number;
}

export interface KeywordMatch {
  term: string;
  count: number;
}

export interface MissingKeyword {
  term: string;
  importance: "high" | "medium" | "low";
}

export interface Improvement {
  title: string;
  detail: string;
  priority: "high" | "medium" | "low";
  suggestion: string;
}

export interface ATSResult {
  overallScore: number;
  categoryScores: CategoryScores;
  matchedKeywords: KeywordMatch[];
  missingKeywords: MissingKeyword[];
  summary: string;
  strengths: string[];
  improvements: Improvement[];
  suggestedSummary: string;
  atsTips: string[];
}

export interface QAPair {
  question: string;
  why: string;
  sampleAnswer: string;
}

export interface InterviewResult {
  questions: QAPair[];
}

export interface CoverLetterResult {
  letter: string;
}

export interface RewriteSection {
  heading: string;
  original: string;
  rewritten: string;
  note: string;
}

export interface RewriteResult {
  sections: RewriteSection[];
}

export type AnalysisMode = "ats" | "cover-letter" | "interview" | "rewrite" | "career-gaps" | "salary-insights" | "linkedin";

export type AnalysisResult =
  | ATSResult
  | InterviewResult
  | CoverLetterResult
  | RewriteResult
  | CareerGapsResult
  | SalaryInsightsResult
  | LinkedInResult;

/* ───── Career Gap Analysis ───── */

export interface CareerGap {
  skill: string;
  importance: "high" | "medium" | "low";
  currentLevel: "none" | "basic" | "intermediate";
  recommendation: string;
  resource: string;
  platform: string;
  estimatedTime: string;
}

export interface CareerGapsResult {
  gaps: CareerGap[];
}

/* ───── Salary Insights ───── */

export interface SalaryRange {
  min: number;
  mid: number;
  max: number;
}

export interface SalaryInsightsResult {
  role: string;
  location: string;
  experienceLevel: string;
  salaryRange: SalaryRange;
  currency: string;
  marketPercentile: number;
  source: string;
  factors: string[];
  negotiationTips: string[];
}

/* ───── LinkedIn Profile Analysis ───── */

export interface LinkedInSection {
  section: string;
  current: string;
  suggestion: string;
  tip: string;
}

export interface LinkedInResult {
  headlineScore: number;
  aboutScore: number;
  experienceScore: number;
  overallScore: number;
  summary: string;
  strengths: string[];
  improvements: LinkedInSection[];
  profileTips: string[];
}

/* ───── Job Application Tracker ───── */

export type ApplicationStatus =
  | "saved"
  | "applied"
  | "phone-screen"
  | "interview"
  | "technical"
  | "offer"
  | "rejected"
  | "accepted"
  | "ghosted";

export interface JobApplication {
  id: string;
  user_id: string;
  company: string;
  role: string;
  url: string | null;
  salary_range: string | null;
  status: ApplicationStatus;
  notes: string | null;
  applied_date: string;
  created_at: string;
  updated_at: string;
}

/* ───── Saved analysis ───── */

export interface SavedAnalysis {
  id: string;
  user_id: string;
  mode: AnalysisMode;
  role?: string;
  resume_text: string;
  job_description: string;
  result: AnalysisResult;
  score?: number;
  created_at: string;
}