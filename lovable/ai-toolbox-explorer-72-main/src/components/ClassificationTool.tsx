import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, RotateCcw, Brain } from "lucide-react";

interface DataPoint {
  id: number;
  text: string;
  actualCategory: 'positiv' | 'negativ';
  aiPrediction?: 'positiv' | 'negativ';
  confidence?: number;
}

const sampleData: DataPoint[] = [
  { id: 1, text: "Jag älskar den här filmen!", actualCategory: 'positiv' },
  { id: 2, text: "Denna produkt är fruktansvärd", actualCategory: 'negativ' },
  { id: 3, text: "Fantastisk service och kvalitet", actualCategory: 'positiv' },
  { id: 4, text: "Väldigt besviken på resultatet", actualCategory: 'negativ' },
  { id: 5, text: "Rekommenderar starkt till alla", actualCategory: 'positiv' },
  { id: 6, text: "Funktionen fungerar inte alls", actualCategory: 'negativ' },
];

const ClassificationTool = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [results, setResults] = useState<DataPoint[]>([]);
  const [isClassifying, setIsClassifying] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });

  const simulateAIClassification = (text: string): { prediction: 'positiv' | 'negativ', confidence: number } => {
    // Simple simulation based on keywords
    const positiveWords = ['älskar', 'fantastisk', 'rekommenderar', 'bra', 'perfekt', 'utmärkt'];
    const negativeWords = ['fruktansvärd', 'besviken', 'fungerar inte', 'dålig', 'hemsk'];
    
    const hasPositive = positiveWords.some(word => text.toLowerCase().includes(word));
    const hasNegative = negativeWords.some(word => text.toLowerCase().includes(word));
    
    let prediction: 'positiv' | 'negativ';
    let baseConfidence = 0.7;
    
    if (hasPositive && !hasNegative) {
      prediction = 'positiv';
      baseConfidence = 0.85;
    } else if (hasNegative && !hasPositive) {
      prediction = 'negativ';
      baseConfidence = 0.85;
    } else {
      prediction = Math.random() > 0.5 ? 'positiv' : 'negativ';
      baseConfidence = 0.6;
    }
    
    const confidence = Math.round((baseConfidence + Math.random() * 0.2) * 100) / 100;
    return { prediction, confidence };
  };

  const classifyCurrentItem = () => {
    setIsClassifying(true);
    
    setTimeout(() => {
      const currentItem = sampleData[currentIndex];
      const { prediction, confidence } = simulateAIClassification(currentItem.text);
      
      const classifiedItem = {
        ...currentItem,
        aiPrediction: prediction,
        confidence
      };
      
      const isCorrect = prediction === currentItem.actualCategory;
      setResults(prev => [...prev, classifiedItem]);
      setScore(prev => ({ 
        correct: prev.correct + (isCorrect ? 1 : 0), 
        total: prev.total + 1 
      }));
      
      setIsClassifying(false);
      setCurrentIndex(prev => prev + 1);
    }, 1500);
  };

  const reset = () => {
    setCurrentIndex(0);
    setResults([]);
    setScore({ correct: 0, total: 0 });
  };

  const currentItem = sampleData[currentIndex];
  const isComplete = currentIndex >= sampleData.length;
  const accuracy = score.total > 0 ? Math.round((score.correct / score.total) * 100) : 0;

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-card shadow-elegant">
        <CardHeader>
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary rounded-lg">
              <Brain className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <CardTitle className="text-xl">AI Klassificering Demo</CardTitle>
              <CardDescription>
                Utforska hur AI klassificerar text som positiv eller negativ sentiment
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {!isComplete && currentItem ? (
            <div className="space-y-4">
              <div className="bg-secondary/50 p-4 rounded-lg">
                <h3 className="font-medium mb-2">Text att klassificera:</h3>
                <p className="text-lg italic">"{currentItem.text}"</p>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  Objekt {currentIndex + 1} av {sampleData.length}
                </div>
                <Button 
                  onClick={classifyCurrentItem} 
                  disabled={isClassifying}
                  className="bg-gradient-primary hover:opacity-90"
                >
                  {isClassifying ? "AI Analyserar..." : "Klassificera med AI"}
                </Button>
              </div>
            </div>
          ) : (
            <div className="text-center space-y-4">
              <div className="text-2xl font-bold text-primary">
                Demo Slutförd! 🎉
              </div>
              <div className="text-lg">
                Noggrannhet: <span className="font-bold text-primary">{accuracy}%</span>
              </div>
              <Button onClick={reset} variant="outline" className="mt-4">
                <RotateCcw className="h-4 w-4 mr-2" />
                Kör igen
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {results.length > 0 && (
        <Card className="bg-gradient-card">
          <CardHeader>
            <CardTitle className="text-lg">Klassificeringsresultat</CardTitle>
            <CardDescription>
              Noggrannhet: {score.correct}/{score.total} korrekt ({accuracy}%)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.map((result) => (
                <div key={result.id} className="flex items-center justify-between p-3 bg-background rounded-lg border">
                  <div className="flex-1">
                    <p className="text-sm mb-2">"{result.text}"</p>
                    <div className="flex items-center space-x-2">
                      <Badge variant={result.aiPrediction === 'positiv' ? 'default' : 'destructive'}>
                        AI: {result.aiPrediction}
                      </Badge>
                      <Badge variant="outline">
                        Säkerhet: {result.confidence ? `${Math.round(result.confidence * 100)}%` : 'N/A'}
                      </Badge>
                    </div>
                  </div>
                  <div className="ml-4">
                    {result.aiPrediction === result.actualCategory ? (
                      <CheckCircle className="h-6 w-6 text-success" />
                    ) : (
                      <XCircle className="h-6 w-6 text-destructive" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ClassificationTool;