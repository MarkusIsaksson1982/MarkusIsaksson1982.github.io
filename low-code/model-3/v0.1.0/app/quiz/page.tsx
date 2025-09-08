import { createClient } from "@/lib/supabase/server";
import { getQuizQuestions } from "@/lib/data/quiz";
import { redirect } from "next/navigation";
import { QuizForm } from "./_components/quiz-form"; // Import the client component

export default async function QuizPage() {
  const supabase = createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return redirect("/login?message=You must be logged in to take the quiz.");
  }

  // Fetch the quiz questions on the server
  const questions = await getQuizQuestions();
  
  return (
    <div className="container mx-auto py-12">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold">Ethical AI & Cyber Safety Quiz</h1>
        <p className="mt-2 text-lg text-muted-foreground">
          Test your knowledge and learn something new.
        </p>
      </div>
      
      {/*
        Pass the server-fetched questions as a prop to the client component.
        This is a key Next.js pattern: Fetch on the server, render on the client.
      */}
      <QuizForm questions={questions} />
    </div>
  );
}
