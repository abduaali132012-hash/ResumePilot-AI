import { Link, NavLink, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import {
  LogOut,
  Menu,
  ScanSearch,
  Sparkles,
  X,
} from "lucide-react";
import { useAuth } from "../lib/store";
import { Button } from "./ui";

export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link to="/" className={`group flex items-center gap-2 ${className}`} aria-label="ResumePilot AI home">
      <span className="flex size-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-secondary shadow-md shadow-primary/25 transition-transform duration-200 group-hover:scale-105">
        <ScanSearch className="size-5 text-white" aria-hidden />
      </span>
      <span className="font-heading text-lg font-bold tracking-tight text-foreground">
        ResumePilot<span className="gradient-text"> AI</span>
      </span>
    </Link>
  );
}

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-150 focus-ring ${
    isActive
      ? "bg-muted text-primary"
      : "text-foreground/70 hover:bg-muted/70 hover:text-foreground"
  }`;

export default function Navbar() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const handleSignOut = async () => {
    setMobileOpen(false);
    await signOut();
    navigate("/");
  };

  const links = (
    <>
      <NavLink to="/analyze" className={navLinkClass}>
        Live Demo
      </NavLink>
      <NavLink to="/applications" className={navLinkClass}>
        <span className="hidden lg:inline">Applications</span>
        <span className="lg:hidden">Apps</span>
      </NavLink>
      <NavLink to="/dashboard" className={navLinkClass}>
        Dashboard
      </NavLink>
    </>
  );

  return (
    <header
      className={`sticky top-0 z-50 w-full transition-all duration-300 ${
        scrolled ? "glass-strong shadow-sm" : "bg-transparent"
      }`}
    >
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6" aria-label="Main">
        <Logo />

        {/* Desktop */}
        <div className="hidden items-center gap-1 md:flex">
          {links}
        </div>

        <div className="hidden items-center gap-2 md:flex">
          {user ? (
            <>
              <span className="mr-1 hidden max-w-44 truncate text-sm text-foreground/60 lg:block">
                {user.email}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSignOut}
                aria-label="Sign out"
              >
                <LogOut className="size-4" aria-hidden />
                Sign out
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="sm" onClick={() => navigate("/auth?mode=signin")}>
                Sign in
              </Button>
              <Button size="sm" onClick={() => navigate("/auth?mode=signup")}>
                <Sparkles className="size-4" aria-hidden />
                Get started
              </Button>
            </>
          )}
        </div>

        {/* Mobile toggle */}
        <button
          className="flex size-10 cursor-pointer items-center justify-center rounded-lg text-foreground/70 transition-colors hover:bg-muted focus-ring md:hidden"
          onClick={() => setMobileOpen((o) => !o)}
          aria-expanded={mobileOpen}
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
        >
          {mobileOpen ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>
      </nav>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="glass-strong border-t border-border px-4 py-3 md:hidden">
          <div className="flex flex-col gap-1">
            {links}
            <div className="mt-2 flex flex-col gap-2 border-t border-border pt-3">
              {user ? (
                <>
                  <p className="truncate px-1 text-sm text-foreground/60">{user.email}</p>
                  <Button variant="outline" onClick={handleSignOut} fullWidth>
                    <LogOut className="size-4" aria-hidden />
                    Sign out
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="outline" onClick={() => { setMobileOpen(false); navigate("/auth?mode=signin"); }} fullWidth>
                    Sign in
                  </Button>
                  <Button onClick={() => { setMobileOpen(false); navigate("/auth?mode=signup"); }} fullWidth>
                    <Sparkles className="size-4" aria-hidden />
                    Get started free
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}