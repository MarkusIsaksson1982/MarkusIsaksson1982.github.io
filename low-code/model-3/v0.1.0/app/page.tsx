import { Button } from "@/components/ui/button"; // We will create this component soon

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center">
        <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
          Ethical AI & Cyber Safety Learning Hub
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Your journey to understanding AI and staying safe online starts here.
        </p>
        <Button size="lg" className="mt-8">
          Start the Quiz
        </Button>
      </div>
    </main>
  );
}
