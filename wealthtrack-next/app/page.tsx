export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-6">Welcome to WealthTrack</h1>
      <p className="text-xl mb-8">Your personal finance tracker</p>
      <a href="/auth" className="bg-primary text-primary-foreground px-6 py-3 rounded-lg">
        Get Started
      </a>
    </main>
  );
}
