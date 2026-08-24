"use client";

import { useEffect, useState } from "react";
import { plans as plansApi } from "@/lib/api";

export default function AdminPlansPage() {
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    plansApi.list()
      .then(setPlans)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-500">Carregando...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Planos</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <div key={plan.id} className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold">{plan.name}</h2>
            <p className="text-sm text-gray-500 mt-1">{plan.description}</p>
            <div className="text-2xl font-bold mt-4">R$ {plan.price_monthly.toFixed(2).replace(".", ",")}/mês</div>
            <div className="mt-4 space-y-1">
              {plan.features?.map((f: any) => (
                <div key={f.code} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">{f.name}</span>
                  <span className="font-medium">
                    {f.value_type === "boolean" ? (f.bool_value ? "✓" : "✗") : f.int_value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
