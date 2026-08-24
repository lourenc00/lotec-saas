"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { customers } from "@/lib/api";
import Link from "next/link";

export default function NewCustomerPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    name: "",
    document: "",
    phone: "",
    whatsapp: "",
    email: "",
    notes: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data: any = { name: form.name };
      if (form.document) data.document = form.document;
      if (form.phone) data.phone = form.phone;
      if (form.whatsapp) data.whatsapp = form.whatsapp;
      if (form.email) data.email = form.email;
      if (form.notes) data.notes = form.notes;
      const created = await customers.create(data);
      router.push(`/dashboard/clientes/${created.id}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <Link href="/dashboard/clientes" className="text-blue-600 hover:underline text-sm">
          ← Voltar
        </Link>
        <h1 className="text-2xl font-bold mt-2">Novo Cliente</h1>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        {error && (
          <div className="bg-red-50 text-red-700 px-4 py-3 rounded mb-4 text-sm">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nome *
            </label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                CPF/CNPJ
              </label>
              <input
                type="text"
                value={form.document}
                onChange={(e) => setForm({ ...form, document: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Telefone
              </label>
              <input
                type="text"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                WhatsApp
              </label>
              <input
                type="text"
                value={form.whatsapp}
                onChange={(e) => setForm({ ...form, whatsapp: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                E-mail
              </label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Observações
            </label>
            <textarea
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Salvando..." : "Salvar"}
          </button>
        </form>
      </div>
    </div>
  );
}
