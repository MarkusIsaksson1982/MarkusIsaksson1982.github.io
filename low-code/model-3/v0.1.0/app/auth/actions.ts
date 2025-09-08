"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export async function logout() {
  const supabase = createClient();
  const { error } = await supabase.auth.signOut();

  if (error) {
    console.error("Logout error:", error.message);
    // Optionally redirect with an error message
    return redirect("/?message=Could not log out.");
  }

  return redirect("/login");
}
