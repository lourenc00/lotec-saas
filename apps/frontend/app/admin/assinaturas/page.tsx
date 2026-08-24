"use client";

import { useEffect, useState } from "react";
import { admin as adminApi } from "@/lib/api";

export default function AdminSubscriptionsPage() {
  const [subs, setSubs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.subscriptions()
      .then((data) => setSubs(data.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const statusColors: Record<string, string> = {
    ACTIVE: "bg-green-100 text-green-800", TRIAL: "bg-blue-100 text-blue-800",
    PAST_DUE: "bg-yellow-100 text-yellow-800", SUSPENDED: "bg-red-100 text-red-800",
    CANCELED: "bg-gray-100 text-gray-800", PENDING: "bg-orange-100 text-orange-800",
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Assinaturas</h1>
      {loading ? (
        <div className="text-gray-500">Carregando...</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-left text-gray-600">
                <th className="p-3">Empresa</th>
                <th className="p-3">Plano</th>
                <th className="p-3">Status</th>
                <th className="p-3">Criada em</th>
                <th className="p-3">Trial até</th>
                <th className="p-3">Próx. Cobrança</th>
              </tr>
            </thead>
            <tbody>
              {subs.map((s) => (
                <tr key={s.id} className="border-t">
                  <td className="p-3 font-medium">{s.company_name}</td>
                  <td className="p-3">{s.plan_name}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[s.status] || ""}`}>
                      {s.status}
                    </span>
                  </td>
                  <td className="p-3 text-gray-500">{new Date(s.created_at).toLocaleDateString("pt-BR")}</td>
                  <td className="p-3 text-gray-500">{s.trial_ends_at ? new Date(s.trial_ends_at).toLocaleDateString("pt-BR") : "-"}</td>
                  <td className="p-3 text-gray-500">{s.next_billing_date ? new Date(s.next_billing_date).toLocaleDateString("pt-BR") : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
