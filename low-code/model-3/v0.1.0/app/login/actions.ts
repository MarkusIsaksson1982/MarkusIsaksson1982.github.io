"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { headers } from "next/headers";

export async function login(formData: FormData) {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const supabase = createClient();

  const { error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    // For better UX, you might want to redirect to a login page with an error message
    // For now, we'll redirect with a query param.
    return redirect("/login?message=Could not authenticate user");
  }

  return redirect("/");
}

// This is an alternative action for a more advanced setup with client-side state
// We can use this later if we want to show inline error messages.
export async function loginWithState(prevState: any, formData: FormData) {
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;
    const supabase = createClient();

    const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
    });

    if (error) {
        return { message: "Could not authenticate user. Please check your credentials." };
    }

    redirect("/");
}
