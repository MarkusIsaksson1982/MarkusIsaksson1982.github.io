import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { AuthProvider } from "@/contexts/AuthContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "WealthTrack",
  description: "Personal finance tracker",
};

const queryClient = new QueryClient();

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
            <AuthProvider>
              {children}
              <Toaster />
            </AuthProvider>
          </ThemeProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}
