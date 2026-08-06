import { Link } from "react-router-dom";
import { SiGithub, SiX } from "react-icons/si";
import { FaLinkedin } from "react-icons/fa6";
import { Logo } from "./Navbar";

const columns = [
  {
    title: "Product",
    links: [
      { label: "Live ATS Demo", to: "/analyze" },
      { label: "Features", to: "/#features" },
      { label: "How it works", to: "/#how-it-works" },
      { label: "Pricing", to: "/#pricing" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Dashboard", to: "/dashboard" },
      { label: "Sign in", to: "/auth?mode=signin" },
      { label: "Create account", to: "/auth?mode=signup" },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-border bg-white/60">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6">
        <div className="grid gap-10 md:grid-cols-[1.5fr_1fr_1fr]">
          <div>
            <Logo />
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-foreground/60">
              The AI copilot that gets your resume past the robots — ATS scoring,
              keyword intelligence, rewrites, cover letters and interview prep in one place.
            </p>
            <div className="mt-5 flex gap-2">
              {[
                { icon: <SiGithub className="size-4" />, label: "GitHub", href: "https://github.com" },
                { icon: <FaLinkedin className="size-4" />, label: "LinkedIn", href: "https://linkedin.com" },
                { icon: <SiX className="size-4" />, label: "X (Twitter)", href: "https://x.com" },
              ].map((s) => (
                <a
                  key={s.label}
                  href={s.href}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={s.label}
                  className="flex size-9 cursor-pointer items-center justify-center rounded-lg border border-border bg-white text-foreground/60 transition-all duration-150 hover:border-primary/40 hover:text-primary focus-ring"
                >
                  {s.icon}
                </a>
              ))}
            </div>
          </div>

          {columns.map((col) => (
            <div key={col.title}>
              <h3 className="text-sm font-bold uppercase tracking-wide text-foreground/50">
                {col.title}
              </h3>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      to={l.to}
                      className="text-sm text-foreground/70 transition-colors duration-150 hover:text-primary focus-ring rounded"
                    >
                      {l.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-3 border-t border-border pt-6 sm:flex-row">
          <p className="text-xs text-foreground/50">
            © {new Date().getFullYear()} ResumePilot AI. Built for the Kanz Prize.
          </p>
          <p className="text-xs text-foreground/40">
            AI results are guidance, not guarantees. Always tailor final decisions to your judgement.
          </p>
        </div>
      </div>
    </footer>
  );
}