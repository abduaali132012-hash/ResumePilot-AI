import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import type { User, Session } from "@supabase/supabase-js";
import { supabase } from "./supabase";

interface AuthState {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ error?: string }>;
  signUp: (email: string, password: string) => Promise<{ error?: string; userCreated?: boolean }>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signIn = useCallback(
    async (email: string, password: string): Promise<{ error?: string }> => {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      if (error) {
        if (error.message.includes("Email not confirmed")) {
          return { error: "Please confirm your email address first. Check your inbox for the confirmation link." };
        }
        return { error: error.message };
      }
      return {};
    },
    []
  );

  const signUp = useCallback(
    async (
      email: string,
      password: string
    ): Promise<{ error?: string; userCreated?: boolean }> => {
      const { data, error } = await supabase.auth.signUp({ email, password });
      if (error) return { error: error.message };

      const userCreated = !!data.user?.identities?.length;
      return { userCreated };
    },
    []
  );

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
    setUser(null);
    setSession(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, session, loading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}