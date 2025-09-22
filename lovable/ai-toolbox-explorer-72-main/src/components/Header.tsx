import { Brain, BookOpen, Zap } from "lucide-react";

const Header = () => {
  return (
    <header className="bg-gradient-primary text-primary-foreground py-6 shadow-glow">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
              <Brain className="h-8 w-8" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">AI Verktygsbox</h1>
              <p className="text-primary-foreground/80 text-sm">Artificiell Intelligens för Gymnasiet</p>
            </div>
          </div>
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-primary-foreground/80">
              <BookOpen className="h-5 w-5" />
              <span className="text-sm">Läroplan</span>
            </div>
            <div className="flex items-center space-x-2 text-primary-foreground/80">
              <Zap className="h-5 w-5" />
              <span className="text-sm">Interaktiv</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;