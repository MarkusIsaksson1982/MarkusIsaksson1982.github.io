import Link from "next/link";
import { BrainCircuit } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex items-center">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <BrainCircuit className="h-6 w-6" />
            <span className="font-bold sm:inline-block">
              AI Safety Hub
            </span>
          </Link>
          <nav className="hidden items-center space-x-6 text-sm font-medium md:flex">
            <Link
              href="/"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Home
            </Link>
            <Link
              href="/quiz"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Quiz
            </Link>
            <Link
              href="/resources"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Resources
            </Link>
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-4">
          <Button variant="ghost">Sign In</Button>
        </div>
      </div>
    </header>
  );
}
