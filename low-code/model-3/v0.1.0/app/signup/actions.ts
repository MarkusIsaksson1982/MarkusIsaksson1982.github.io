"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { headers } from "next/headers";

export async function signup(formData: FormData) {
  const origin = headers().get("origin");
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const supabase = createClient();

  const { error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      // This email redirect is crucial for the confirmation link
      emailRedirectTo: `${origin}/auth/callback`,
    },
  });

  if (error) {
    console.error("Sign-up error:", error.message);
    return redirect("/signup?message=Could not create account. Please try again.");
  }

  // Redirect user to a page that tells them to check their email
  return redirect("/login?message=Check your email to confirm your account and sign in.");
}
