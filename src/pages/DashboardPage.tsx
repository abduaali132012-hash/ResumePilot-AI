import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  BarChart3,
  Clock,
  FileText,
  ScanSearch,
  TrendingUp,
  ChevronRight,
} from "lucide-react";
import { Button, Card, EmptyState, Badge, Spinner } from "../components/ui";
import { supabase } from "../lib/supabase";
import { useAuth } from "../lib/store";
import type { SavedAnalysis, AnalysisMode } from "../lib/types";

const modeLabels: Record<AnalysisMode, string> = {
  ats: "ATS Score",
  "cover-letter": "Cover Letter",
  interview: "Interview Prep",
  rewrite: "Rewrite",
  "career-gaps": "Career Gaps",
  "salary-insights": "Salary Insights",
  linkedin: "LinkedIn Profile",
};

const modeTone: Record<AnalysisMode, "primary" | "accent" | "warning" | "success"> = {
  ats: "primary",
  "cover-letter": "accent",
  interview: "warning",
  rewrite: "success",
  "career-gaps": "warning",
  "salary-insights": "accent",
  linkedin: "primary",
};

const modeIcons: Record<string, React.ReactNode> = {
  ats: <ScanSearch className="size-4" />,
  "cover-letter": <FileText className="size-4" />,
  interview: <BarChart3 className="size-4" />,
  rewrite: <TrendingUp className="size-4" />,
  linkedin: <BarChart3 className="size-4" />,
};

function scoreColor(s: number | null) {
  if (s === null) return { bg: "bg-muted", text: "text-foreground/50", bar: "" };
  if (s >= 80) return { bg: "bg-emerald-100", text: "text-emerald-700", bar: "bg-accent" };
  if (s >= 60) return { bg: "bg-amber-100", text: "text-amber-700", bar: "bg-amber-500" };
  return { bg: "bg-red-100", text: "text-red-700", bar: "bg-destructive" };
}

