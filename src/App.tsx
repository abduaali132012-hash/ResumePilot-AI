import { Suspense, lazy, useEffect } from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "./lib/store";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import { Spinner } from "./components/ui";

/* Route-level code splitting — each page chunk downloads only when visited,
   shrinking the initial bundle to the shell (nav, footer, shared UI). */
const LandingPage = lazy(() => import("./pages/LandingPage"));
const AnalyzePage = lazy(() => import("./pages/AnalyzePage"));
const AuthPage = lazy(() => import("./pages/AuthPage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const HistoryDetailPage = lazy(() => import("./pages/HistoryDetailPage"));
const ApplicationsPage = lazy(() => import("./pages/ApplicationsPage"));

/* Scroll to top on route change (unless hash anchor) */
function ScrollToTop() {
  const { pathname, hash } = useLocation();
  useEffect(() => {
    if (!hash) window.scrollTo({ top: 0, behavior: "instant" as ScrollBehavior });
  }, [pathname, hash]);
  return null;
}

/* Fallback shown while a route chunk loads */
function PageFallback() {
  return (
    <div
      role="status"
      aria-label="Loading page"
      className="flex min-h-[60vh] flex-col items-center justify-center gap-4"
    >
      <Spinner className="size-8" />
      <p className="text-sm text-foreground/50">Loading…</p>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ScrollToTop />
        <a href="#main-content" className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-primary focus:rounded-lg focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-ring">
          Skip to content
        </a>
        <div className="flex min-h-screen flex-col bg-background text-foreground">
          <Navbar />
          <main id="main-content" className="flex-1">
            <Suspense fallback={<PageFallback />}>
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/analyze" element={<AnalyzePage />} />
                <Route path="/auth" element={<AuthPage />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/applications" element={<ApplicationsPage />} />
                <Route path="/analysis/:id" element={<HistoryDetailPage />} />
                <Route path="*" element={<LandingPage />} />
              </Routes>
            </Suspense>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}
