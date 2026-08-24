import type { Metadata } from "next";
import { AuthProvider } from "@/components/auth-context";
import { NavBar } from "@/components/NavBar";
import "./globals.css";

export const metadata: Metadata = {
  title: "CodeAtlas",
  description:
    "A personal coding intelligence system that learns how you code — and teaches you what you need next.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col bg-neutral-50 text-neutral-900">
        <AuthProvider>
          <NavBar />
          <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-8">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
