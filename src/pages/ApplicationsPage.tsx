import { useEffect, useState, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  Briefcase,
  Building2,
  ExternalLink,
  Plus,
  Pencil,
  Trash2,
  ArrowUpDown,
  Calendar,
  FileText,
  CheckCircle2,
  XCircle,
  Clock,
  Phone,
  Users,
  Code,
  Sparkles,
  AlertCircle,
} from "lucide-react";
import { Button, Card, Input, TextArea, EmptyState, Spinner } from "../components/ui";
import { supabase } from "../lib/supabase";
import { useAuth } from "../lib/store";
import type { JobApplication, ApplicationStatus } from "../lib/types";

/* ───── Status configuration ───── */

const STATUS_CONFIG: Record<ApplicationStatus, { label: string; tone: "primary" | "accent" | "warning" | "danger" | "success" | "neutral"; icon: React.ReactNode; dotColor: string }> = {
  saved: { label: "Saved", tone: "neutral", icon: <Clock className="size-3" />, dotColor: "bg-gray-400" },
  applied: { label: "Applied", tone: "primary", icon: <FileText className="size-3" />, dotColor: "bg-blue-500" },
  "phone-screen": { label: "Phone Screen", tone: "warning", icon: <Phone className="size-3" />, dotColor: "bg-amber-500" },
  interview: { label: "Interview", tone: "warning", icon: <Users className="size-3" />, dotColor: "bg-amber-500" },
  technical: { label: "Technical", tone: "warning", icon: <Code className="size-3" />, dotColor: "bg-amber-500" },
  offer: { label: "Offer", tone: "accent", icon: <Sparkles className="size-3" />, dotColor: "bg-emerald-500" },
  rejected: { label: "Rejected", tone: "danger", icon: <XCircle className="size-3" />, dotColor: "bg-red-500" },
  accepted: { label: "Accepted", tone: "success", icon: <CheckCircle2 className="size-3" />, dotColor: "bg-emerald-500" },
  ghosted: { label: "Ghosted", tone: "neutral", icon: <AlertCircle className="size-3" />, dotColor: "bg-gray-400" },
};

const STATUS_ORDER: ApplicationStatus[] = [
  "saved", "applied", "phone-screen", "interview", "technical", "offer", "accepted", "rejected", "ghosted",
];

const STATUS_BORDER: Record<string, string> = {
  saved: "border-l-gray-300",
  applied: "border-l-blue-500",
  "phone-screen": "border-l-amber-500",
  interview: "border-l-amber-500",
  technical: "border-l-amber-500",
  offer: "border-l-emerald-500",
  rejected: "border-l-red-500",
  accepted: "border-l-emerald-500",
  ghosted: "border-l-gray-300",
};

/* ───── Form modal ───── */

function ApplicationForm({
  initial,
  onSave,
  onCancel,
}: {
  initial?: Partial<JobApplication>;
  onSave: (app: { company: string; role: string; url: string; salary_range: string; status: ApplicationStatus; notes: string; applied_date: string }) => void;
  onCancel: () => void;
}) {
  const [company, setCompany] = useState(initial?.company ?? "");
  const [role, setRole] = useState(initial?.role ?? "");
  const [url, setUrl] = useState(initial?.url ?? "");
  const [salaryRange, setSalaryRange] = useState(initial?.salary_range ?? "");
  const [status, setStatus] = useState<ApplicationStatus>(initial?.status ?? "applied");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [appliedDate, setAppliedDate] = useState(initial?.applied_date ?? new Date().toISOString().split("T")[0]);
  const firstInputRef = useRef<HTMLInputElement>(null);

  // Focus trap and escape key
  useEffect(() => {
    firstInputRef.current?.focus();
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onCancel]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!company.trim() || !role.trim()) return;
    onSave({ company: company.trim(), role: role.trim(), url: url.trim(), salary_range: salaryRange.trim(), status, notes: notes.trim(), applied_date: appliedDate });
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm"
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
    >
      <div className="w-full max-w-lg" onClick={(e) => e.stopPropagation()}>
        <Card className="p-6">
          <h3 id="dialog-title" className="mb-5 text-lg font-bold text-foreground">{initial ? "Edit application" : "Add application"}</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Company *" placeholder="e.g. Google" value={company} onChange={(e) => setCompany(e.target.value)} required ref={firstInputRef} />
              <Input label="Role *" placeholder="e.g. Senior Engineer" value={role} onChange={(e) => setRole(e.target.value)} required />
            </div>
            <Input label="Job posting URL" placeholder="https://..." value={url} onChange={(e) => setUrl(e.target.value)} />
            <Input label="Salary range" placeholder="e.g. $120K-$150K" value={salaryRange} onChange={(e) => setSalaryRange(e.target.value)} />
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-foreground/80">Status</label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value as ApplicationStatus)}
                  className="h-11 w-full rounded-lg border border-border bg-white px-3.5 text-sm text-foreground transition-all duration-150 focus-ring hover:border-primary/40"
                >
                  {STATUS_ORDER.map((s) => (
                    <option key={s} value={s}>{STATUS_CONFIG[s].label}</option>
                  ))}
                </select>
              </div>
              <Input label="Applied date" type="date" value={appliedDate} onChange={(e) => setAppliedDate(e.target.value)} />
            </div>
            <TextArea label="Notes" placeholder="Recruiter contact, interview details, follow-up…" value={notes} onChange={(e) => setNotes(e.target.value)} className="min-h-24" />
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" type="button" onClick={onCancel}>Cancel</Button>
              <Button type="submit">{initial ? "Save changes" : "Add application"}</Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}

