import Link from "next/link";
import { signup } from "./actions"; // Import the Server Action
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

// The page now accepts searchParams to display messages
export default function SignupPage({
  searchParams,
}: {
  searchParams: { message: string };
}) {
  return (
    <div className="container flex items-center justify-center py-12">
      <Card className="mx-auto w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-2xl">Create an Account</CardTitle>
          <CardDescription>
            Enter your email and a password to get started.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* The form now calls the 'signup' server action */}
          <form action={signup} className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="m@example.com"
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" name="password" type="password" required />
            </div>
            {searchParams.message && (
              <div
                className={`text-sm font-medium ${
                  searchParams.message.includes("Check your email")
                    ? "text-foreground"
                    : "text-destructive"
                }`}
              >
                {searchParams.message}
              </div>
            )}
            <Button type="submit" className="w-full mt-2">
              Sign Up
            </Button>
          </form>
          <div className="mt-4 text-center text-sm">
            Already have an account?{" "}
            <Link href="/login" className="underline">
              Sign in
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
