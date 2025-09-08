import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export default async function QuizPage() {
  const supabase = createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    // If no user is logged in, protect the route and redirect to the login page.
    // You can also add a message to the query string to inform the user.
    return redirect("/login?message=You must be logged in to view this page.");
  }

  return (
    <div className="container mx-auto py-12 text-center">
      <h1 className="text-3xl font-bold">Welcome to the Quiz!</h1>
      <p className="mt-4 text-lg text-muted-foreground">
        This is a protected page. We're glad you could make it,{" "}
        <span className="font-medium text-foreground">{user.email}</span>.
      </p>
      <div className="mt-8 p-8 border rounded-lg bg-card">
        <p className="text-muted-foreground">
          [Quiz content will be rendered here...]
        </p>
      </div>
    </div>
  );
}
