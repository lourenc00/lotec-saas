"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { serviceOrders, customers, devices, companies } from "@/lib/api";
import Link from "next/link";

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState({ orders: 0, customers: 0, devices: 0 });
  const [recentOrders, setRecentOrders] = useState<any[]>([]);
  const [needsCompany, setNeedsCompany] = useState(false);
  const [companyName, setCompanyName] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    if (!user.company_id) {
      setNeedsCompany(true);
      setLoading(false);
      return;
    }
    Promise.all([
      serviceOrders.list({ page_size: 5 }).catch(() => ({ items: [] })),
      customers.list({ page_size: 1 }).catch(() => []),
      devices.list({ page_size: 1 }).catch(() => []),
      companies.get().catch(() => null),
    ]).then(([ordersData, custs, devs, company]) => {
      setRecentOrders(ordersData.items || []);
      setStats({
        orders: ordersData.total || 0,
        customers: Array.isArray(custs) ? custs.length : 0,
        devices: Array.isArray(devs) ? devs.length : 0,
      });
      if (company) setCompanyName(company.name);
      setLoading(false);
    });
  }, [user]);

  const handleCreateCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    await companies.create({ name: companyName });
    setNeedsCompany(false);
    window.location.reload();
  };

  if (loading) {
    return <div className="text-gray-500">Carregando...</div>;
  }

  if (needsCompany) {
    return (
      <div className="max-w-md mx-auto mt-12">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Criar sua empresa</h2>
          <p className="text-gray-500 text-sm mb-4">
            Para começar, crie sua empresa.
          </p>
          <form onSubmit={handleCreateCompany} className="space-y-4">
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              required
              placeholder="Nome da empresa"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700"
            >
              Criar Empresa
            </button>
          </form>
        </div>
      </div>
    );
  }

  const statusLabels: Record<string, string> = {
    RECEIVED: "Recebido",
    IN_ANALYSIS: "Em Análise",
    WAITING_APPROVAL: "Aguardando Aprovação",
    WAITING_PART: "Aguardando Peça",
    IN_REPAIR: "Em Reparo",
    READY: "Pronto",
    DELIVERED: "Entregue",
    CANCELED: "Cancelado",
    NO_REPAIR: "Sem Reparo",
  };

  const statusColors: Record<string, string> = {
    RECEIVED: "bg-blue-100 text-blue-800",
    IN_ANALYSIS: "bg-yellow-100 text-yellow-800",
    WAITING_APPROVAL: "bg-orange-100 text-orange-800",
    WAITING_PART: "bg-purple-100 text-purple-800",
    IN_REPAIR: "bg-indigo-100 text-indigo-800",
    READY: "bg-green-100 text-green-800",
    DELIVERED: "bg-gray-100 text-gray-800",
    CANCELED: "bg-red-100 text-red-800",
    NO_REPAIR: "bg-red-100 text-red-700",
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Link href="/dashboard/os" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
          <div className="text-sm text-gray-500">Ordens de Serviço</div>
          <div className="text-3xl font-bold text-gray-900 mt-1">{stats.orders}</div>
        </Link>
        <Link href="/dashboard/clientes" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
          <div className="text-sm text-gray-500">Clientes</div>
          <div className="text-3xl font-bold text-gray-900 mt-1">{stats.customers}</div>
        </Link>
        <Link href="/dashboard/aparelhos" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
          <div className="text-sm text-gray-500">Aparelhos</div>
          <div className="text-3xl font-bold text-gray-900 mt-1">{stats.devices}</div>
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="font-semibold text-gray-800">OS Recentes</h2>
          <Link
            href="/dashboard/os/nova"
            className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
          >
            + Nova OS
          </Link>
        </div>
        {recentOrders.length === 0 ? (
          <div className="p-6 text-center text-gray-400">
            Nenhuma ordem de serviço ainda
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {recentOrders.map((order: any) => (
              <Link
                key={order.id}
                href={`/dashboard/os/${order.id}`}
                className="flex items-center justify-between px-6 py-4 hover:bg-gray-50"
              >
                <div>
                  <span className="font-mono text-sm text-gray-600">
                    OS #{order.os_number}
                  </span>
                  <p className="text-sm text-gray-900 mt-0.5">
                    {order.problem_reported}
                  </p>
                </div>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    statusColors[order.status] || "bg-gray-100"
                  }`}
                >
                  {statusLabels[order.status] || order.status}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
