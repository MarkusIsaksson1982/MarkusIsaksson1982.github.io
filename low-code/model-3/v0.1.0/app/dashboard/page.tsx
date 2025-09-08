import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { getQuizResultsByUser } from "@/lib/data/quiz";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function DashboardPage() {
  const supabase = createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return redirect("/login?message=You must be logged in to view your dashboard.");
  }

  const quizResults = await getQuizResultsByUser(user.id);

  return (
    <div className="container mx-auto py-12">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold">Your Dashboard</h1>
        <p className="mt-2 text-lg text-muted-foreground">
          Welcome back, {user.email}. Here are your quiz results.
        </p>
      </div>

      <Card className="max-w-3xl mx-auto">
        <CardHeader>
          <CardTitle>Quiz History</CardTitle>
        </CardHeader>
        <CardContent>
          {quizResults.length === 0 ? (
            <p className="text-center text-muted-foreground">
              You haven't completed any quizzes yet.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Quiz Date</TableHead>
                  <TableHead className="text-right">Score</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {quizResults.map((result) => (
                  <TableRow key={result.id}>
                    <TableCell>
                      {new Date(result.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <span className="font-bold text-lg">{result.score}</span>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
