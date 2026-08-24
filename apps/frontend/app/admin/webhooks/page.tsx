"use client";

import { useEffect, useState } from "react";
import { admin as adminApi } from "@/lib/api";

export default function AdminWebhooksPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.webhookEvents()
      .then((data) => setEvents(data.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const statusColors: Record<string, string> = {
    RECEIVED: "bg-blue-100 text-blue-800", PROCESSING: "bg-yellow-100 text-yellow-800",
    PROCESSED: "bg-green-100 text-green-800", FAILED: "bg-red-100 text-red-800",
    IGNORED: "bg-gray-100 text-gray-800",
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Webhooks</h1>
      {loading ? (
        <div className="text-gray-500">Carregando...</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-left text-gray-600">
                <th className="p-3">Tipo</th>
                <th className="p-3">Ação</th>
                <th className="p-3">Status</th>
                <th className="p-3">Erro</th>
                <th className="p-3">Data</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id} className="border-t">
                  <td className="p-3">{e.event_type}</td>
                  <td className="p-3 text-gray-500">{e.action || "-"}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[e.processing_status] || ""}`}>
                      {e.processing_status}
                    </span>
                  </td>
                  <td className="p-3 text-red-600 text-xs max-w-[200px] truncate">{e.error_message || "-"}</td>
                  <td className="p-3 text-gray-500">{new Date(e.created_at).toLocaleString("pt-BR")}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {events.length === 0 && <p className="text-gray-400 text-center py-8">Nenhum evento registrado</p>}
        </div>
      )}
    </div>
  );
}
