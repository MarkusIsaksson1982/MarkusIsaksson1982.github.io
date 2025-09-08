import { getResources } from "@/lib/data/resources";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default async function ResourcesPage() {
  const resources = await getResources();

  return (
    <div className="container mx-auto py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold">Educational Resources</h1>
        <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
          Explore a curated collection of articles, videos, and guides on AI ethics and cyber safety to deepen your knowledge.
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        {resources.length === 0 ? (
          <div className="md:col-span-2 lg:col-span-3 text-center text-muted-foreground">
            No resources found. Please add content to the `resources` table.
          </div>
        ) : (
          resources.map((resource) => (
            <Card key={resource.id} className="flex flex-col justify-between">
              <CardHeader>
                <div className="flex justify-between items-start mb-2">
                  <CardTitle className="text-lg">{resource.title}</CardTitle>
                  {resource.category && <Badge variant="secondary">{resource.category}</Badge>}
                </div>
                <CardDescription>{resource.summary}</CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                <p>
                  <span className="font-medium">Published: </span>
                  {new Date(resource.created_at).toLocaleDateString()}
                </p>
              </CardContent>
              <CardFooter>
                <Link href={resource.link} className="flex items-center text-primary hover:underline" target="_blank" rel="noopener noreferrer">
                  Read More <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </CardFooter>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
