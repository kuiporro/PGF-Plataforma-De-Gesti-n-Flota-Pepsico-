import "./globals.css";
import Sidebar from "@/components/Sidebar";
import Topbar from "@/components/Topbar";
import ThemeToggle from "@/components/ThemeToggle";

export const metadata = {
  title: "PGF – Plataforma de Gestión de Flota",
  description: "Sistema de control de flota y órdenes de trabajo.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className="bg-gray-100 dark:bg-gray-900 transition-colors duration-300">
        <div className="flex min-h-screen bg-gray-100">
          {/* SIDEBAR */}
          <Sidebar />
          <main className="flex-1 p-6 min-h-screen text-gray-800 dark:text-gray-200 transition-colors duration-300">
            <ThemeToggle />
            {children}

          </main>

          {/* CONTENIDO */}
          <div className="flex-1 flex flex-col">
            <Topbar />

            <main className="flex-1 p-6 min-h-screen text-gray-800 dark:text-gray-200 transition-colors duration-300">
              
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
