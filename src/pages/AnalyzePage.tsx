import { useState, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertCircle,
  DollarSign,
  FileText,
  MessageSquare,
  ScanSearch,
  Sparkles,
  Target,
  Wand2,
  Upload,
  X,
} from "lucide-react";
import { FaLinkedin } from "react-icons/fa6";
import { Button, Card, Tabs, TabItem, TextArea, Input } from "../components/ui";
import ResultsPanel from "../components/ResultsPanel";
import { supabase } from "../lib/supabase";
import { useAuth } from "../lib/store";
import type { AnalysisMode, AnalysisResult, ATSResult } from "../lib/types";

/* ───── Sample data ───── */
const SAMPLE_RESUME = `Alex Chen
alex.chen@email.com | (555) 123-4567 | linkedin.com/in/alexchen

PROFESSIONAL SUMMARY
Product Manager with 5+ years of experience leading cross-functional teams to deliver SaaS platforms. Skilled in user research, roadmap prioritization, and data-driven decision making. Successfully launched 3 products from concept to GA, driving $2.5M in ARR.

EXPERIENCE
Senior Product Manager | TechFlow Inc. | 2021 - Present
- Led the product strategy for a B2B analytics platform serving 200+ enterprise clients
- Defined and prioritized a 12-month roadmap, delivering 4 major releases on schedule
- Improved user engagement by 34% through A/B testing of onboarding flows
- Collaborated with engineering, design, and sales to align feature priorities with revenue goals

Product Manager | DataSync Corp | 2019 - 2021
- Managed the full lifecycle of a data integration tool from MVP to v2.0
- Conducted 50+ user interviews to identify pain points and validate feature concepts
- Drove a 28% increase in trial-to-paid conversion through UX improvements
- Created dashboards to track KPIs including MAU, retention, and NPS

EDUCATION
MBA, Stanford Graduate School of Business | 2019
B.S. Computer Science, UC Berkeley | 2015

SKILLS
Product Strategy | Roadmap Planning | User Research | A/B Testing | SQL | Python | Agile/Scrum | Figma | Jira | Amplitude | Tableau`;

const SAMPLE_JOB = `Senior Product Manager — AI Platform

About Us
NeuralMind is building the next-generation AI platform for enterprise customers. We're looking for a Senior Product Manager to lead our core product team.

Responsibilities
- Define and execute the product strategy and roadmap for the AI platform
- Work closely with ML engineers, designers, and customers to ship high-impact features
- Drive product discovery through user research, competitive analysis, and data insights
- Prioritize features based on business impact, customer needs, and technical feasibility
- Define and track KPIs, including adoption, engagement, retention, and revenue
- Present product updates and strategy to leadership and stakeholders

Requirements
- 5+ years of product management experience in SaaS or B2B environments
- Experience working on AI/ML products or platforms
- Strong analytical skills with proficiency in SQL and data visualization tools
- Excellent cross-functional communication and stakeholder management
- Track record of launching products from 0 to 1
- Experience with Agile development methodologies
- Bachelor's degree in Computer Science, Engineering, or related field

Preferred
- MBA or advanced degree
- Experience with LLMs, generative AI, or recommendation systems
- Experience working at a high-growth startup (Series A-C)
- Python or similar scripting language proficiency`;

const SAMPLE_LINKEDIN = `Alex Chen
Product Leader | AI & SaaS | Stanford MBA
San Francisco Bay Area

About
Product leader with 5+ years building B2B SaaS platforms at scale. Passionate about AI-powered products that transform how businesses operate. Stanford MBA graduate who combines strategic thinking with hands-on product execution. Led cross-functional teams to deliver products generating $2.5M+ in ARR.

Experience
Senior Product Manager at TechFlow Inc. (2021-Present)
- Lead product strategy for B2B analytics platform
- Defined 12-month roadmap and delivered 4 major releases
- Improved user engagement by 34%
- Collaborated with engineering, design, and sales teams

Product Manager at DataSync Corp (2019-2021)
- Managed data integration tool from MVP to v2.0
- Conducted 50+ user interviews
- Drove 28% increase in trial-to-paid conversion
- Created KPI dashboards

Education
MBA, Stanford Graduate School of Business
B.S. Computer Science, UC Berkeley

Skills
Product Strategy, Roadmap Planning, User Research, A/B Testing, SQL, Python, Agile, Figma, Jira, Amplitude, Tableau`;

