import "./globals.css";
import ConditionalLayout from "@/components/ConditionalLayout";

export const metadata = {
  title: "PGF – Plataforma de Gestión de Flota",
  description: "Sistema de control de flota y órdenes de trabajo.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className="bg-gray-100 dark:bg-gray-900 transition-colors duration-300">
        <ConditionalLayout>{children}</ConditionalLayout>
      </body>
    </html>
  );
}
