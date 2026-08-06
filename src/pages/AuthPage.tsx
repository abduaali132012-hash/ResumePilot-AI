import { useState, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { AlertCircle, Check, Eye, EyeOff, Sparkles } from "lucide-react";
import { Button, Card, Input } from "../components/ui";
import { useAuth } from "../lib/store";

export default function AuthPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const modeParam = searchParams.get("mode") || "signin";
  const next = searchParams.get("next") || "/dashboard";

  const { signIn, signUp } = useAuth();

  const [mode, setMode] = useState<"signin" | "signup">(
    modeParam === "signup" ? "signup" : "signin"
  );
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const toggleMode = useCallback(() => {
    setMode((m) => (m === "signin" ? "signup" : "signin"));
    setError(null);
    setSuccess(null);
  }, []);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);
      setSuccess(null);

      if (!email.trim()) {
        setError("Please enter your email address.");
        return;
      }
      if (!password || password.length < 6) {
        setError("Password must be at least 6 characters.");
        return;
      }

      setLoading(true);
      try {
        if (mode === "signin") {
          const { error: err } = await signIn(email.trim(), password);
          if (err) {
            setError(err);
            return;
          }
          navigate(next, { replace: true });
        } else {
          const { error: err, userCreated } = await signUp(email.trim(), password);
          if (err) {
            setError(err);
            return;
          }
          if (userCreated) {
            setSuccess("Account created! Check your email for a confirmation link before signing in.");
          } else {
            setSuccess("Check your email for a confirmation link. Once confirmed, you can sign in.");
          }
        }
      } catch {
        setError("Something went wrong. Please try again.");
      } finally {
        setLoading(false);
      }
    },
    [mode, email, password, signIn, signUp, navigate, next]
  );

  return (
    <div className="mx-auto flex min-h-[calc(100vh-8rem)] max-w-md items-center justify-center px-4 py-12">
      <Card className="w-full p-6 sm:p-8">
        {/* Header */}
        <div className="mb-6 text-center">
          <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-secondary text-white shadow-md shadow-primary/25">
            <Sparkles className="size-6" />
          </div>
          <h1 className="font-heading text-2xl font-extrabold text-foreground">
            {mode === "signin" ? "Welcome back" : "Create your account"}
          </h1>
          <p className="mt-1 text-sm text-foreground/60">
            {mode === "signin"
              ? "Sign in to access your analysis history."
              : "Save your analyses and track your progress."}
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex rounded-xl border border-border bg-muted/60 p-1">
          {(["signin", "signup"] as const).map((m) => (
            <button
              key={m}
              onClick={() => { setMode(m); setError(null); setSuccess(null); }}
              className={`flex-1 cursor-pointer rounded-lg py-2 text-sm font-semibold transition-all duration-150 focus-ring ${
                mode === m
                  ? "bg-white text-foreground shadow-sm"
                  : "text-foreground/60 hover:text-foreground"
              }`}
            >
              {m === "signin" ? "Sign in" : "Create account"}
            </button>
          ))}
        </div>

        {/* Success message */}
        {success && (
          <div className="mb-4 flex items-start gap-2.5 rounded-xl border border-accent/30 bg-accent/5 px-4 py-3 text-sm">
            <Check className="mt-0.5 size-5 shrink-0 text-accent" />
            <span className="text-foreground/70">{success}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />

          <div className="relative">
            <Input
              label="Password"
              type={showPw ? "text" : "password"}
              placeholder="At least 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === "signin" ? "current-password" : "new-password"}
              hint={mode === "signup" ? "Min. 6 characters" : undefined}
              required
            />
            <button
              type="button"
              onClick={() => setShowPw((s) => !s)}
              className="absolute right-3 top-[38px] cursor-pointer text-foreground/40 transition-colors hover:text-foreground/70 focus-ring rounded"
              aria-label={showPw ? "Hide password" : "Show password"}
            >
              {showPw ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
            </button>
          </div>

          {error && (
            <div className="flex items-start gap-2.5 rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
              <AlertCircle className="mt-0.5 size-5 shrink-0" />
              <span className="text-destructive/80">{error}</span>
            </div>
          )}

          <Button type="submit" fullWidth size="lg" loading={loading}>
            {loading
              ? "Please wait…"
              : mode === "signin"
              ? "Sign in"
              : "Create account"}
          </Button>
        </form>

        {/* Footer */}
        <div className="mt-6 text-center text-xs text-foreground/50">
          {mode === "signin" ? (
            <>
              Don't have an account?{" "}
              <button onClick={toggleMode} className="cursor-pointer font-semibold text-primary underline transition-colors hover:text-primary/80 focus-ring rounded">
                Sign up
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button onClick={toggleMode} className="cursor-pointer font-semibold text-primary underline transition-colors hover:text-primary/80 focus-ring rounded">
                Sign in
              </button>
            </>
          )}
        </div>

        <div className="mt-4 text-center">
          <button
            onClick={() => navigate("/analyze")}
            className="cursor-pointer text-xs text-foreground/40 underline transition-colors hover:text-foreground/60 focus-ring rounded"
          >
            Skip — try the demo first
          </button>
        </div>
      </Card>
    </div>
  );
}