"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export async function saveQuizResult(score: number) {
  const supabase = createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    // This is a failsafe. The route is protected, but we double-check.
    return redirect("/login?message=You must be logged in to save your score.");
  }

  const { error } = await supabase
    .from("quiz_results")
    .insert({ user_id: user.id, score });

  if (error) {
    console.error("Error saving quiz result:", error.message);
    // In a real application, you might use a toast or redirect with an error.
    return { success: false, message: "Failed to save quiz result." };
  }

  return { success: true, message: "Quiz result saved successfully!" };
}
