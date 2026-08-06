import {
  forwardRef,
  type ButtonHTMLAttributes,
  type InputHTMLAttributes,
  type TextareaHTMLAttributes,
  type ReactNode,
} from "react";
import { Loader2 } from "lucide-react";

/* ───── Button ───── */

type Variant = "primary" | "secondary" | "ghost" | "outline" | "danger";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  fullWidth?: boolean;
}

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-primary text-on-primary hover:bg-primary/90 shadow-sm shadow-primary/30",
  secondary:
    "bg-secondary/10 text-primary hover:bg-secondary/20 border border-secondary/30",
  outline:
    "border border-border bg-transparent text-foreground hover:border-primary/50 hover:text-primary",
  ghost: "text-foreground/70 hover:bg-muted hover:text-foreground",
  danger: "bg-destructive/10 text-destructive hover:bg-destructive/20 border border-destructive/20",
};

const sizeClasses: Record<Size, string> = {
  sm: "h-8 px-3 text-sm gap-1.5",
  md: "h-10 px-4 text-sm gap-2",
  lg: "h-12 px-6 text-base gap-2",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { variant = "primary", size = "md", loading, fullWidth, className = "", children, disabled, ...props },
    ref
  ) => (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center rounded-lg font-semibold transition-all duration-150 ease-out active:scale-[0.97] disabled:opacity-50 disabled:pointer-events-none cursor-pointer focus-ring ${variantClasses[variant]} ${sizeClasses[size]} ${fullWidth ? "w-full" : ""} ${className}`}
      {...props}
    >
      {loading && <Loader2 className="size-4 animate-spin" aria-hidden />}
      {children}
    </button>
  )
);
Button.displayName = "Button";

/* ───── Card ───── */

export function Card({
  children,
  className = "",
  hover = false,
}: {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl border border-border bg-white shadow-sm transition-all duration-200 ${
        hover ? "hover:shadow-lg hover:-translate-y-0.5 hover:border-primary/30" : ""
      } ${className}`}
    >
      {children}
    </div>
  );
}

/* ───── Inputs ───── */

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, hint, error, className = "", id, ...props }, ref) => {
    const inputId = id || props.name;
    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="mb-1.5 block text-sm font-medium text-foreground/80">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`h-11 w-full rounded-lg border bg-white px-3.5 text-sm text-foreground placeholder:text-foreground/35 transition-all duration-150 focus-ring ${
            error ? "border-destructive" : "border-border hover:border-primary/40"
          } ${className}`}
          {...props}
        />
        {error && <p className="mt-1 text-xs text-destructive">{error}</p>}
        {hint && !error && <p className="mt-1 text-xs text-foreground/50">{hint}</p>}
      </div>
    );
  }
);
Input.displayName = "Input";

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: string;
  error?: string;
  count?: number;
}

export const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ label, hint, error, className = "", count, id, ...props }, ref) => {
    const inputId = id || props.name;
    return (
      <div className="w-full">
        {label && (
          <div className="mb-1.5 flex items-center justify-between">
            <label htmlFor={inputId} className="block text-sm font-medium text-foreground/80">
              {label}
            </label>
            {count !== undefined && (
              <span className="text-xs tabular-nums text-foreground/40">{count} chars</span>
            )}
          </div>
        )}
        <textarea
          ref={ref}
          id={inputId}
          className={`min-h-40 w-full resize-y rounded-lg border bg-white px-3.5 py-3 text-sm leading-relaxed text-foreground placeholder:text-foreground/35 transition-all duration-150 focus-ring scrollbar-thin ${
            error ? "border-destructive" : "border-border hover:border-primary/40"
          } ${className}`}
          {...props}
        />
        {error && <p className="mt-1 text-xs text-destructive">{error}</p>}
        {hint && !error && <p className="mt-1 text-xs text-foreground/50">{hint}</p>}
      </div>
    );
  }
);
TextArea.displayName = "TextArea";

/* ───── Badge ───── */

type BadgeTone = "primary" | "accent" | "neutral" | "warning" | "danger" | "success";

const toneClasses: Record<BadgeTone, string> = {
  primary: "bg-primary/10 text-primary",
  accent: "bg-accent/10 text-accent",
  neutral: "bg-muted text-foreground/70",
  warning: "bg-amber-100 text-amber-700",
  danger: "bg-destructive/10 text-destructive",
  success: "bg-emerald-100 text-emerald-700",
};

export function Badge({
  children,
  tone = "neutral",
  className = "",
}: {
  children: ReactNode;
  tone?: BadgeTone;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${toneClasses[tone]} ${className}`}
    >
      {children}
    </span>
  );
}

/* ───── Tabs ───── */

export interface TabItem {
  id: string;
  label: string;
  icon?: ReactNode;
}

export function Tabs({
  tabs,
  active,
  onChange,
}: {
  tabs: TabItem[];
  active: string;
  onChange: (id: string) => void;
}) {
  return (
    <div
      role="tablist"
      aria-label="Analysis tools"
      className="inline-flex max-w-full items-center gap-1 overflow-x-auto rounded-xl border border-border bg-muted/60 p-1 scrollbar-thin"
    >
      {tabs.map((tab) => {
        const selected = tab.id === active;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={selected}
            onClick={() => onChange(tab.id)}
            className={`inline-flex shrink-0 cursor-pointer items-center gap-1.5 rounded-lg px-3.5 py-2 text-sm font-semibold transition-all duration-150 focus-ring ${
              selected
                ? "bg-white text-primary shadow-sm"
                : "text-foreground/60 hover:text-foreground"
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}

/* ───── Spinner ───── */

export function Spinner({ className = "" }: { className?: string }) {
  return <Loader2 className={`size-5 animate-spin text-primary ${className}`} aria-label="Loading" />;
}

/* ───── Empty state ───── */

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-muted/40 px-6 py-16 text-center">
      <div className="mb-4 flex size-14 items-center justify-center rounded-2xl bg-white text-primary shadow-sm">
        {icon}
      </div>
      <h3 className="text-lg font-bold text-foreground">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-foreground/60">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}