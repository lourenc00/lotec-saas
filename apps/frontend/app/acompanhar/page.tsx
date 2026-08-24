"use client";

import { useState } from "react";
import { portal } from "@/lib/api";
import Link from "next/link";

export default function TrackPage() {
  const [code, setCode] = useState("");
  const [order, setOrder] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim()) return;
    setLoading(true);
    setError("");
    setOrder(null);
    try {
      const data = await portal.track(code.trim());
      setOrder(data);
    } catch (err: any) {
      setError(err.message || "Código não encontrado");
    } finally {
      setLoading(false);
    }
  };

  const statusLabels: Record<string, string> = {
    RECEIVED: "Recebido", IN_ANALYSIS: "Em Análise", WAITING_APPROVAL: "Aguard. Aprovação",
    WAITING_PART: "Aguard. Peça", IN_REPAIR: "Em Reparo", READY: "Pronto para Retirada",
    DELIVERED: "Entregue", CANCELED: "Cancelado", NO_REPAIR: "Sem Reparo",
  };

  const statusIcons: Record<string, string> = {
    RECEIVED: "📥", IN_ANALYSIS: "🔍", WAITING_APPROVAL: "⏳",
    WAITING_PART: "📦", IN_REPAIR: "🔧", READY: "✅",
    DELIVERED: "🏠", CANCELED: "❌", NO_REPAIR: "🚫",
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Acompanhar OS</h1>
          <p className="text-gray-500 mt-2">Digite o código de acompanhamento da sua ordem de serviço</p>
        </div>

        <form onSubmit={handleSearch} className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex gap-3">
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Ex: ABC-12345 ou LoTec-001"
              className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Buscando..." : "Buscar"}
            </button>
          </div>
        </form>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {order && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-semibold text-lg">OS #{order.os_number || order.id?.slice(0, 8)}</h2>
                <p className="text-sm text-gray-500">
                  {order.device_info || "Aparelho"} — {order.customer_name}
                </p>
              </div>
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                {statusIcons[order.status] || ""} {statusLabels[order.status] || order.status}
              </span>
            </div>

            {order.technician_name && (
              <p className="text-sm text-gray-600 mb-4">
                <span className="font-medium">Técnico:</span> {order.technician_name}
              </p>
            )}

            {order.status === "WAITING_APPROVAL" && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <p className="text-yellow-800 text-sm">
                  ⏳ Aguardando sua aprovação para prosseguir com o reparo.
                </p>
              </div>
            )}

            {order.status === "READY" && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <p className="text-green-800 text-sm">
                  ✅ Seu aparelho está pronto para retirada!
                </p>
              </div>
            )}

            {order.description && (
              <div className="mt-4 pt-4 border-t">
                <h3 className="text-sm font-medium text-gray-700 mb-1">Observações</h3>
                <p className="text-sm text-gray-600">{order.description}</p>
              </div>
            )}
          </div>
        )}

        <div className="text-center mt-8">
          <Link href="/login" className="text-blue-600 hover:underline text-sm">
            Acessar sistema
          </Link>
        </div>
      </div>
    </div>
  );
}