/* ───── Page ───── */

export default function ApplicationsPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<JobApplication | null>(null);
  const [sortBy, setSortBy] = useState<"date" | "status" | "company">("date");
  const [filterStatus, setFilterStatus] = useState<ApplicationStatus | "all">("all");

  useEffect(() => {
    if (!authLoading && !user) {
      navigate("/auth?next=/applications", { replace: true });
      return;
    }
    if (!user) return;

    const fetch = async () => {
      setLoading(true);
      const { data, error } = await supabase
        .from("job_applications")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false });
      if (!error && data) setApplications(data as unknown as JobApplication[]);
      setLoading(false);
    };
    fetch();
  }, [user, authLoading, navigate]);

  const handleSave = useCallback(async (app: { company: string; role: string; url: string; salary_range: string; status: ApplicationStatus; notes: string; applied_date: string }) => {
    if (!user) return;

    if (editing) {
      const { error } = await supabase
        .from("job_applications")
        .update({ ...app, updated_at: new Date().toISOString() })
        .eq("id", editing.id);
      if (!error) {
        setApplications((prev) => prev.map((a) => a.id === editing.id ? { ...a, ...app } as JobApplication : a));
      }
    } else {
      const { data, error } = await supabase
        .from("job_applications")
        .insert({ user_id: user.id, ...app })
        .select()
        .single();
      if (!error && data) {
        setApplications((prev) => [data as unknown as JobApplication, ...prev]);
      }
    }
    setShowForm(false);
    setEditing(null);
  }, [user, editing]);

  const handleDelete = useCallback(async (id: string) => {
    await supabase.from("job_applications").delete().eq("id", id);
    setApplications((prev) => prev.filter((a) => a.id !== id));
  }, []);

  const handleStatusChange = useCallback(async (id: string, newStatus: ApplicationStatus) => {
    await supabase.from("job_applications").update({ status: newStatus, updated_at: new Date().toISOString() }).eq("id", id);
    setApplications((prev) => prev.map((a) => a.id === id ? { ...a, status: newStatus } as JobApplication : a));
  }, []);

  // Stats
  const total = applications.length;
  const active = applications.filter((a) => !["rejected", "accepted", "ghosted"].includes(a.status)).length;
  const interviews = applications.filter((a) => ["phone-screen", "interview", "technical"].includes(a.status)).length;

  // Filter & sort
  let filtered = filterStatus === "all" ? applications : applications.filter((a) => a.status === filterStatus);
  filtered = [...filtered].sort((a, b) => {
    if (sortBy === "date") return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    if (sortBy === "company") return a.company.localeCompare(b.company);
    return STATUS_ORDER.indexOf(a.status) - STATUS_ORDER.indexOf(b.status);
  });

  if (authLoading || loading) {
    return <div className="flex min-h-[50vh] items-center justify-center"><Spinner className="size-8" /></div>;
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:py-12">
      {/* Header */}
      <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="font-heading text-3xl font-extrabold text-foreground sm:text-4xl">
            Application <span className="gradient-text">Tracker</span>
          </h1>
          <p className="mt-2 text-base text-foreground/60">
            Manage every job application from one dashboard.
          </p>
        </div>
        <Button onClick={() => { setEditing(null); setShowForm(true); }}>
          <Plus className="size-4" />
          Add application
        </Button>
      </div>

      {/* Stats */}
      <div className="mb-6 grid grid-cols-3 gap-4">
        {[
          { icon: <Briefcase className="size-5" />, label: "Total", value: total },
          { icon: <Clock className="size-5" />, label: "Active", value: active },
          { icon: <Calendar className="size-5" />, label: "Interviews", value: interviews },
        ].map((s) => (
          <Card key={s.label} className="flex flex-col items-center p-4 text-center">
            <div className="mb-2 flex size-9 items-center justify-center rounded-xl bg-primary/10 text-primary">{s.icon}</div>
            <span className="font-heading text-xl font-extrabold text-foreground">{s.value}</span>
            <span className="text-xs text-foreground/50">{s.label}</span>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as ApplicationStatus | "all")}
          className="h-9 rounded-lg border border-border bg-white px-2.5 text-xs font-medium text-foreground focus-ring"
          aria-label="Filter by status"
        >
          <option value="all">All statuses</option>
          {STATUS_ORDER.map((s) => (
            <option key={s} value={s}>{STATUS_CONFIG[s].label}</option>
          ))}
        </select>
        <button
          onClick={() => setSortBy((s) => s === "date" ? "status" : s === "status" ? "company" : "date")}
          className="inline-flex h-9 cursor-pointer items-center gap-1.5 rounded-lg border border-border bg-white px-2.5 text-xs font-medium text-foreground/70 transition-colors hover:border-primary/40 hover:text-primary focus-ring"
          aria-label="Change sort order"
        >
          <ArrowUpDown className="size-3" />
          Sort: {sortBy === "date" ? "Date" : sortBy === "status" ? "Status" : "Company"}
        </button>
      </div>

      {/* Empty state */}
      {filtered.length === 0 && (
        <EmptyState
          icon={<Building2 className="size-6" />}
          title={applications.length === 0 ? "No applications yet" : "No matches"}
          description={applications.length === 0 ? "Start tracking your job applications here. Add your first one to get started." : "Try changing the filter to see more results."}
          action={applications.length === 0 ? (
            <Button onClick={() => { setEditing(null); setShowForm(true); }}>
              <Plus className="size-4" />
              Add your first application
            </Button>
          ) : undefined}
        />
      )}

      {/* List */}
      <div className="space-y-3">
        {filtered.map((app) => {
          const cfg = STATUS_CONFIG[app.status];
          return (
            <Card key={app.id} className={`flex flex-wrap items-center gap-3 p-4 sm:flex-nowrap sm:gap-4 border-l-4 transition-all duration-200 hover:shadow-md ${STATUS_BORDER[app.status] || ""}`}>
              {/* Status dot */}
              <div className={`absolute right-3 top-3 size-2 rounded-full ${cfg.dotColor} sm:static sm:size-3`} aria-hidden />

              {/* Company icon */}
              <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <Building2 className="size-5" />
              </div>

              {/* Info */}
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-bold text-foreground">{app.role}</p>
                <p className="truncate text-xs text-foreground/50">{app.company}{app.salary_range ? ` · ${app.salary_range}` : ""}</p>
              </div>

              {/* Status dropdown */}
              <select
                value={app.status}
                onChange={(e) => handleStatusChange(app.id, e.target.value as ApplicationStatus)}
                className="h-8 rounded-lg border border-border bg-white px-2 text-xs font-semibold text-foreground focus-ring"
                aria-label={`Status for ${app.role} at ${app.company}`}
              >
                {STATUS_ORDER.map((s) => (
                  <option key={s} value={s}>{STATUS_CONFIG[s].label}</option>
                ))}
              </select>

              {/* Date */}
              <span className="hidden shrink-0 text-xs text-foreground/40 sm:block">
                {new Date(app.applied_date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
              </span>

              {/* Actions */}
              <div className="flex items-center gap-1">
                {app.url && (
                  <a
                    href={app.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex size-8 cursor-pointer items-center justify-center rounded-lg text-foreground/50 transition-colors hover:bg-muted hover:text-primary focus-ring"
                    aria-label="Open job posting"
                  >
                    <ExternalLink className="size-4" />
                  </a>
                )}
                <button
                  onClick={() => { setEditing(app); setShowForm(true); }}
                  className="flex size-8 cursor-pointer items-center justify-center rounded-lg text-foreground/50 transition-colors hover:bg-muted hover:text-primary focus-ring"
                  aria-label="Edit application"
                >
                  <Pencil className="size-4" />
                </button>
                <button
                  onClick={() => handleDelete(app.id)}
                  className="flex size-8 cursor-pointer items-center justify-center rounded-lg text-foreground/50 transition-colors hover:bg-destructive/10 hover:text-destructive focus-ring"
                  aria-label="Delete application"
                >
                  <Trash2 className="size-4" />
                </button>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Form modal */}
      {showForm && (
        <ApplicationForm
          initial={editing ?? undefined}
          onSave={handleSave}
          onCancel={() => { setShowForm(false); setEditing(null); }}
        />
      )}
    </div>
  );
}