import { createClient } from "@/lib/supabase/server";

export type Question = {
  id: string;
  text: string;
  options: string[];
  correct_answer: string;
  category: string | null;
};

export type QuizResult = {
  id: string;
  user_id: string;
  score: number;
  created_at: string;
};

export async function getQuizQuestions(): Promise<Question[]> {
  const supabase = createClient();

  const { data, error } = await supabase.from("questions").select("*");

  if (error) {
    console.error("Error fetching quiz questions:", error.message);
    return [];
  }

  return data.map((q) => ({
    ...q,
    options: Array.isArray(q.options) ? q.options : [],
  }));
}

export async function getQuizResultsByUser(userId: string): Promise<QuizResult[]> {
  const supabase = createClient();

  const { data, error } = await supabase
    .from("quiz_results")
    .select("*")
    .eq("user_id", userId)
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Error fetching quiz results:", error.message);
    return [];
  }

  return data as QuizResult[];
}

export type LeaderboardEntry = {
  user_id: string;
  email: string;
  max_score: number;
};

export async function getLeaderboard(): Promise<LeaderboardEntry[]> {
  const supabase = createClient();

  // Call the PostgreSQL function we created
  const { data, error } = await supabase.rpc('get_leaderboard');

  if (error) {
    console.error("Error fetching leaderboard data:", error.message);
    return [];
  }

  return data as LeaderboardEntry[];
}
