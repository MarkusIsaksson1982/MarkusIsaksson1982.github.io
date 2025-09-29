import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LucideIcon } from "lucide-react";

interface ToolCardProps {
  title: string;
  description: string;
  category: string;
  icon: LucideIcon;
  isActive?: boolean;
  isComing?: boolean;
}

const ToolCard = ({ title, description, category, icon: Icon, isActive = false, isComing = false }: ToolCardProps) => {
  return (
    <Card className={`transition-all duration-300 hover:shadow-elegant hover:-translate-y-1 cursor-pointer ${
      isActive ? 'bg-gradient-secondary border-primary shadow-glow' : 'bg-gradient-card'
    } ${isComing ? 'opacity-75' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className={`p-2 rounded-lg ${isActive ? 'bg-primary text-primary-foreground' : 'bg-primary/10 text-primary'}`}>
            <Icon className="h-6 w-6" />
          </div>
          <div className="flex gap-2">
            <Badge variant={isActive ? "default" : "secondary"} className="text-xs">
              {category}
            </Badge>
            {isComing && (
              <Badge variant="outline" className="text-xs">
                Kommer snart
              </Badge>
            )}
          </div>
        </div>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-sm leading-relaxed">
          {description}
        </CardDescription>
      </CardContent>
    </Card>
  );
};

export default ToolCard;