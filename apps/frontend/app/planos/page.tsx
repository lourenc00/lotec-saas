"use client";

import { useEffect, useState } from "react";
import { plans as plansApi } from "@/lib/api";
import Link from "next/link";

export default function PlansPage() {
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    plansApi
      .list()
      .then((data) => setPlans(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900">Planos</h1>
          <p className="text-gray-500 mt-2">Escolha o plano ideal para sua assistência técnica</p>
        </div>

        {loading ? (
          <div className="text-center text-gray-500">Carregando planos...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className={`bg-white rounded-2xl shadow-md p-8 border-2 transition-all hover:shadow-lg ${
                  plan.code === "professional"
                    ? "border-blue-500 scale-105"
                    : "border-transparent"
                }`}
              >
                {plan.code === "professional" && (
                  <div className="bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-full inline-block mb-4">
                    MAIS POPULAR
                  </div>
                )}
                <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                <p className="text-gray-500 text-sm mt-1">{plan.description}</p>
                <div className="mt-4 mb-6">
                  <span className="text-3xl font-bold text-gray-900">
                    R$ {plan.price_monthly.toFixed(2).replace(".", ",")}
                  </span>
                  <span className="text-gray-500 text-sm">/mês</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features?.map((f: any) => (
                    <li key={f.code} className="flex items-center text-sm">
                      {f.value_type === "boolean" ? (
                        f.bool_value ? (
                          <span className="text-green-500 mr-2">✓</span>
                        ) : (
                          <span className="text-gray-300 mr-2">✗</span>
                        )
                      ) : (
                        <span className="text-blue-500 mr-2">•</span>
                      )}
                      <span className={f.value_type === "boolean" && !f.bool_value ? "text-gray-400" : ""}>
                        {f.name}
                        {f.value_type === "integer" && f.int_value ? `: ${f.int_value}` : ""}
                      </span>
                    </li>
                  ))}
                </ul>
                <Link
                  href="/cadastro"
                  className={`block w-full text-center py-3 rounded-lg font-medium transition-colors ${
                    plan.code === "professional"
                      ? "bg-blue-600 text-white hover:bg-blue-700"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  Começar Agora
                </Link>
              </div>
            ))}
          </div>
        )}

        <div className="text-center mt-12">
          <Link href="/login" className="text-blue-600 hover:underline">
            Já tem conta? Entrar
          </Link>
        </div>
      </div>
    </div>
  );
}
