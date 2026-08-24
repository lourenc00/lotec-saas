"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import Link from "next/link";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Erro ao fazer login");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Lotec</h1>
          <p className="text-gray-500 mt-1">Gestão de Assistências Técnicas</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-xl font-semibold mb-6">Entrar</h2>
          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-3 rounded mb-4 text-sm">
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                E-mail
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="seu@email.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Senha
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 font-medium"
            >
              {loading ? "Entrando..." : "Entrar"}
            </button>
          </form>
          <div className="mt-6 text-center text-sm text-gray-500 space-y-2">
            <div>
              Não tem conta?{" "}
              <Link href="/cadastro" className="text-blue-600 hover:underline">
                Cadastre-se
              </Link>
            </div>
            <div>
              <Link href="/planos" className="text-blue-600 hover:underline">
                Ver Planos
              </Link>
              {" · "}
              <Link href="/acompanhar" className="text-blue-600 hover:underline">
                Acompanhar OS
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
