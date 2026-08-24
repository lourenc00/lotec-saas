"use client";

import { useEffect, useState } from "react";
import { admin as adminApi } from "@/lib/api";

export default function AdminCompaniesPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const load = (p: number) => {
    setLoading(true);
    adminApi.companies({ page: p, limit: 20 })
      .then((data) => {
        setCompanies(data.items || []);
        setTotalPages(data.pages || 1);
        setPage(p);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(1); }, []);

  const handleStatus = async (id: string, action: "activate" | "suspend") => {
    const reason = action === "suspend" ? prompt("Motivo da suspensão:") : undefined;
    if (action === "suspend" && !reason) return;
    await adminApi.updateStatus(id, { status: action === "activate" ? "ACTIVE" : "SUSPENDED", reason: reason ?? undefined });
    load(page);
  };

  const statusColors: Record<string, string> = {
    ACTIVE: "bg-green-100 text-green-800", SUSPENDED: "bg-red-100 text-red-800", PENDING: "bg-yellow-100 text-yellow-800",
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Empresas</h1>

      {loading ? (
        <div className="text-gray-500">Carregando...</div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left text-gray-600">
                  <th className="p-3">Nome</th>
                  <th className="p-3">Plano</th>
                  <th className="p-3">OS</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Criada em</th>
                  <th className="p-3">Ações</th>
                </tr>
              </thead>
              <tbody>
                {companies.map((c) => (
                  <tr key={c.id} className="border-t">
                    <td className="p-3 font-medium">{c.name}</td>
                    <td className="p-3">{c.plan}</td>
                    <td className="p-3">{c.os_count}</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[c.status] || ""}`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="p-3 text-gray-500">{new Date(c.created_at).toLocaleDateString("pt-BR")}</td>
                    <td className="p-3">
                      {c.status === "ACTIVE" ? (
                        <button onClick={() => handleStatus(c.id, "suspend")} className="text-red-600 hover:underline text-xs">Suspender</button>
                      ) : (
                        <button onClick={() => handleStatus(c.id, "activate")} className="text-green-600 hover:underline text-xs">Ativar</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex justify-center gap-2 mt-4">
            <button disabled={page <= 1} onClick={() => load(page - 1)} className="px-3 py-1 rounded border text-sm disabled:opacity-50">Anterior</button>
            <span className="px-3 py-1 text-sm text-gray-600">Página {page} de {totalPages}</span>
            <button disabled={page >= totalPages} onClick={() => load(page + 1)} className="px-3 py-1 rounded border text-sm disabled:opacity-50">Próxima</button>
          </div>
        </>
      )}
    </div>
  );
}