/* ───── Score trend mini-chart ───── */
function ScoreTrendChart({ analyses }: { analyses: SavedAnalysis[] }) {
  const scored = analyses
    .filter((a) => a.score != null && a.mode === "ats")
    .slice(0, 20)
    .reverse();

  if (scored.length < 2) return null;

  const maxScore = Math.max(...scored.map((a) => a.score!));
  const minScore = Math.min(...scored.map((a) => a.score!));
  const range = Math.max(maxScore - minScore, 10);
  const chartHeight = 120;
  const barWidth = Math.max(20, Math.min(40, 400 / scored.length));
  const chartWidth = scored.length * (barWidth + 6) + 20;

  return (
    <Card className="p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="flex items-center gap-2 text-sm font-bold text-foreground">
          <TrendingUp className="size-4 text-primary" />
          Score Trend
        </h3>
        <span className="text-xs text-foreground/50">{scored.length} analyses</span>
      </div>
      <div className="overflow-x-auto scrollbar-thin" style={{ maxWidth: "100%" }}>
        <svg width={chartWidth} height={chartHeight} className="block" role="img" aria-label="ATS score trend chart">
          {/* Y-axis grid lines */}
          {[0, 25, 50, 75, 100].map((y) => {
            const yPos = chartHeight - (y / 100) * (chartHeight - 20) - 10;
            return (
              <g key={y}>
                <line x1={0} y1={yPos} x2={chartWidth} y2={yPos} stroke="var(--color-border)" strokeWidth={0.5} />
                <text x={chartWidth - 2} y={yPos + 3} textAnchor="end" fontSize={9} fill="var(--color-foreground/0.4)">
                  {y}
                </text>
              </g>
            );
          })}
          {/* Bars */}
          {scored.map((a, i) => {
            const x = 10 + i * (barWidth + 6);
            const barH = ((a.score! - minScore) / range) * (chartHeight - 30);
            const y = chartHeight - 10 - barH;
            const color = a.score! >= 80 ? "var(--color-accent)" : a.score! >= 60 ? "#eab308" : "var(--color-destructive)";
            return (
              <g key={a.id}>
                <rect x={x} y={y} width={barWidth} height={Math.max(barH, 2)} rx={3} fill={color} opacity={0.8}>
                  <title>{a.score}% — {new Date(a.created_at).toLocaleDateString()}</title>
                </rect>
              </g>
            );
          })}
        </svg>
      </div>
    </Card>
  );
}

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  const [analyses, setAnalyses] = useState<SavedAnalysis[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) {
      navigate("/auth?next=/dashboard", { replace: true });
      return;
    }
    if (!user) return;

    const fetchAnalyses = async () => {
      setLoading(true);
      const { data, error } = await supabase
        .from("resume_analyses")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false })
        .limit(50);

      if (!error && data) {
        setAnalyses(data as unknown as SavedAnalysis[]);
      }
      setLoading(false);
    };

    fetchAnalyses();
  }, [user, authLoading, navigate]);

  // Stats
  const total = analyses.length;
  const scored = analyses.filter((a) => a.score != null);
  const avgScore =
    scored.length > 0
      ? Math.round(scored.reduce((sum, a) => sum + (a.score ?? 0), 0) / scored.length)
      : null;
  const recent = analyses.filter(
    (a) => Date.now() - new Date(a.created_at).getTime() < 7 * 24 * 60 * 60 * 1000
  ).length;

  if (authLoading || loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Spinner className="size-8" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:py-12">
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-heading text-3xl font-extrabold text-foreground sm:text-4xl">
          Your <span className="gradient-text">Analysis History</span>
        </h1>
        <p className="mt-2 text-base text-foreground/60">
          Track every resume analysis and compare your scores over time.
        </p>
      </div>

      {/* Stats row */}
      <div className="mb-8 grid grid-cols-3 gap-4">
        {[
          {
            icon: <FileText className="size-5" />,
            label: "Total analyses",
            value: total,
            gradient: "from-primary/10 to-secondary/10",
            iconBg: "bg-primary/10",
            iconColor: "text-primary",
          },
          {
            icon: <TrendingUp className="size-5" />,
            label: "Avg. ATS score",
            value: avgScore ? `${avgScore}%` : "—",
            gradient: "from-accent/10 to-emerald-100",
            iconBg: "bg-accent/10",
            iconColor: "text-accent",
          },
          {
            icon: <Clock className="size-5" />,
            label: "This week",
            value: recent,
            gradient: "from-amber-50 to-amber-100/30",
            iconBg: "bg-amber-100",
            iconColor: "text-amber-600",
          },
        ].map((s) => (
          <Card key={s.label} className={`flex flex-col items-center p-4 text-center sm:p-5 bg-gradient-to-br ${s.gradient}`}>
            <div className={`mb-2 flex size-9 items-center justify-center rounded-xl ${s.iconBg} ${s.iconColor}`}>
              {s.icon}
            </div>
            <span className="font-heading text-xl font-extrabold text-foreground">{s.value}</span>
            <span className="text-xs text-foreground/50">{s.label}</span>
          </Card>
        ))}
      </div>

      {/* Score trend chart */}
      {analyses.length > 0 && <ScoreTrendChart analyses={analyses} />}

      {/* List */}
      {analyses.length === 0 ? (
        <div className="mt-6">
          <EmptyState
            icon={<ScanSearch className="size-6" />}
            title="No analyses yet"
            description="Run your first ATS analysis to see your history here. It only takes 30 seconds."
            action={
              <Button onClick={() => navigate("/analyze")}>
                <BarChart3 className="size-4" />
                Analyze your resume
              </Button>
            }
          />
        </div>
      ) : (
        <div className="mt-6 space-y-3">
          {analyses.map((a) => {
            const sc = scoreColor(a.score ?? null);
            return (
              <Link
                key={a.id}
                to={`/analysis/${a.id}`}
                className="group block"
              >
                <Card className="flex items-center gap-4 p-4 sm:gap-6 transition-all duration-200 hover:shadow-md hover:border-primary/30">
                  {/* Mode icon */}
                  <div className="hidden shrink-0 sm:flex size-10 items-center justify-center rounded-xl bg-primary/5 text-primary/60 group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                    {modeIcons[a.mode] || <ScanSearch className="size-4" />}
                  </div>

                  {/* Mode badge */}
                  <Badge tone={modeTone[a.mode as AnalysisMode] || "neutral"}>
                    {modeLabels[a.mode as AnalysisMode] || a.mode}
                  </Badge>

                  {/* Role & date */}
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-foreground">
                      {a.role || "Untitled Analysis"}
                    </p>
                    <p className="text-xs text-foreground/50">
                      {new Date(a.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>

                  {/* Score mini-bar */}
                  {a.score != null && (
                    <div className="hidden sm:flex items-center gap-2">
                      <div className="h-6 w-16 overflow-hidden rounded-full bg-muted">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${sc.bar}`}
                          style={{ width: `${a.score}%` }}
                        />
                      </div>
                      <span className={`text-xs font-bold tabular-nums ${sc.text}`}>
                        {a.score}
                      </span>
                    </div>
                  )}

                  {a.score == null && (
                    <span className="hidden text-xs text-foreground/40 sm:block">—</span>
                  )}

                  {/* Chevron */}
                  <ChevronRight className="size-4 shrink-0 text-foreground/20 transition-all duration-200 group-hover:text-primary group-hover:translate-x-0.5" />
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}