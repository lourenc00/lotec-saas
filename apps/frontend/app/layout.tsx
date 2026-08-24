import type {Metadata} from "next";
import "./globals.css";
import Providers from "@/lib/providers";

export const metadata: Metadata = {
  title: "Lotec - Gestão de Assistências Técnicas",
  description: "Plataforma SaaS para gestão de assistências técnicas",
};

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="pt-BR">
      <body className="bg-gray-50 text-gray-900 min-h-screen">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
