"use client";

import { useAuth } from "@/lib/auth-context";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/dashboard/clientes", label: "Clientes", icon: "👥" },
  { href: "/dashboard/aparelhos", label: "Aparelhos", icon: "📱" },
  { href: "/dashboard/os", label: "Ordens de Serviço", icon: "🔧" },
  { href: "/dashboard/relatorios", label: "Relatórios", icon: "📈" },
  { href: "/dashboard/assinatura", label: "Assinatura", icon: "💳" },
];

function AppContent({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Carregando...</div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen flex bg-gray-50">
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 flex flex-col transform transition-transform lg:transform-none ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-blue-600">Lotec</h1>
          <p className="text-xs text-gray-400 mt-1">Assistências Técnicas</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive =
              item.href === "/dashboard"
                ? pathname === "/dashboard"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-blue-50 text-blue-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-3 border-t border-gray-200">
          {user.is_super_admin && (
            <Link
              href="/admin"
              onClick={() => setSidebarOpen(false)}
              className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-100 mb-2"
            >
              <span>⚡</span>
              Super Admin
            </Link>
          )}
          <div className="text-sm font-medium text-gray-700 truncate px-3 py-1">
            {user.name}
          </div>
          <div className="text-xs text-gray-400 truncate px-3 mb-2">
            {user.email}
          </div>
          <button
            onClick={logout}
            className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md"
          >
            Sair
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-gray-600 hover:text-gray-900"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h2 className="text-lg font-semibold text-gray-800">
            {NAV_ITEMS.find(
              (i) =>
                i.href === "/dashboard"
                  ? pathname === "/dashboard"
                  : pathname.startsWith(i.href)
            )?.label || "Lotec"}
          </h2>
        </header>
        <main className="flex-1 p-4 md:p-6 overflow-auto">{children}</main>
      </div>
    </div>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <AppContent>{children}</AppContent>;
}
