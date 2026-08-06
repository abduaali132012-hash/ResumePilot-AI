import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import confetti from "canvas-confetti";
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  Briefcase,
  Check,
  ChevronDown,
  Copy,
  DollarSign,
  Download,
  FileText,
  MessageSquare,
  Quote,
  ScanSearch,
  Sparkles,
  Star,
  Target,
  TrendingUp,
  Trophy,
  Users,
  Wand2,
} from "lucide-react";
import { motion, useReducedMotion } from "framer-motion";
import { Button, Card, Badge } from "../components/ui";
import ScoreGauge from "../components/ScoreGauge";

/* ───── Animated counter ───── */
function AnimatedCounter({ value, suffix = "" }: { value: string; suffix?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const [display, setDisplay] = useState("0");
  const [hasAnimated, setHasAnimated] = useState(false);
  const prefersReduced = useReducedMotion();

  const numeric = parseInt(value.replace(/\D/g, ""), 10);
  const isNumeric = !isNaN(numeric);

  useEffect(() => {
    if (prefersReduced || !isNumeric || hasAnimated) {
      setDisplay(value);
      return;
    }

    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated) {
          setHasAnimated(true);
          const start = performance.now();
          const duration = 1500;
          const tick = (now: number) => {
            const t = Math.min(1, (now - start) / duration);
            const eased = 1 - Math.pow(1 - t, 3);
            const current = Math.round(eased * numeric);
            setDisplay(current + suffix);
            if (t < 1) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        }
      },
      { threshold: 0.3 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [value, suffix, numeric, isNumeric, hasAnimated, prefersReduced]);

  return (
    <span ref={ref} className="font-heading text-2xl font-extrabold text-foreground">
      {display}
    </span>
  );
}

/* ───── Static stats carousel ───── */
const stats = [
  { icon: <BarChart3 className="size-5" />, value: "24K+", label: "Resumes analysed" },
  { icon: <Users className="size-5" />, value: "12K+", label: "Active users" },
  { icon: <TrendingUp className="size-5" />, value: "92%", label: "Avg. score improvement" },
  { icon: <Star className="size-5" />, value: "4.9", label: "User rating" },
];

/* ───── Features grid ───── */
const features = [
  {
    icon: <ScanSearch className="size-6" />,
    title: "ATS Match Score",
    desc: "Get a precise 0-100 match score showing how your resume performs against any job description.",
  },
  {
    icon: <Target className="size-6" />,
    title: "Keyword Gap Analysis",
    desc: "See exactly which keywords from the job description are missing — and how to add them naturally.",
  },
  {
    icon: <Wand2 className="size-6" />,
    title: "AI Resume Rewrite",
    desc: "Rewrite every section of your resume with quantified achievements and keyword alignment.",
  },
  {
    icon: <FileText className="size-6" />,
    title: "Cover Letter Generator",
    desc: "Generate a tailored, impactful cover letter in seconds that matches the job description.",
  },
  {
    icon: <MessageSquare className="size-6" />,
    title: "Interview Prep",
    desc: "Get 8 targeted interview questions with sample STAR answers based on your resume and the job.",
  },
  {
    icon: <Users className="size-6" />,
    title: "LinkedIn Profile Analyzer",
    desc: "Analyse and optimise your LinkedIn profile — headline, about section, experience, and more.",
  },
  {
    icon: <Copy className="size-6" />,
    title: "Analysis History",
    desc: "Save every analysis, track your progress, and compare scores across different job applications.",
  },
  {
    icon: <BookOpen className="size-6" />,
    title: "Career Gap Analyzer",
    desc: "Identify missing skills for your target role and get personalised course recommendations to close the gap.",
  },
  {
    icon: <DollarSign className="size-6" />,
    title: "Salary Insights",
    desc: "Estimate salary ranges for matching roles with market data, percentile benchmarks, and negotiation tips.",
  },
  {
    icon: <Briefcase className="size-6" />,
    title: "Application Tracker",
    desc: "Manage every job application from one dashboard — track status, notes, and follow-ups in real time.",
  },
];

/* ───── Steps ───── */
const steps = [
  { icon: <FileText className="size-7" />, title: "1. Paste your resume & job description", desc: "Copy-paste your resume text and the job description you're targeting. No signup required." },
  { icon: <Sparkles className="size-7" />, title: "2. AI analyses against ATS algorithms", desc: "Our Gemini-powered engine evaluates keyword alignment, format, experience fit, and impact." },
  { icon: <TrendingUp className="size-7" />, title: "3. Get your score, keywords, and rewrite", desc: "Receive a detailed breakdown with actionable improvements and a rewritten professional summary." },
];

/* ───── Pricing tiers ───── */
const tiers = [
  {
    name: "Free",
    price: "$0",
    desc: "Perfect for trying the tool.",
    features: ["5 analyses per month", "ATS scoring only", "Basic keyword tips", "No account needed"],
    cta: "Try free",
    href: "/analyze",
    popular: false,
  },
  {
    name: "Pro",
    price: "$9",
    desc: "For active job seekers.",
    features: [
      "Unlimited analyses",
      "All 7 modes (ATS, cover letter, interview, rewrite, LinkedIn, gaps, salary)",
      "Full results & keyword breakdown",
      "Saved analysis history",
      "Email support",
    ],
    cta: "Start free trial",
    href: "/auth?mode=signup",
    popular: true,
  },
  {
    name: "Career",
    price: "$19",
    desc: "For serious career moves.",
    features: [
      "Everything in Pro",
      "Priority support",
      "Multi-resume versions & comparison",
      "LinkedIn optimisation deep-dive",
      "API access (coming soon)",
    ],
    cta: "Start free trial",
    href: "/auth?mode=signup",
    popular: false,
  },
];

/* ───── Benchmark comparison ───── */
const benchmarks = [
  { feature: "ATS Match Scoring (0-100)", pilot: true, other1: true, other2: false, other3: false },
  { feature: "Keyword Gap Analysis", pilot: true, other1: true, other2: true, other3: false },
  { feature: "AI Resume Rewrite", pilot: true, other1: false, other2: false, other3: false },
  { feature: "Cover Letter Generator", pilot: true, other1: false, other2: false, other3: false },
  { feature: "Interview Prep with STAR Answers", pilot: true, other1: false, other2: false, other3: false },
  { feature: "LinkedIn Profile Analyzer", pilot: true, other1: false, other2: false, other3: false },
  { feature: "Career Gap Analyzer", pilot: true, other1: false, other2: false, other3: false },
  { feature: "Salary Insights & Benchmarks", pilot: true, other1: false, other2: false, other3: false },
  { feature: "Application Tracker", pilot: true, other1: false, other2: false, other3: false },
  { feature: "Free Tier (no credit card)", pilot: true, other1: true, other2: false, other3: true },
  { feature: "Gemini AI Powered", pilot: true, other1: false, other2: false, other3: false },
];

const benchLabels = ["ResumePilot AI", "Jobscan", "TopResume", "Rezi"];

/* ───── FAQ ───── */
const faqs = [
  { q: "How accurate is the ATS match score?", a: "The score is based on the same principles real ATS systems use: keyword matching, section parsing, experience alignment, and impact quantification. While no automated tool can perfectly replicate every ATS, our analysis gives you a strong indicator of where you stand." },
  { q: "Do I need to create an account?", a: "No! You can run a full ATS analysis without signing up. Accounts are only needed to save your history and access unlimited analyses." },
  { q: "What AI model powers the analysis?", a: "ResumePilot uses Google Gemini 2.0 Flash — a fast, capable model with strong resume analysis expertise. Your data is never used for training." },
  { q: "Can I download my cover letter?", a: "Yes — every cover letter and rewritten summary includes a copy button. You can paste it into Google Docs, Word, or any editor." },
];

/* ───── Testimonials ───── */
const testimonials = [
  {
    quote: "ResumePilot helped me identify exactly what keywords my resume was missing. After applying the suggestions, I got 3 interview callbacks in the first week.",
    author: "Sarah K.",
    role: "Senior Product Manager",
    rating: 5,
  },
  {
    quote: "The cover letter generator saved me hours. I tailored 12 applications in one afternoon and the quality was genuinely impressive.",
    author: "James M.",
    role: "Software Engineer",
    rating: 5,
  },
  {
    quote: "I was getting rejected before the first interview. The ATS score showed me my resume wasn't even being seen. A few tweaks later and I landed a role at a FAANG company.",
    author: "Priya R.",
    role: "Data Scientist",
    rating: 5,
  },
];

/* ───── Section wrapper with scroll animation ───── */
function Section({
  id,
  children,
  className = "",
}: {
  id?: string;
  children: React.ReactNode;
  className?: string;
}) {
  const prefersReduced = useReducedMotion();
  return (
    <motion.section
      id={id}
      initial={prefersReduced ? {} : { opacity: 0, y: 24 }}
      whileInView={prefersReduced ? {} : { opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className={className}
    >
      {children}
    </motion.section>
  );
}

/* ───── Staggered fade-in container ───── */
function StaggerContainer({
  children,
  className = "",
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const prefersReduced = useReducedMotion();
  return (
    <motion.div
      initial={prefersReduced ? {} : { opacity: 0, y: 16 }}
      whileInView={prefersReduced ? {} : { opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.4, delay, ease: "easeOut" }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ───── Landing page ───── */
export default function LandingPage() {
  const navigate = useNavigate();
  const prefersReduced = useReducedMotion();

  const fireConfetti = useCallback(() => {
    if (prefersReduced) return;
    const duration = 2000;
    const end = Date.now() + duration;
    const colors = ["#5854e6", "#7c3aed", "#10b981", "#34d399", "#f59e0b"];

    const frame = () => {
      confetti({
        particleCount: 3,
        angle: 60,
        spread: 55,
        origin: { x: 0, y: 0.7 },
        colors,
      });
      confetti({
        particleCount: 3,
        angle: 120,
        spread: 55,
        origin: { x: 1, y: 0.7 },
        colors,
      });
      if (Date.now() < end) requestAnimationFrame(frame);
    };
    frame();
  }, [prefersReduced]);

  return (
    <div className="blob-bg">
      {/* Animated floating glow blobs */}
      <div className="blob-glow blob-glow-1" aria-hidden />
      <div className="blob-glow blob-glow-2" aria-hidden />
      <div className="blob-glow blob-glow-3" aria-hidden />
      {/* ───── HERO ───── */}
      <Section className="mx-auto max-w-7xl px-4 pt-20 pb-8 sm:px-6 sm:pt-28">
        <div className="flex flex-col items-center text-center">
          <motion.div
            initial={prefersReduced ? {} : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="mb-6 inline-flex items-center gap-1.5 rounded-full border border-border bg-white px-4 py-1.5 text-xs font-semibold text-primary shadow-sm">
              <Sparkles className="size-3.5" />
              AI-Powered Resume Optimisation
            </span>
          </motion.div>

          <motion.h1
            initial={prefersReduced ? {} : { opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="font-heading max-w-3xl text-4xl font-extrabold leading-[1.1] tracking-tight text-foreground sm:text-5xl lg:text-6xl"
          >
            Your Resume,{" "}
            <span className="gradient-text">Optimised</span> for the
            Algorithms That Matter
          </motion.h1>

          <motion.p
            initial={prefersReduced ? {} : { opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mt-4 max-w-2xl text-balance text-base leading-relaxed text-foreground/60 sm:text-lg"
          >
            Stop guessing what ATS filters look for. Upload your resume, paste a
            job description, and get an AI-powered match score, keyword analysis,
            and rewrite — all in seconds.
          </motion.p>

          <motion.div
            initial={prefersReduced ? {} : { opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-8 flex flex-wrap items-center justify-center gap-3"
          >
            <Button size="lg" onClick={() => { fireConfetti(); navigate("/analyze"); }}>
              Try the live demo
              <ArrowRight className="size-4" />
            </Button>
            <Button variant="outline" size="lg" onClick={() => document.getElementById("features")?.scrollIntoView({ behavior: "smooth" })}>
              See how it works
            </Button>
          </motion.div>

          <motion.p
            initial={prefersReduced ? {} : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.45 }}
            className="mt-4 text-xs text-foreground/40"
          >
            No signup required · Powered by{" "}
            <span className="font-medium text-foreground/60">Gemini AI</span>
            · 100% free to try
          </motion.p>
        </div>

        {/* Product mockup card with glow effect */}
        <motion.div
          initial={prefersReduced ? {} : { opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.45 }}
          className="mx-auto mt-12 max-w-3xl"
        >
          <div className="relative">
            {/* Glow behind card */}
            <div className="absolute -inset-4 rounded-3xl bg-gradient-to-br from-primary/20 via-accent/10 to-secondary/20 opacity-50 blur-2xl" aria-hidden />
            <Card className="relative overflow-hidden !p-0 !border-0 shadow-2xl shadow-primary/15">
              <div className="bg-gradient-to-br from-primary/5 via-white to-accent/5 p-6 sm:p-8">
                <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start sm:gap-8">
                  <ScoreGauge score={78} size={120} />
                  <div className="flex-1 space-y-4">
                    <div className="flex flex-wrap gap-1.5">
                      {["React", "TypeScript", "Figma", "Agile", "SaaS"].map((kw) => (
                        <Badge key={kw} tone="success">{kw}</Badge>
                      ))}
                      {["GraphQL", "AWS", "Python"].map((kw) => (
                        <Badge key={kw} tone="danger">{kw}</Badge>
                      ))}
                    </div>
                    <div className="space-y-1.5">
                      {[
                        { name: "Keywords", val: 82 },
                        { name: "Experience", val: 74 },
                        { name: "Format", val: 88 },
                        { name: "Impact", val: 70 },
                      ].map(({ name, val }) => (
                        <div key={name} className="flex items-center gap-2">
                          <span className="w-20 shrink-0 text-[11px] font-semibold text-foreground/50">{name}</span>
                          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
                            <div
                              className="h-full rounded-full transition-all duration-700 ease-out"
                              style={{
                                width: `${val}%`,
                                backgroundColor: val >= 80 ? "var(--color-accent)" : val >= 60 ? "#eab308" : "var(--color-destructive)",
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="mt-5 flex items-center justify-center gap-2 text-xs text-foreground/40">
                  <Check className="size-3.5 text-accent" />
                  <span>Real output from ResumePilot AI — try it with your own resume</span>
                </div>
              </div>
            </Card>
          </div>
        </motion.div>
      </Section>

      {/* ───── STATS BAR (animated counters) ───── */}
      <Section className="mx-auto max-w-5xl px-4 py-16">
        <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
          {stats.map((s) => (
            <div key={s.label} className="flex flex-col items-center gap-1.5 text-center">
              <div className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                {s.icon}
              </div>
              <AnimatedCounter value={s.value} suffix={s.value.includes("+") ? "+" : s.value.includes("%") ? "%" : ""} />
              <span className="text-xs text-foreground/50">{s.label}</span>
            </div>
          ))}
        </div>
      </Section>

      {/* ───── FEATURES ───── */}
      <Section id="features" className="mx-auto max-w-7xl px-4 py-16 sm:px-6">
        <div className="mb-12 text-center">
          <h2 className="font-heading text-3xl font-extrabold text-foreground sm:text-4xl">
            Everything you need to <span className="gradient-text">win</span>
          </h2>
          <p className="mt-3 text-base text-foreground/60">
            From ATS scoring to interview prep — one tool, endless advantage.
          </p>
        </div>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <StaggerContainer key={f.title} delay={i * 0.04}>
              <Card hover className="p-6">
                <div className="mb-4 flex size-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  {f.icon}
                </div>
                <h3 className="text-base font-bold text-foreground">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-foreground/60">{f.desc}</p>
              </Card>
            </StaggerContainer>
          ))}
        </div>
      </Section>

      {/* ───── HOW IT WORKS ───── */}
      <Section id="how-it-works" className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
        <div className="mb-12 text-center">
          <h2 className="font-heading text-3xl font-extrabold text-foreground sm:text-4xl">
            Works in <span className="gradient-text">3</span> simple steps
          </h2>
          <p className="mt-3 text-base text-foreground/60">
            No uploads, no accounts, no friction.
          </p>
        </div>
        <div className="relative grid gap-6 sm:grid-cols-3">
          {/* Connecting line (desktop) */}
          <div className="absolute left-1/3 right-1/3 top-12 hidden h-px bg-gradient-to-r from-primary/30 via-primary/60 to-primary/30 sm:block" aria-hidden />
          {steps.map((s, i) => (
            <StaggerContainer key={i} delay={i * 0.12}>
              <Card className="relative z-10 p-6 text-center">
                <div className="mx-auto mb-4 flex size-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-secondary/10 text-primary shadow-sm">
                  {s.icon}
                </div>
                <h3 className="text-base font-bold text-foreground">{s.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-foreground/60">{s.desc}</p>
              </Card>
            </StaggerContainer>
          ))}
        </div>
      </Section>

      {/* ───── TESTIMONIALS ───── */}
      <Section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <div className="mb-12 text-center">
          <h2 className="font-heading text-3xl font-extrabold text-foreground sm:text-4xl">
            Trusted by job seekers like <span className="gradient-text">you</span>
          </h2>
          <p className="mt-3 text-base text-foreground/60">
            Real results from real people.
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {testimonials.map((t, i) => (
            <StaggerContainer key={i} delay={i * 0.08}>
              <Card className="flex h-full flex-col p-6">
                <Quote className="mb-3 size-6 text-primary/30" />
                <p className="flex-1 text-sm leading-relaxed text-foreground/70">
                  "{t.quote}"
                </p>
                <div className="mt-4 flex items-center gap-3 border-t border-border pt-4">
                  <div className="flex size-10 items-center justify-center rounded-full bg-gradient-to-br from-primary/20 to-secondary/20 text-sm font-bold text-primary">
                    {t.author.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-bold text-foreground">{t.author}</p>
                    <p className="text-xs text-foreground/50">{t.role}</p>
                  </div>
                </div>
              </Card>
            </StaggerContainer>
          ))}
        </div>
      </Section>

      {/* ───── PRICING ───── */}
      <Section id="pricing" className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <div className="mb-12 text-center">
          <h2 className="font-heading text-3xl font-extrabold text-foreground sm:text-4xl">
            Simple, transparent <span className="gradient-text">pricing</span>
          </h2>
          <p className="mt-3 text-base text-foreground/60">
            Start free, upgrade when you're serious.
          </p>
        </div>
        <div className="grid gap-6 lg:grid-cols-3">
          {tiers.map((tier, i) => (
            <StaggerContainer key={tier.name} delay={i * 0.08}>
              <Card
                className={`relative flex flex-col p-6 ${
                  tier.popular ? "border-primary/40 shadow-lg shadow-primary/10 ring-1 ring-primary/30" : ""
                }`}
              >
                {tier.popular && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 inline-flex items-center gap-1 rounded-full bg-primary px-4 py-1 text-xs font-bold text-white shadow-md">
                    <Sparkles className="size-3" />
                    Most popular
                  </span>
                )}
                <h3 className="text-lg font-bold text-foreground">{tier.name}</h3>
                <p className="mt-1 text-sm text-foreground/50">{tier.desc}</p>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="font-heading text-4xl font-extrabold text-foreground">{tier.price}</span>
                  {tier.price !== "$0" && <span className="text-sm text-foreground/50">/month</span>}
                </div>
                <ul className="mt-6 flex-1 space-y-3">
                  {tier.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm">
                      <Check className="mt-0.5 size-4 shrink-0 text-accent" />
                      <span className="text-foreground/70">{f}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  variant={tier.popular ? "primary" : "outline"}
                  fullWidth
                  className="mt-8"
                  onClick={() => navigate(tier.href)}
                >
                  {tier.cta}
                </Button>
              </Card>
            </StaggerContainer>
          ))}
        </div>
      </Section>

      {/* ───── BENCHMARK COMPARISON ───── */}
      <Section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <div className="mb-12 text-center">
          <h2 className="font-heading text-3xl font-extrabold text-foreground sm:text-4xl">
            How we <span className="gradient-text">compare</span>
          </h2>
          <p className="mt-3 text-base text-foreground/60">
            No other free tool gives you this much. See for yourself.
          </p>
        </div>
        <div className="overflow-x-auto rounded-2xl border border-border bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                <th className="p-4 font-bold text-foreground">Features</th>
                {benchLabels.map((label, i) => (
                  <th key={label} className={`p-4 text-center font-bold ${i === 0 ? "text-primary" : "text-foreground/50"}`}>
                    {i === 0 && <Sparkles className="mx-auto mb-1 size-4 text-primary" />}
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {benchmarks.map((b) => (
                <tr key={b.feature} className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors">
                  <td className="p-4 font-medium text-foreground/80">{b.feature}</td>
                  {[b.pilot, b.other1, b.other2, b.other3].map((present, ci) => (
                    <td key={ci} className="p-4 text-center">
                      {present ? (
                        <span className="inline-flex size-6 items-center justify-center rounded-full bg-accent/15">
                          <Check className="size-3.5 text-accent" />
                        </span>
                      ) : (
                        <span className="text-foreground/20">—</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-4 text-center text-xs text-foreground/40">
          Comparison based on publicly available feature lists as of July 2025. Features may change.
        </p>
      </Section>

      {/* ───── FAQ ───── */}
      <Section className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <div className="mb-10 text-center">
          <h2 className="font-heading text-3xl font-extrabold text-foreground sm:text-4xl">
            Frequently asked <span className="gradient-text">questions</span>
          </h2>
        </div>
        <div className="space-y-3">
          {faqs.map((faq) => (
            <details key={faq.q} className="group rounded-xl border border-border bg-white transition-all duration-200 open:shadow-md hover:border-primary/20">
              <summary className="flex cursor-pointer items-center justify-between gap-2 p-4 text-sm font-bold text-foreground transition-colors hover:text-primary focus-ring rounded-xl">
                {faq.q}
                <ChevronDown className="size-4 shrink-0 text-foreground/40 transition-transform duration-200 group-open:rotate-180" />
              </summary>
              <div className="border-t border-border px-4 pb-4 pt-3">
                <p className="text-sm leading-relaxed text-foreground/70">{faq.a}</p>
              </div>
            </details>
          ))}
        </div>
      </Section>

      {/* ───── BUILT FOR THE HACKATHON ───── */}
      <Section className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
        <Card className="overflow-hidden !border-0 bg-gradient-to-br from-primary/5 via-white to-accent/5 p-8 sm:p-10 shadow-xl shadow-primary/10">
          <div className="flex flex-col items-center gap-6 text-center">
            <div className="flex size-16 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 shadow-lg shadow-orange-500/25">
              <Trophy className="size-8 text-white" />
            </div>
            <div>
              <h2 className="font-heading text-2xl font-extrabold text-foreground sm:text-3xl">
                Built for the <span className="gradient-text">Kanz Prize</span> x Antler
              </h2>
              <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-foreground/60">
                ResumePilot AI was crafted for the Kanz Hackathon with the Antler prize in mind. 
                We believe every job seeker deserves a fair shot at getting past ATS filters — 
                and AI is the key to levelling the playing field.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-3">
              <a
                href="/ResumePilot_AI_Presentation.pptx"
                download
                className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-white px-5 py-2.5 text-sm font-semibold text-foreground shadow-sm transition-all duration-150 hover:border-primary/40 hover:text-primary hover:shadow-md active:scale-[0.97] focus-ring"
              >
                <Download className="size-4" />
                Download Presentation (PPTX)
              </a>
              <a
                href="/ResumePilot_AI_Presentation.pdf"
                download
                className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-white px-5 py-2.5 text-sm font-semibold text-foreground shadow-sm transition-all duration-150 hover:border-primary/40 hover:text-primary hover:shadow-md active:scale-[0.97] focus-ring"
              >
                <Download className="size-4" />
                Download Presentation (PDF)
              </a>
            </div>
            <p className="text-xs text-foreground/40">
              View our full hackathon submission deck and source code.
            </p>
          </div>
        </Card>
      </Section>

      {/* ───── FINAL CTA ───── */}
      <Section className="mx-auto max-w-4xl px-4 py-16 sm:px-6">
        <Card className="overflow-hidden !border-0 bg-gradient-to-br from-primary via-primary/90 to-secondary p-8 text-center shadow-2xl shadow-primary/30 sm:p-12">
          <h2 className="font-heading text-3xl font-extrabold text-white sm:text-4xl">
            Ready to get past the robots?
          </h2>
          <p className="mx-auto mt-3 max-w-lg text-balance text-base text-white/80">
            Try the live ATS analyzer now — no signup, no credit card, just your
            resume and a job description.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Button
              size="lg"
              className="!bg-white !text-primary hover:!bg-white/90"
              onClick={() => { fireConfetti(); navigate("/analyze"); }}
            >
              Try the live demo
              <ArrowRight className="size-4" />
            </Button>
            <Button
              variant="ghost"
              size="lg"
              className="!text-white/80 hover:!bg-white/10 hover:!text-white"
              onClick={() => navigate("/auth?mode=signup")}
            >
              Create free account
            </Button>
          </div>
          <p className="mt-4 text-xs text-white/50">
            Free forever · No credit card · 5 free analyses per month
          </p>
        </Card>
      </Section>
    </div>
  );
}