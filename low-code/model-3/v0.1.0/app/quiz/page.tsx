import { createClient } from "@/lib/supabase/server";
import { getQuizQuestions } from "@/lib/data/quiz"; // Import the data fetching function
import { redirect } from "next/navigation";
// import { QuizForm } from "./_components/quiz-form"; // We will create this next

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
  
  // Log the questions to the server console to verify fetching
  console.log("Fetched questions on the server:", questions);

  return (
    <div className="container mx-auto py-12">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold">Ethical AI & Cyber Safety Quiz</h1>
        <p className="mt-2 text-lg text-muted-foreground">
          Test your knowledge and learn something new.
        </p>
      </div>
      
      {/*
        We will pass the questions to a client component that handles interactivity.
        For now, this is a placeholder for the next step.
      */}
      {/* <QuizForm questions={questions} /> */}
      
      <div className="mt-8 p-8 border rounded-lg bg-card max-w-2xl mx-auto">
        <h2 className="font-semibold text-lg mb-4">Quiz data loaded!</h2>
        <p className="text-muted-foreground">
          {questions.length > 0
            ? `Successfully fetched ${questions.length} questions from the database. Ready to build the interactive UI.`
            : "No questions found in the database. Please add some questions to the 'questions' table in Supabase."}
        </p>
      </div>
    </div>
  );
}
