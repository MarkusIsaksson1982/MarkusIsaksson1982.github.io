import { submitFeedback } from "./actions";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export default function FeedbackPage({
  searchParams,
}: {
  searchParams: { message: string };
}) {
  const isSuccess = searchParams.message?.includes("Thank you");

  return (
    <div className="container flex items-center justify-center py-12">
      <Card className="mx-auto w-full max-w-xl">
        <CardHeader>
          <CardTitle className="text-2xl">Give Us Your Feedback</CardTitle>
          <CardDescription>
            Have a suggestion or found an issue? Let us know!
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form action={submitFeedback} className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Your Name (Optional)</Label>
              <Input id="name" name="name" type="text" placeholder="Jane Doe" />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="email">Your Email (Optional)</Label>
              <Input id="email" name="email" type="email" placeholder="jane.doe@example.com" />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="message">Message</Label>
              <Textarea
                id="message"
                name="message"
                placeholder="I love the quizzes! What about a leaderboard?"
                required
              />
            </div>
            {searchParams.message && (
              <div
                className={`text-sm font-medium ${
                  isSuccess ? "text-primary" : "text-destructive"
                }`}
              >
                {searchParams.message}
              </div>
            )}
            <Button type="submit" className="w-full mt-2">
              Submit Feedback
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