/* ───── File upload zone ───── */
function FileUploadZone({
  onText,
  label,
}: {
  onText: (text: string) => void;
  label: string;
}) {
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    async (file: File) => {
      setError(null);
      if (!file.name.endsWith(".txt") && !file.name.endsWith(".pdf")) {
        setError("Please upload a .txt or .pdf file.");
        return;
      }
      if (file.size > 1024 * 1024) {
        setError("File must be under 1 MB.");
        return;
      }
      try {
        const text = await file.text();
        if (text.trim().length < 20) {
          setError("File appears to be empty or unreadable.");
          return;
        }
        onText(text);
        setFileName(file.name);
      } catch {
        setError("Could not read file. Try pasting the text instead.");
      }
    },
    [onText]
  );

  return (
    <div>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={async (e) => {
          e.preventDefault();
          setDragOver(false);
          const file = e.dataTransfer.files[0];
          if (file) await handleFile(file);
        }}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-xl border-2 border-dashed p-4 text-center transition-all duration-200 ${
          dragOver
            ? "border-primary/60 bg-primary/5"
            : fileName
            ? "border-accent/40 bg-accent/5"
            : "border-border hover:border-primary/40 hover:bg-muted/30"
        }`}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") inputRef.current?.click(); }}
        aria-label={`Upload ${label}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".txt,.pdf"
          className="hidden"
          onChange={async (e) => {
            const file = e.target.files?.[0];
            if (file) await handleFile(file);
            e.target.value = "";
          }}
        />
        {fileName ? (
          <div className="flex items-center justify-center gap-2 text-sm">
            <FileText className="size-4 text-accent" />
            <span className="font-medium text-accent">{fileName}</span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setFileName(null);
                onText("");
              }}
              className="ml-1 cursor-pointer rounded-full p-0.5 hover:bg-destructive/10 hover:text-destructive focus-ring"
              aria-label="Remove file"
            >
              <X className="size-3.5" />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-1.5">
            <Upload className="size-5 text-foreground/40" />
            <p className="text-xs text-foreground/50">
              <span className="font-medium text-foreground/70">Click to upload</span> or drag & drop a .txt or .pdf
            </p>
          </div>
        )}
      </div>
      {error && <p className="mt-1 text-xs text-destructive">{error}</p>}
    </div>
  );
}

/* ───── Tabs ───── */
const MODE_TABS: TabItem[] = [
  { id: "ats", label: "ATS Score", icon: <ScanSearch className="size-4" /> },
  { id: "cover-letter", label: "Cover Letter", icon: <FileText className="size-4" /> },
  { id: "interview", label: "Interview Prep", icon: <MessageSquare className="size-4" /> },
  { id: "rewrite", label: "Rewrite", icon: <Wand2 className="size-4" /> },
  { id: "career-gaps", label: "Career Gaps", icon: <Target className="size-4" /> },
  { id: "salary-insights", label: "Salary Insights", icon: <DollarSign className="size-4" /> },
  { id: "linkedin", label: "LinkedIn", icon: <FaLinkedin className="size-4" /> },
];

