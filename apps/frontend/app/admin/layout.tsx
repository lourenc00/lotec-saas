"use client";

import { useAuth } from "@/lib/auth-context";
import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";

const ADMIN_ITEMS = [
  { href: "/admin", label: "Dashboard", icon: "📊" },
  { href: "/admin/empresas", label: "Empresas", icon: "🏢" },
  { href: "/admin/assinaturas", label: "Assinaturas", icon: "💳" },
  { href: "/admin/pagamentos", label: "Pagamentos", icon: "💰" },
  { href: "/admin/webhooks", label: "Webhooks", icon: "🔔" },
  { href: "/admin/planos", label: "Planos", icon: "📋" },
  { href: "/admin/configuracoes", label: "Configurações", icon: "⚙️" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && (!user || !user.is_super_admin)) {
      router.push("/dashboard");
    }
  }, [user, loading, router]);

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="text-gray-500">Carregando...</div></div>;
  if (!user?.is_super_admin) return null;

  return (
    <div className="min-h-screen flex bg-gray-50">
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-red-600">⚡ Super Admin</h1>
          <p className="text-xs text-gray-400 mt-1">Painel de Administração</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {ADMIN_ITEMS.map((item) => {
            const isActive = item.href === "/admin" ? pathname === "/admin" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive ? "bg-red-50 text-red-700" : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-3 border-t border-gray-200">
          <Link href="/dashboard" className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-100">
            ← Voltar ao App
          </Link>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <main className="flex-1 p-6 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
