"use client";

import { useEffect, useState } from "react";
import { admin as adminApi } from "@/lib/api";

export default function AdminPaymentsPage() {
  const [payments, setPayments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.payments()
      .then((data) => setPayments(data.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const statusColors: Record<string, string> = {
    APPROVED: "bg-green-100 text-green-800", PENDING: "bg-yellow-100 text-yellow-800",
    REJECTED: "bg-red-100 text-red-800", REFUNDED: "bg-orange-100 text-orange-800",
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Pagamentos</h1>
      {loading ? (
        <div className="text-gray-500">Carregando...</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-left text-gray-600">
                <th className="p-3">Empresa</th>
                <th className="p-3">Valor</th>
                <th className="p-3">Status</th>
                <th className="p-3">Método</th>
                <th className="p-3">Data</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id} className="border-t">
                  <td className="p-3 font-medium">{p.company_name}</td>
                  <td className="p-3">R$ {p.amount?.toFixed(2) || "0.00"}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[p.status] || ""}`}>
                      {p.status}
                    </span>
                  </td>
                  <td className="p-3 text-gray-500">{p.payment_method || "-"}</td>
                  <td className="p-3 text-gray-500">{p.paid_at ? new Date(p.paid_at).toLocaleDateString("pt-BR") : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {payments.length === 0 && <p className="text-gray-400 text-center py-8">Nenhum pagamento registrado</p>}
        </div>
      )}
    </div>
  );
}
