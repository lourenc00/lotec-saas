"use client";

import { useEffect, useState } from "react";
import { dashboard, reports, serviceOrders, exportsApi } from "@/lib/api";
import Link from "next/link";

export default function ReportsPage() {
  const [summary, setSummary] = useState<any>(null);
  const [byStatus, setByStatus] = useState<any>({});
  const [topServices, setTopServices] = useState<any[]>([]);
  const [deviceModels, setDeviceModels] = useState<any[]>([]);
  const [serviceReport, setServiceReport] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      dashboard.summary(),
      dashboard.serviceOrders({ days: 30 }),
      dashboard.services({ days: 30 }),
      dashboard.deviceModels(),
      reports.serviceOrders(),
      reports.services(),
    ])
      .then(([s, os, svc, dm, repOs, repSvc]) => {
        setSummary(s);
        setByStatus(os);
        setTopServices(svc);
        setDeviceModels(dm);
        setServiceReport(repSvc);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const statusLabels: Record<string, string> = {
    RECEIVED: "Recebido", IN_ANALYSIS: "Em Análise", WAITING_APPROVAL: "Aguard. Aprovação",
    WAITING_PART: "Aguard. Peça", IN_REPAIR: "Em Reparo", READY: "Pronto",
    DELIVERED: "Entregue", CANCELED: "Cancelado", NO_REPAIR: "Sem Reparo",
  };

  if (loading) return <div className="text-gray-500 py-8 text-center">Carregando...</div>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Relatórios</h1>
        <div className="flex gap-2">
          <button
            onClick={() => exportsApi.customers().catch((e) => alert(e.message))}
            className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700"
          >
            📥 Exportar Clientes (CSV)
          </button>
          <button
            onClick={() => exportsApi.serviceOrders().catch((e) => alert(e.message))}
            className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700"
          >
            📥 Exportar OS (CSV)
          </button>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Total OS</div>
            <div className="text-2xl font-bold">{summary.total_os}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">OS este mês</div>
            <div className="text-2xl font-bold">{summary.month_os}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Clientes</div>
            <div className="text-2xl font-bold">{summary.total_customers}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">OS Abertas</div>
            <div className="text-2xl font-bold text-orange-600">{summary.open_os}</div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">OS por Status (30 dias)</h2>
          {Object.keys(byStatus).length === 0 ? (
            <p className="text-gray-400 text-sm">Sem dados</p>
          ) : (
            <div className="space-y-2">
              {Object.entries(byStatus).map(([status, count]: [string, any]) => (
                <div key={status} className="flex items-center justify-between">
                  <span className="text-sm">{statusLabels[status] || status}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-100 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${Math.min(100, (count / Math.max(...Object.values(byStatus) as number[])) * 100)}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium w-8 text-right">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">Receita por Serviço (30 dias)</h2>
          {topServices.length === 0 ? (
            <p className="text-gray-400 text-sm">Sem dados</p>
          ) : (
            <div className="space-y-2">
              {topServices.map((s: any, i: number) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="truncate flex-1">{s.description}</span>
                  <span className="font-medium ml-2">R$ {s.total_revenue.toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">Aparelhos Mais Atendidos</h2>
          {deviceModels.length === 0 ? (
            <p className="text-gray-400 text-sm">Sem dados</p>
          ) : (
            <div className="space-y-2">
              {deviceModels.map((d: any, i: number) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span>{d.brand} {d.model}</span>
                  <span className="text-gray-500">{d.count} aparelhos</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">Serviços (Geral)</h2>
          {serviceReport.length === 0 ? (
            <p className="text-gray-400 text-sm">Sem dados</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="pb-2">Serviço</th>
                    <th className="pb-2 text-right">Qtd</th>
                    <th className="pb-2 text-right">Receita</th>
                  </tr>
                </thead>
                <tbody>
                  {serviceReport.slice(0, 10).map((s: any, i: number) => (
                    <tr key={i} className="border-b border-gray-50">
                      <td className="py-2">{s.description}</td>
                      <td className="py-2 text-right">{s.total_qty}</td>
                      <td className="py-2 text-right">R$ {s.total_revenue.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
