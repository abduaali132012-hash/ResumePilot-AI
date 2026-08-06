import { useCallback, useState } from "react";
import { Check, ChevronDown, Copy, FileText, Import, Lightbulb, ListChecks, MessageSquare, Sparkles, Target, TrendingUp, Wand2, Clock, BookOpen, Printer } from "lucide-react";
import { FaLinkedin } from "react-icons/fa6";
import { Badge, Card, EmptyState } from "./ui";
import type {
  ATSResult,
  CoverLetterResult,
  InterviewResult,
  RewriteResult,
  CareerGapsResult,
  SalaryInsightsResult,
  LinkedInResult,
  AnalysisMode,
  AnalysisResult,
} from "../lib/types";
import ScoreGauge, { CategoryBar } from "./ScoreGauge";

function ExportBtn() {
  return (
    <button
      onClick={() => window.print()}
      className="inline-flex cursor-pointer items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs font-semibold text-foreground/60 transition-all duration-150 hover:border-primary/30 hover:text-primary focus-ring"
      aria-label="Export as PDF"
    >
      <Printer className="size-3.5" />
      Export PDF
    </button>
  );
}

/* ───── Copy button ───── */

function CopyBtn({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* fallback */ }
  }, [text]);
  return (
    <button
      onClick={handleCopy}
      className="inline-flex cursor-pointer items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs font-semibold text-foreground/60 transition-all duration-150 hover:border-primary/30 hover:text-primary focus-ring"
      aria-label="Copy to clipboard"
    >
      {copied ? <Check className="size-3.5 text-accent" /> : <Copy className="size-3.5" />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

/* ───── Priority badge ───── */

function PriorityBadge({ p }: { p: string }) {
  const tone = p === "high" ? "danger" : p === "medium" ? "warning" : "neutral";
  return <Badge tone={tone}>{p}</Badge>;
}

/* ───── ATS result ───── */

function ATSView({ data }: { data: ATSResult }) {
  const { overallScore, categoryScores, matchedKeywords, missingKeywords, summary, strengths, improvements, suggestedSummary, atsTips } = data;

  return (
    <div className="space-y-8 animate-fadeSlideUp">
      {/* Score row */}
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start sm:gap-8">
        <ScoreGauge score={overallScore} />
        <div className="flex-1 space-y-3">
          <p className="text-sm leading-relaxed text-foreground/70">{summary}</p>
          <div className="space-y-1.5">
            {categoryScores && (
              <>
                <CategoryBar name="Keywords" value={categoryScores.keywords} />
                <CategoryBar name="Experience" value={categoryScores.experience} />
                <CategoryBar name="Format" value={categoryScores.format} />
                <CategoryBar name="Impact" value={categoryScores.impact} />
              </>
            )}
          </div>
        </div>
      </div>

      {/* Keywords */}
      <div className="grid gap-6 sm:grid-cols-2">
        <Card className="p-5">
          <div className="mb-3 flex items-center gap-2 text-sm font-bold text-foreground">
            <Check className="size-4 text-accent" />
            Matched keywords ({matchedKeywords?.length ?? 0})
          </div>
          <div className="flex flex-wrap gap-1.5">
            {matchedKeywords?.length ? matchedKeywords.map((k) => (
              <Badge key={k.term} tone="success">
                {k.term} <span className="text-[10px] opacity-60">×{k.count}</span>
              </Badge>
            )) : <span className="text-xs text-foreground/40">None found</span>}
          </div>
        </Card>
        <Card className="p-5">
          <div className="mb-3 flex items-center gap-2 text-sm font-bold text-foreground">
            <Target className="size-4 text-destructive" />
            Missing keywords ({missingKeywords?.length ?? 0})
          </div>
          <div className="flex flex-wrap gap-1.5">
            {missingKeywords?.length ? missingKeywords.map((k) => (
              <Badge key={k.term} tone={k.importance === "high" ? "danger" : k.importance === "medium" ? "warning" : "neutral"}>
                {k.term}
              </Badge>
            )) : <span className="text-xs text-foreground/40">All key terms covered — great!</span>}
          </div>
        </Card>
      </div>

      {/* Strengths */}
      <Card className="p-5">
        <h3 className="mb-3 flex items-center gap-2 text-sm font-bold text-foreground">
          <Lightbulb className="size-4 text-accent" />
          Strengths
        </h3>
        <ul className="space-y-1.5">
          {strengths?.map((s, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-foreground/70">
              <span className="mt-1 size-1.5 shrink-0 rounded-full bg-accent" />
              {s}
            </li>
          ))}
        </ul>
      </Card>

      {/* Improvements */}
      <Card className="p-5">
        <h3 className="mb-4 flex items-center gap-2 text-sm font-bold text-foreground">
          <ListChecks className="size-4 text-primary" />
          Improvements needed
        </h3>
        <div className="space-y-4">
          {improvements?.map((imp, i) => (
            <div key={i} className="rounded-xl border border-border bg-muted/40 p-4">
              <div className="mb-1.5 flex flex-wrap items-center gap-2">
                <span className="text-sm font-bold text-foreground">{imp.title}</span>
                <PriorityBadge p={imp.priority} />
              </div>
              <p className="text-sm leading-relaxed text-foreground/70">{imp.detail}</p>
              {imp.suggestion && (
                <p className="mt-2 flex items-start gap-1.5 text-sm italic text-primary/80">
                  <Sparkles className="mt-0.5 size-3.5 shrink-0" />
                  {imp.suggestion}
                </p>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Suggested summary */}
      {suggestedSummary && (
        <Card className="p-5">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-sm font-bold text-foreground">
              <Wand2 className="size-4 text-primary" />
              Rewritten Professional Summary
            </h3>
            <CopyBtn text={suggestedSummary} />
          </div>
          <p className="text-sm leading-relaxed text-foreground/70">{suggestedSummary}</p>
        </Card>
      )}

      {/* ATS tips */}
      <Card className="p-5">
        <h3 className="mb-3 flex items-center gap-2 text-sm font-bold text-foreground">
          <FileText className="size-4 text-primary" />
          ATS Tips
        </h3>
        <ul className="space-y-2">
          {atsTips?.map((tip, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-foreground/70">
              <span className="mt-1 size-1.5 shrink-0 rounded-full bg-primary" />
              {tip}
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

/* ───── Cover letter ───── */

function CoverLetterView({ data }: { data: CoverLetterResult }) {
  return (
    <div className="animate-fadeSlideUp">
      <Card className="p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-sm font-bold text-foreground">
            <MessageSquare className="size-4 text-accent" />
            Your Tailored Cover Letter
          </h3>
          <CopyBtn text={data.letter} />
        </div>
        <div className="whitespace-pre-line rounded-xl bg-muted/50 p-5 text-sm leading-relaxed text-foreground/80">
          {data.letter}
        </div>
      </Card>
    </div>
  );
}

/* ───── Interview prep ───── */

function InterviewView({ data }: { data: InterviewResult }) {
  const [openIdx, setOpenIdx] = useState<number | null>(0);
  return (
    <div className="space-y-3 animate-fadeSlideUp">
      <p className="text-sm text-foreground/60">
        Prepare with {data.questions?.length ?? 0} targeted questions based on the job description.
      </p>
      {data.questions?.map((q, i) => (
        <Card key={i} className="overflow-hidden">
          <button
            onClick={() => setOpenIdx(openIdx === i ? null : i)}
            className="flex w-full cursor-pointer items-center justify-between p-4 text-left transition-colors hover:bg-muted/30 focus-ring"
            aria-expanded={openIdx === i}
          >
            <span className="text-sm font-bold text-foreground">
              <span className="mr-2 text-primary/60">Q{i + 1}.</span> {q.question}
            </span>
            <ChevronDown className={`size-4 shrink-0 text-foreground/40 transition-transform duration-200 ${openIdx === i ? "rotate-180" : ""}`} />
          </button>
          {openIdx === i && (
            <div className="border-t border-border px-4 pb-4 pt-3">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-foreground/50">
                Why this matters
              </p>
              <p className="mb-4 text-sm leading-relaxed text-foreground/70">{q.why}</p>
              <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-accent/70">
                Sample answer (STAR)
              </p>
              <p className="text-sm leading-relaxed text-foreground/70">{q.sampleAnswer}</p>
            </div>
          )}
        </Card>
      ))}
    </div>
  );
}

/* ───── Rewrite ───── */

function RewriteView({ data }: { data: RewriteResult }) {
  return (
    <div className="space-y-5 animate-fadeSlideUp">
      <p className="text-sm text-foreground/60">
        {data.sections?.length ?? 0} section{data.sections?.length !== 1 ? "s" : ""} rewritten with keyword optimisation.
      </p>
      {data.sections?.map((sec, i) => (
        <Card key={i} className="overflow-hidden">
          <div className="border-b border-border bg-muted/30 px-4 py-3">
            <span className="text-sm font-bold text-foreground">{sec.heading}</span>
          </div>
          <div className="grid gap-4 p-4 sm:grid-cols-2">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-destructive/60">
                Original
              </p>
              <p className="text-sm leading-relaxed text-foreground/70">{sec.original}</p>
            </div>
            <div>
              <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-accent/70">
                <Wand2 className="size-3" />
                Rewritten
              </p>
              <p className="text-sm leading-relaxed text-foreground">{sec.rewritten}</p>
            </div>
          </div>
          {sec.note && (
            <div className="flex items-start gap-1.5 border-t border-border bg-primary/[0.02] px-4 py-2.5">
              <Lightbulb className="mt-0.5 size-3.5 shrink-0 text-primary/70" />
              <p className="text-xs italic text-primary/70">{sec.note}</p>
            </div>
          )}
        </Card>
      ))}
    </div>
  );
}

/* ───── Career Gap Analysis ───── */

function CareerGapsView({ data }: { data: CareerGapsResult }) {
  const highCount = data.gaps.filter((g) => g.importance === "high").length;
  const medCount = data.gaps.filter((g) => g.importance === "medium").length;

  return (
    <div className="space-y-6 animate-fadeSlideUp">
      {/* Summary card */}
      <Card className="flex items-center gap-4 p-5 sm:gap-6">
        <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-amber-100 text-amber-600">
          <Target className="size-7" />
        </div>
        <div>
          <p className="text-base font-bold text-foreground">
            {data.gaps.length} skill gap{data.gaps.length !== 1 ? "s" : ""} identified
          </p>
          <p className="text-sm text-foreground/60">
            {highCount} high-priority, {medCount} medium-priority —{" "}
            {data.gaps.length > 0 ? "here's how to close them." : "your profile looks strong!"}
          </p>
        </div>
      </Card>

      {/* Gap cards */}
      <div className="space-y-4">
        {data.gaps.map((gap, i) => (
          <Card key={i} className="overflow-hidden">
            <div className="flex items-start gap-4 p-5">
              <div className="min-w-0 flex-1">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <span className="text-base font-bold text-foreground">{gap.skill}</span>
                  <Badge tone={gap.importance === "high" ? "danger" : gap.importance === "medium" ? "warning" : "neutral"}>
                    {gap.importance} priority
                  </Badge>
                  <Badge tone={gap.currentLevel === "none" ? "danger" : gap.currentLevel === "basic" ? "warning" : "success"}>
                    {gap.currentLevel === "none" ? "Not present" : gap.currentLevel === "basic" ? "Basic" : "Intermediate"}
                  </Badge>
                </div>
                <p className="mb-3 text-sm leading-relaxed text-foreground/70">{gap.recommendation}</p>
                <div className="flex flex-wrap items-center gap-3 text-xs text-foreground/50">
                  <span className="inline-flex items-center gap-1">
                    <Import className="size-3" />
                    {gap.platform}
                  </span>
                  <span className="inline-flex items-center gap-1">
                    <BookOpen className="size-3" />
                    {gap.resource}
                  </span>
                  <span className="inline-flex items-center gap-1">
                    <Clock className="size-3" />
                    {gap.estimatedTime}
                  </span>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

/* ───── Salary Insights ───── */

function SalaryInsightsView({ data }: { data: SalaryInsightsResult }) {
  const { role, location, experienceLevel, salaryRange, marketPercentile, factors, negotiationTips } = data;

  const fmt = (n: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);

  return (
    <div className="space-y-6 animate-fadeSlideUp">
      {/* Header */}
      <Card className="p-5">
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start sm:gap-6">
          <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-600">
            <TrendingUp className="size-7" />
          </div>
          <div className="text-center sm:text-left">
            <h2 className="font-heading text-2xl font-extrabold text-foreground">{role}</h2>
            <p className="text-sm text-foreground/60">
              {location} · {experienceLevel}
            </p>
          </div>
        </div>
      </Card>

      {/* Salary range */}
      <Card className="p-5">
        <h3 className="mb-4 text-sm font-bold text-foreground">Estimated Salary Range</h3>
        <div className="mb-4 flex items-center justify-center gap-4">
          <div className="text-center">
            <p className="text-xs font-semibold text-foreground/50">Min</p>
            <p className="font-heading text-xl font-extrabold text-foreground">{fmt(salaryRange.min)}</p>
          </div>
          <div className="text-center">
            <p className="text-xs font-semibold text-foreground/50">Median</p>
            <p className="font-heading text-3xl font-extrabold text-primary">{fmt(salaryRange.mid)}</p>
          </div>
          <div className="text-center">
            <p className="text-xs font-semibold text-foreground/50">Max</p>
            <p className="font-heading text-xl font-extrabold text-foreground">{fmt(salaryRange.max)}</p>
          </div>
        </div>
        {/* Market percentile bar */}
        <div className="mx-auto max-w-md">
          <div className="mb-1 flex items-center justify-between text-xs text-foreground/50">
            <span>Market percentile</span>
            <span className="font-semibold">{marketPercentile}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-gradient-to-r from-accent to-primary transition-all duration-700"
              style={{ width: `${Math.min(marketPercentile, 100)}%` }}
            />
          </div>
          <p className="mt-2 text-xs text-foreground/40">{data.source}</p>
        </div>
      </Card>

      {/* Factors */}
      <Card className="p-5">
        <h3 className="mb-3 flex items-center gap-2 text-sm font-bold text-foreground">
          <Lightbulb className="size-4 text-primary" />
          What influences this range
        </h3>
        <ul className="space-y-2">
          {factors.map((f, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-foreground/70">
              <span className="mt-1 size-1.5 shrink-0 rounded-full bg-primary" />
              {f}
            </li>
          ))}
        </ul>
      </Card>

      {/* Negotiation tips */}
      <Card className="p-5">
        <h3 className="mb-3 flex items-center gap-2 text-sm font-bold text-foreground">
          <MessageSquare className="size-4 text-accent" />
          Negotiation Tips
        </h3>
        <ul className="space-y-2">
          {negotiationTips.map((tip, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-foreground/70">
              <span className="mt-1 size-1.5 shrink-0 rounded-full bg-accent" />
              {tip}
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

/* ───── LinkedIn Profile Analysis ───── */

function LinkedInView({ data }: { data: LinkedInResult }) {
  const { headlineScore, aboutScore, experienceScore, overallScore, summary, strengths, improvements, profileTips } = data;

  return (
    <div className="space-y-8 animate-fadeSlideUp">
      {/* Score row */}
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start sm:gap-8">
        <ScoreGauge score={overallScore} label="Profile Score" />
        <div className="flex-1 space-y-3">
          <p className="text-sm leading-relaxed text-foreground/70">{summary}</p>
          <div className="space-y-1.5">
            <CategoryBar name="Headline" value={headlineScore} />
            <CategoryBar name="About Section" value={aboutScore} />
            <CategoryBar name="Experience" value={experienceScore} />
          </div>
        </div>
      </div>

      {/* Strengths */}
      <Card className="p-5">
        <h3 className="mb-3 flex items-center gap-2 text-sm font-bold text-foreground">
          <Lightbulb className="size-4 text-accent" />
          Profile Strengths
        </h3>
        <ul className="space-y-1.5">
          {strengths?.map((s, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-foreground/70">
              <span className="mt-1 size-1.5 shrink-0 rounded-full bg-accent" />
              {s}
            </li>
          ))}
        </ul>
      </Card>

      {/* Improvements */}
      <Card className="p-5">
        <h3 className="mb-4 flex items-center gap-2 text-sm font-bold text-foreground">
          <ListChecks className="size-4 text-primary" />
          Optimisation Suggestions
        </h3>
        <div className="space-y-4">
          {improvements?.map((imp, i) => (
            <div key={i} className="overflow-hidden rounded-xl border border-border">
              <div className="border-b border-border bg-muted/30 px-4 py-2.5">
                <span className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-primary">
                  <FaLinkedin className="size-3" />
                  {imp.section}
                </span>
              </div>
              <div className="p-4">
                <p className="mb-1 text-xs font-semibold text-foreground/50">Current</p>
                <p className="mb-3 text-sm italic text-foreground/70">{imp.current}</p>
                <p className="mb-1 text-xs font-semibold text-accent/70">Suggested</p>
                <p className="mb-2 text-sm text-foreground">{imp.suggestion}</p>
                <p className="flex items-start gap-1.5 text-xs text-primary/70">
                  <Sparkles className="mt-0.5 size-3 shrink-0" />
                  {imp.tip}
                </p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Profile Tips */}
      <Card className="p-5">
        <h3 className="mb-3 flex items-center gap-2 text-sm font-bold text-foreground">
          <Target className="size-4 text-primary" />
          LinkedIn Optimisation Tips
        </h3>
        <ul className="space-y-2">
          {profileTips?.map((tip, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-foreground/70">
              <span className="mt-1 size-1.5 shrink-0 rounded-full bg-primary" />
              {tip}
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

/* ───── Main result panel ───── */

export default function ResultsPanel({
  mode,
  result,
}: {
  mode: AnalysisMode;
  result: AnalysisResult;
}) {
  if (!result) return null;

  return (
    <div>
      <div className="mb-4 flex items-center justify-between print:hidden">
        <span className="text-xs text-foreground/40" />
        <ExportBtn />
      </div>
      {renderResult(mode, result)}
    </div>
  );
}

function renderResult(mode: AnalysisMode, result: AnalysisResult) {
  if (!result) return null;

  switch (mode) {
    case "ats":
      return <ATSView data={result as ATSResult} />;
    case "cover-letter":
      return <CoverLetterView data={result as CoverLetterResult} />;
    case "interview":
      return <InterviewView data={result as InterviewResult} />;
    case "rewrite":
      return <RewriteView data={result as RewriteResult} />;
    case "career-gaps":
      return <CareerGapsView data={result as CareerGapsResult} />;
    case "salary-insights":
      return <SalaryInsightsView data={result as SalaryInsightsResult} />;
    case "linkedin":
      return <LinkedInView data={result as LinkedInResult} />;
    default:
      return <EmptyState icon={<Target className="size-6" />} title="Unknown mode" description="This analysis mode is not supported." />;
  }
}