import { getLeaderboard } from "@/lib/data/quiz";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Crown } from "lucide-react";

// Helper function to mask emails for privacy
const maskEmail = (email: string) => {
  const [user, domain] = email.split("@");
  if (user.length <= 2) {
    return `${user.slice(0, 1)}***@${domain}`;
  }
  return `${user.slice(0, 2)}***@${domain}`;
};

export default async function LeaderboardPage() {
  const leaderboardData = await getLeaderboard();

  return (
    <div className="container mx-auto py-12">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold">Top Scorers Leaderboard</h1>
        <p className="mt-2 text-lg text-muted-foreground">
          See how you stack up against the competition!
        </p>
      </div>

      <Card className="max-w-3xl mx-auto">
        <CardHeader>
          <CardTitle>Top 10 High Scores</CardTitle>
        </CardHeader>
        <CardContent>
          {leaderboardData.length === 0 ? (
            <p className="text-center text-muted-foreground">
              No scores have been recorded yet. Be the first!
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[80px]">Rank</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead className="text-right">High Score</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {leaderboardData.map((entry, index) => (
                  <TableRow key={entry.user_id}>
                    <TableCell className="font-bold text-lg text-center">
                      {index === 0 ? <Crown className="h-6 w-6 text-yellow-500" /> : index + 1}
                    </TableCell>
                    <TableCell>{maskEmail(entry.email)}</TableCell>
                    <TableCell className="text-right font-bold text-lg">
                      {entry.max_score}
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
