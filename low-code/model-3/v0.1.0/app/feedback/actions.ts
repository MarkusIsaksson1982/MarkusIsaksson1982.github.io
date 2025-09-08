"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export async function submitFeedback(formData: FormData) {
  const supabase = createClient();

  const name = formData.get("name") as string | null;
  const email = formData.get("email") as string | null;
  const message = formData.get("message") as string;

  if (!message) {
    return redirect("/feedback?message=Please provide a message.");
  }

  const { error } = await supabase
    .from("feedback")
    .insert({ name, email, message });

  if (error) {
    console.error("Error submitting feedback:", error.message);
    return redirect("/feedback?message=Failed to submit feedback. Please try again.");
  }

  return redirect("/feedback?message=Thank you for your feedback! We appreciate it.");
}
