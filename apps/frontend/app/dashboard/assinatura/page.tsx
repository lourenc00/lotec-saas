"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { subscription as subApi, plans as plansApi } from "@/lib/api";
import Link from "next/link";

export default function SubscriptionPage() {
  const { user } = useAuth();
  const [sub, setSub] = useState<any>(null);
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showPlans, setShowPlans] = useState(false);

  useEffect(() => {
    if (!user?.company_id) {
      setLoading(false);
      return;
    }
    Promise.all([subApi.get(), plansApi.list()])
      .then(([s, p]) => {
        setSub(s);
        setPlans(p);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user]);

  const handleCheckout = async (planId: string) => {
    try {
      const result = await subApi.checkout(planId);
      if (result?.checkout_url) {
        window.location.href = result.checkout_url;
      } else {
        window.location.reload();
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleChangePlan = async (planId: string) => {
    if (!confirm("Tem certeza que deseja alterar o plano?")) return;
    try {
      await subApi.changePlan(planId);
      window.location.reload();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleCancel = async () => {
    if (!confirm("Tem certeza que deseja cancelar a assinatura?")) return;
    try {
      await subApi.cancel();
      window.location.reload();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) return <div className="text-gray-500 py-8 text-center">Carregando...</div>;

  const statusLabels: Record<string, string> = {
    ACTIVE: "Ativa", TRIAL: "Período de Teste", PAST_DUE: "Em Atraso",
    SUSPENDED: "Suspensa", CANCELED: "Cancelada", PENDING: "Pendente",
  };

  const statusColors: Record<string, string> = {
    ACTIVE: "bg-green-100 text-green-800", TRIAL: "bg-blue-100 text-blue-800",
    PAST_DUE: "bg-yellow-100 text-yellow-800", SUSPENDED: "bg-red-100 text-red-800",
    CANCELED: "bg-gray-100 text-gray-800", PENDING: "bg-orange-100 text-orange-800",
  };

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <Link href="/dashboard" className="text-blue-600 hover:underline text-sm">← Voltar</Link>
        <h1 className="text-2xl font-bold mt-2">Assinatura</h1>
      </div>

      {sub && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-lg">Plano Atual</h2>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[sub.status] || "bg-gray-100"}`}>
              {statusLabels[sub.status] || sub.status}
            </span>
          </div>

          {sub.status === "SUSPENDED" && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <p className="text-yellow-800 text-sm">
                Sua assinatura precisa ser regularizada.{" "}
                <Link href="/planos" className="font-medium underline">Ver planos</Link>
              </p>
            </div>
          )}

          {sub.trial_ends_at && sub.status === "TRIAL" && (
            <p className="text-sm text-gray-600 mb-4">
              Período de teste até: {new Date(sub.trial_ends_at).toLocaleDateString("pt-BR")}
            </p>
          )}

          {sub.next_billing_date && (
            <p className="text-sm text-gray-600 mb-4">
              Próxima cobrança: {new Date(sub.next_billing_date).toLocaleDateString("pt-BR")}
            </p>
          )}

          <div className="flex gap-3 mt-4">
            <button
              onClick={() => setShowPlans(!showPlans)}
              className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
            >
              {showPlans ? "Fechar" : "Alterar Plano"}
            </button>
            {sub.status !== "CANCELED" && (
              <button
                onClick={handleCancel}
                className="bg-red-50 text-red-600 px-4 py-2 rounded-md text-sm hover:bg-red-100"
              >
                Cancelar Assinatura
              </button>
            )}
          </div>
        </div>
      )}

      {showPlans && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {plans.map((plan) => (
            <div key={plan.id} className={`bg-white rounded-lg shadow p-6 border-2 ${
              sub?.plan_id === plan.id ? "border-blue-500" : "border-transparent"
            }`}>
              <h3 className="font-semibold">{plan.name}</h3>
              <p className="text-2xl font-bold mt-2">R$ {plan.price_monthly.toFixed(2).replace(".", ",")}<span className="text-sm font-normal text-gray-500">/mês</span></p>
              {sub?.plan_id === plan.id ? (
                <div className="mt-4 text-sm text-blue-600 font-medium">Plano Atual</div>
              ) : (
                <button
                  onClick={() => handleChangePlan(plan.id)}
                  className="mt-4 w-full bg-blue-600 text-white py-2 rounded-md text-sm hover:bg-blue-700"
                >
                  Selecionar
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {!sub && !loading && (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <p className="text-gray-500 mb-4">Nenhuma assinatura ativa.</p>
          <Link href="/planos" className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700">
            Ver Planos
          </Link>
        </div>
      )}
    </div>
  );
}
