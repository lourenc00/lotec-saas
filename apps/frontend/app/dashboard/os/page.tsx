"use client";

import { useEffect, useState } from "react";
import { serviceOrders } from "@/lib/api";
import Link from "next/link";

const STATUS_OPTIONS = [
  { value: "", label: "Todos" },
  { value: "RECEIVED", label: "Recebido" },
  { value: "IN_ANALYSIS", label: "Em Análise" },
  { value: "WAITING_APPROVAL", label: "Aguard. Aprovação" },
  { value: "WAITING_PART", label: "Aguard. Peça" },
  { value: "IN_REPAIR", label: "Em Reparo" },
  { value: "READY", label: "Pronto" },
  { value: "DELIVERED", label: "Entregue" },
  { value: "CANCELED", label: "Cancelado" },
];

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

const statusLabels: Record<string, string> = {
  RECEIVED: "Recebido", IN_ANALYSIS: "Em Análise", WAITING_APPROVAL: "Aguard. Aprovação",
  WAITING_PART: "Aguard. Peça", IN_REPAIR: "Em Reparo", READY: "Pronto",
  DELIVERED: "Entregue", CANCELED: "Cancelado", NO_REPAIR: "Sem Reparo",
};

export default function ServiceOrdersPage() {
  const [data, setData] = useState<any>({ items: [], total: 0, pages: 0 });
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    serviceOrders
      .list({ page, page_size: 20, status: status || undefined, q: search || undefined })
      .then((d) => setData(d))
      .catch(() => setData({ items: [], total: 0, pages: 0 }))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [page, status]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Ordens de Serviço</h1>
        <Link href="/dashboard/os/nova" className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700">
          + Nova OS
        </Link>
      </div>

      <div className="flex flex-col md:flex-row gap-2 mb-4">
        <form onSubmit={handleSearch} className="flex gap-2 flex-1">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por cliente ou problema..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button type="submit" className="bg-gray-100 px-4 py-2 rounded-md hover:bg-gray-200 text-sm">Buscar</button>
        </form>
        <select
          value={status}
          onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="text-gray-500 py-8 text-center">Carregando...</div>
      ) : data.items.length === 0 ? (
        <div className="text-gray-400 py-8 text-center bg-white rounded-lg shadow">Nenhuma OS encontrada</div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="divide-y divide-gray-100">
              {data.items.map((o: any) => (
                <Link key={o.id} href={`/dashboard/os/${o.id}`} className="flex items-center justify-between px-6 py-4 hover:bg-gray-50">
                  <div>
                    <span className="font-mono text-sm text-gray-600">OS #{o.os_number}</span>
                    <p className="text-sm text-gray-900 mt-0.5">{o.problem_reported}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {new Date(o.created_at).toLocaleDateString("pt-BR")}
                      {o.estimated_value ? ` • R$ ${Number(o.estimated_value).toFixed(2)}` : ""}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap ${statusColors[o.status] || "bg-gray-100"}`}>
                    {statusLabels[o.status] || o.status}
                  </span>
                </Link>
              ))}
            </div>
          </div>
          {data.pages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-3 py-1 border rounded disabled:opacity-50 text-sm"
              >
                Anterior
              </button>
              <span className="text-sm text-gray-500">
                Página {page} de {data.pages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                disabled={page >= data.pages}
                className="px-3 py-1 border rounded disabled:opacity-50 text-sm"
              >
                Próxima
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
