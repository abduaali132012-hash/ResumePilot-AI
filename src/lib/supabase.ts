import { createClient } from "@supabase/supabase-js";

const supabaseUrl = "https://qdfmneetrmzvozwxchlm.supabase.co";
const supabaseAnonKey =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFkZm1uZWV0cm16dm96d3hjaGxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM0MTk1MDksImV4cCI6MjA5ODk5NTUwOX0.GAyY086Ho57fVExFyx86kL-g2EwiHVZeKsp3i-uDyPA";

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    flowType: "implicit",
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
});