/* ───── Page ───── */
export default function AnalyzePage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [mode, setMode] = useState<AnalysisMode>("ats");
  const [resumeText, setResumeText] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [role, setRole] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [saved, setSaved] = useState(false);

  const handleAnalyze = useCallback(async () => {
    setError(null);
    setResult(null);
    setSaved(false);

    // LinkedIn mode only needs profile text
    if (mode === "linkedin") {
      if (!resumeText.trim() || resumeText.trim().length < 50) {
        setError("Please paste your LinkedIn profile text (at least 50 characters).");
        return;
      }
    } else {
      if (!resumeText.trim() || resumeText.trim().length < 50) {
        setError("Please enter your resume (at least 50 characters).");
        return;
      }
      if (!jobDesc.trim() || jobDesc.trim().length < 50) {
        setError("Please enter a job description (at least 50 characters).");
        return;
      }
    }

    setLoading(true);
    try {
      const body = mode === "linkedin"
        ? { mode, resumeText: resumeText.trim(), role: role.trim() || undefined }
        : { mode, resumeText: resumeText.trim(), jobDescription: jobDesc.trim(), role: role.trim() || undefined };

      const { data, error: fnErr } = await supabase.functions.invoke("analyze-resume", {
        body,
      });

      if (fnErr) throw new Error(fnErr.message || "Failed to analyze resume");
      if (data?.error) throw new Error(data.error);

      setResult(data as AnalysisResult);

      // Auto-save if signed in
      if (user && data) {
        const score = mode === "ats" ? (data as ATSResult).overallScore : null;
        await supabase.from("resume_analyses").insert({
          user_id: user.id,
          mode,
          role: role.trim() || null,
          resume_text: resumeText.trim(),
          job_description: jobDesc.trim(),
          result: data,
          score,
        });
        setSaved(true);
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Something went wrong. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [mode, resumeText, jobDesc, role, user]);

  const loadSample = () => {
    if (mode === "linkedin") {
      setResumeText(SAMPLE_LINKEDIN);
      setRole("Senior Product Manager");
    } else {
      setResumeText(SAMPLE_RESUME);
      setJobDesc(SAMPLE_JOB);
      setRole("Senior Product Manager");
    }
    setResult(null);
    setError(null);
  };

  const isLinkedIn = mode === "linkedin";

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:py-12">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="font-heading text-3xl font-extrabold text-foreground sm:text-4xl">
          {isLinkedIn ? <>LinkedIn Profile <span className="gradient-text">Analyzer</span></> : <>AI Resume <span className="gradient-text">Analyzer</span></>}
        </h1>
        <p className="mt-2 text-base text-foreground/60">
          {isLinkedIn
            ? "Paste your LinkedIn profile for an AI-powered optimisation analysis."
            : "Paste your resume and a job description — get an instant, AI-powered match analysis."}
        </p>
      </div>

      {/* Mode tabs */}
      <div className="mb-6 flex justify-center">
        <Tabs tabs={MODE_TABS} active={mode} onChange={(id) => { setMode(id as AnalysisMode); setResult(null); setError(null); }} />
      </div>

      {/* Saved indicator */}
      {saved && (
        <div className="mb-4 flex items-center justify-center gap-2 text-sm font-medium text-accent">
          <Sparkles className="size-4" />
          Analysis saved to your history
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left — Resume / LinkedIn Profile */}
        <Card className="p-5">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-sm font-medium text-foreground/80">
              {isLinkedIn ? "LinkedIn Profile" : "Resume"}
            </span>
            <FileUploadZone onText={setResumeText} label={isLinkedIn ? "LinkedIn profile" : "resume"} />
          </div>
          <TextArea
            placeholder={
              isLinkedIn
                ? "Paste your LinkedIn profile text here (headline, about, experience, skills…)"
                : "Paste your full resume text here…"
            }
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            count={resumeText.length}
            className="min-h-48"
          />
        </Card>

        {/* Right — Job Description (hidden for LinkedIn) */}
        <div className="space-y-4">
          {!isLinkedIn && (
            <Card className="p-5">
              <TextArea
                label="Job Description"
                placeholder="Paste the job description you're targeting…"
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
                count={jobDesc.length}
                className="min-h-36"
              />
            </Card>
          )}
          <Card className="p-5">
            <Input
              label={isLinkedIn ? "Target Role (optional)" : "Target Role (optional)"}
              placeholder={isLinkedIn ? "e.g. Senior Product Manager" : "e.g. Senior Product Manager"}
              value={role}
              onChange={(e) => setRole(e.target.value)}
            />
          </Card>

          {/* Actions */}
          <div className="flex flex-wrap items-center gap-2">
            <Button
              size="lg"
              loading={loading}
              onClick={handleAnalyze}
              className="flex-1 sm:flex-none"
            >
              {loading ? "Analyzing with AI…" : isLinkedIn ? "Analyze Profile" : "Analyze"}
              {!loading && <Sparkles className="size-4" />}
            </Button>
            <Button variant="outline" size="md" onClick={loadSample}>
              Load sample data
            </Button>
          </div>

          {/* Not signed in prompt */}
          {!user && !loading && !result && (
            <p className="text-xs text-foreground/40">
              <span className="font-medium">Free to try.</span>{" "}
              <button
                onClick={() => navigate("/auth?mode=signup")}
                className="cursor-pointer underline transition-colors hover:text-primary focus-ring rounded"
              >
                Sign up
              </button>{" "}
              to save your analysis history.
            </p>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mt-6 flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/5 px-5 py-4 text-sm text-destructive">
          <AlertCircle className="mt-0.5 size-5 shrink-0" />
          <div>
            <p className="font-semibold">Analysis failed</p>
            <p className="mt-0.5 text-destructive/80">{error}</p>
          </div>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="mt-10 space-y-8 animate-fadeSlideUp">
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start sm:gap-8">
            <div className="size-40 shrink-0 animate-shimmer rounded-full" />
            <div className="flex-1 space-y-4">
              <div className="h-4 w-full animate-shimmer rounded-lg" />
              <div className="h-4 w-3/4 animate-shimmer rounded-lg" />
              <div className="space-y-2">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="h-3 w-24 animate-shimmer rounded-lg" />
                    <div className="h-2 flex-1 animate-shimmer rounded-full" />
                    <div className="h-3 w-8 animate-shimmer rounded-lg" />
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="grid gap-6 sm:grid-cols-2">
            <div className="h-32 animate-shimmer rounded-2xl" />
            <div className="h-32 animate-shimmer rounded-2xl" />
          </div>
          <div className="h-28 animate-shimmer rounded-2xl" />
          <div className="h-40 animate-shimmer rounded-2xl" />
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="mt-10">
          <ResultsPanel mode={mode} result={result} />
        </div>
      )}
    </div>
  );
}