import { createClient } from "@/lib/supabase/server";

export type Resource = {
  id: string;
  title: string;
  summary: string;
  link: string;
  category: string | null;
  created_at: string;
};

export async function getResources(): Promise<Resource[]> {
  const supabase = createClient();

  const { data, error } = await supabase
    .from("resources")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Error fetching resources:", error.message);
    return [];
  }

  return data as Resource[];
}
