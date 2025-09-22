import Header from "@/components/Header";
import ToolCard from "@/components/ToolCard";
import ClassificationTool from "@/components/ClassificationTool";
import { 
  Search, 
  Eye, 
  TrendingUp, 
  MessageSquare, 
  Bot, 
  Gamepad2, 
  TreePine, 
  BarChart3, 
  Network, 
  Camera,
  Target,
  Shuffle
} from "lucide-react";
import heroImage from "@/assets/ai-hero.jpg";

const Index = () => {
  const aiTools = [
    {
      title: "Sökning & Optimering",
      description: "Algoritmer som hittar optimala lösningar i stora datamängder genom systematisk sökning och utvärdering av alternativ.",
      category: "Algoritmer",
      icon: Search,
      isComing: true
    },
    {
      title: "Objektigenkänning",
      description: "Datorseende som identifierar och klassificerar objekt i bilder och video med hjälp av neurala nätverk.",
      category: "Vision",
      icon: Eye,
      isComing: true
    },
    {
      title: "Prediktion & Regression",
      description: "Maskininlärning för att förutsäga framtida värden baserat på historiska data och mönster.",
      category: "Prediktion",  
      icon: TrendingUp,
      isComing: true
    },
    {
      title: "Naturlig Språkbearbetning",
      description: "AI som förstår, tolkar och genererar mänskligt språk för översättning, analys och kommunikation.",
      category: "NLP",
      icon: MessageSquare,
      isComing: true
    },
    {
      title: "Spelagenter",
      description: "Intelligenta agenter som lär sig strategier och optimerar sitt spelande genom reinforcement learning.",
      category: "Agenter",
      icon: Gamepad2,
      isComing: true
    },
    {
      title: "Beslutsträd",
      description: "Träd-baserade algoritmer som fattar beslut genom att dela upp problem i mindre, hanterbara delar.",
      category: "Algoritmer",
      icon: TreePine,
      isComing: true
    },
    {
      title: "Övervakat Lärande",
      description: "Maskininlärning med märkt träningsdata där algoritmen lär sig från exempel med kända svar.",
      category: "ML",
      icon: Target,
      isComing: true
    },
    {
      title: "Oövervakat Lärande", 
      description: "Maskininlärning som hittar dolda mönster i omärkt data utan förutbestämda kategorier.",
      category: "ML",
      icon: Shuffle,
      isComing: true
    },
    {
      title: "Robotik & Automation",
      description: "Fysiska och virtuella robotar som utför uppgifter autonomt med hjälp av sensorer och AI.",
      category: "Robotik",
      icon: Bot,
      isComing: true
    },
    {
      title: "Generativ AI",
      description: "AI som skapar nytt innehåll som text, bilder, musik och kod baserat på träningsdata.",
      category: "Generativ",
      icon: Network,
      isComing: true
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-hero opacity-10"></div>
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-20"
          style={{ backgroundImage: `url(${heroImage})` }}
        ></div>
        <div className="relative container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-primary bg-clip-text text-transparent">
            AI Verktygsbox för Gymnasiet
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
            Utforska artificiell intelligens genom interaktiva verktyg som täcker hela gymnasiekursen. 
            Från klassificering till neurala nätverk - lär dig AI genom praktisk tillämpning.
          </p>
          <div className="flex justify-center space-x-4 text-sm text-muted-foreground">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-primary rounded-full"></div>
              <span>Följer läroplan ARTI1000X</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-accent rounded-full"></div>
              <span>Interaktiv inlärning</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-success rounded-full"></div>
              <span>Praktiska exempel</span>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Tool Section */}
      <section className="py-16 bg-secondary/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Utvalda Verktyg</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Börja din AI-resa med vårt interaktiva klassificeringsverktyg. Förstå grunderna 
              i maskininlärning genom praktiska exempel.
            </p>
          </div>
          <div className="max-w-4xl mx-auto">
            <ClassificationTool />
          </div>
        </div>
      </section>

      {/* Tools Grid Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Alla AI-Verktyg</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Komplett verktygsuppsättning som täcker hela AI-kursen enligt gymnasieskolans läroplan.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            <ToolCard
              title="Klassificering"
              description="Interaktiv demo som visar hur AI klassificerar text, bilder eller data i olika kategorier med hjälp av maskininlärning."
              category="ML"
              icon={BarChart3}
              isActive={true}
            />
            {aiTools.map((tool, index) => (
              <ToolCard
                key={index}
                title={tool.title}
                description={tool.description}
                category={tool.category}
                icon={tool.icon}
                isComing={tool.isComing}
              />
            ))}
          </div>

          {/* Learning Objectives */}
          <div className="bg-gradient-secondary rounded-2xl p-8 shadow-elegant">
            <h3 className="text-2xl font-bold mb-6 text-center">Kursmål enligt Läroplan</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                  <Network className="h-6 w-6 text-primary-foreground" />
                </div>
                <h4 className="font-semibold mb-2">AI-kunskap</h4>
                <p className="text-sm text-muted-foreground">Kunskaper om AI, dess tillämpningar, tekniker och beståndsdelar</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-accent rounded-full flex items-center justify-center mx-auto mb-4">
                  <Target className="h-6 w-6 text-accent-foreground" />
                </div>
                <h4 className="font-semibold mb-2">Problemlösning</h4>
                <p className="text-sm text-muted-foreground">Förmåga att använda AI i problemlösning</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-success rounded-full flex items-center justify-center mx-auto mb-4">
                  <Eye className="h-6 w-6 text-success-foreground" />
                </div>
                <h4 className="font-semibold mb-2">Etik & Samhälle</h4>
                <p className="text-sm text-muted-foreground">Resonera om möjligheter och risker med AI för samhället</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-primary/5 py-12 mt-16">
        <div className="container mx-auto px-4 text-center">
          <p className="text-muted-foreground mb-4">
            Skapad enligt gymnasieskolans läroplan för Artificiell Intelligens (ARTI1000X)
          </p>
          <div className="flex justify-center space-x-6 text-sm text-muted-foreground">
            <span>100 poäng | Nivå 1</span>
            <span>•</span>
            <span>Gäller från 1 juli 2025</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;