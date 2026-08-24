"use client";

import { useEffect, useState } from "react";
import { admin as adminApi } from "@/lib/api";

export default function AdminDashboardPage() {
  const [dash, setDash] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.dashboard()
      .then(setDash)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-500">Carregando...</div>;
  if (!dash) return <div className="text-red-500">Erro ao carregar dashboard</div>;

  const cards = [
    { label: "Empresas Ativas", value: dash.active_companies, color: "blue" },
    { label: "Total Empresas", value: dash.total_companies, color: "gray" },
    { label: "Usuários", value: dash.total_users, color: "gray" },
    { label: "Ordens de Serviço", value: dash.total_os, color: "gray" },
    { label: "MRR", value: `R$ ${dash.mrr.toFixed(2)}`, color: "green" },
    { label: "Webhooks com Falha", value: dash.failed_webhooks, color: "red" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        {cards.map((c, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">{c.label}</div>
            <div className={`text-2xl font-bold ${c.color === "red" ? "text-red-600" : c.color === "green" ? "text-green-600" : ""}`}>{c.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="font-semibold mb-4">Assinaturas por Plano</h2>
        {Object.keys(dash.subscriptions_by_plan).length === 0 ? (
          <p className="text-gray-400 text-sm">Sem assinaturas</p>
        ) : (
          <div className="space-y-2">
            {Object.entries(dash.subscriptions_by_plan).map(([plan, count]: [string, any]) => (
              <div key={plan} className="flex items-center justify-between">
                <span className="text-sm">{plan}</span>
                <span className="font-medium">{count} empresa(s)</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
