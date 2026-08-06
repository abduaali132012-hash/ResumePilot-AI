import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button, Spinner } from "../components/ui";
import ResultsPanel from "../components/ResultsPanel";
import { supabase } from "../lib/supabase";
import { useAuth } from "../lib/store";
import type { SavedAnalysis, AnalysisMode } from "../lib/types";

export default function HistoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  const [analysis, setAnalysis] = useState<SavedAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      navigate("/auth", { replace: true });
      return;
    }
    if (!user || !id) return;

    const fetch = async () => {
      setLoading(true);
      const { data, error } = await supabase
        .from("resume_analyses")
        .select("*")
        .eq("id", id)
        .eq("user_id", user.id)
        .single();

      if (error || !data) {
        setError("Analysis not found or access denied.");
      } else {
        setAnalysis(data as unknown as SavedAnalysis);
      }
      setLoading(false);
    };

    fetch();
  }, [id, user, authLoading, navigate]);

  if (authLoading || loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Spinner className="size-8" />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="mx-auto flex min-h-[50vh] max-w-lg flex-col items-center justify-center px-4 text-center">
        <p className="text-lg font-bold text-foreground">Analysis not found</p>
        <p className="mt-2 text-sm text-foreground/60">{error || "It may have been deleted."}</p>
        <Button className="mt-6" variant="outline" onClick={() => navigate("/dashboard")}>
          <ArrowLeft className="size-4" />
          Back to dashboard
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:py-12">
      <button
        onClick={() => navigate("/dashboard")}
        className="mb-6 inline-flex cursor-pointer items-center gap-1.5 text-sm text-foreground/50 transition-colors hover:text-primary focus-ring rounded"
      >
        <ArrowLeft className="size-4" />
        Back to dashboard
      </button>

      <div className="mb-8">
        <h1 className="font-heading text-2xl font-extrabold text-foreground">
          {analysis.role || "Untitled Analysis"}
        </h1>
        <p className="mt-1 text-sm text-foreground/50">
          {new Date(analysis.created_at).toLocaleDateString("en-US", {
            weekday: "long",
            month: "long",
            day: "numeric",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>

      <ResultsPanel mode={analysis.mode as AnalysisMode} result={analysis.result} />
    </div>
  );
}