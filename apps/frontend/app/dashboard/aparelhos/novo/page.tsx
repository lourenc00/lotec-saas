"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { devices, customers } from "@/lib/api";
import Link from "next/link";

const CATEGORIES = ["SMARTPHONE", "TABLET", "NOTEBOOK", "COMPUTER", "OTHER"];

export default function NewDevicePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const presetCustomerId = searchParams.get("customer_id") || "";
  const [customersList, setCustomersList] = useState<any[]>([]);
  const [form, setForm] = useState({
    customer_id: presetCustomerId,
    category: "SMARTPHONE",
    brand: "",
    model: "",
    color: "",
    imei: "",
    serial_number: "",
    physical_condition: "",
    notes: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    customers.list({ page_size: 100 }).then((data) => {
      setCustomersList(Array.isArray(data) ? data : []);
    });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data: any = {
        customer_id: form.customer_id,
        category: form.category,
        model: form.model,
      };
      if (form.brand) data.brand = form.brand;
      if (form.color) data.color = form.color;
      if (form.imei) data.imei = form.imei;
      if (form.serial_number) data.serial_number = form.serial_number;
      if (form.physical_condition) data.physical_condition = form.physical_condition;
      if (form.notes) data.notes = form.notes;
      await devices.create(data);
      router.push("/dashboard/aparelhos");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <div className="mb-6">
        <Link href="/dashboard/aparelhos" className="text-blue-600 hover:underline text-sm">← Voltar</Link>
        <h1 className="text-2xl font-bold mt-2">Novo Aparelho</h1>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        {error && <div className="bg-red-50 text-red-700 px-4 py-3 rounded mb-4 text-sm">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Cliente *</label>
            <select
              value={form.customer_id}
              onChange={(e) => setForm({ ...form, customer_id: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Selecione o cliente</option>
              {customersList.map((c: any) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Categoria *</label>
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Marca</label>
              <input type="text" value={form.brand} onChange={(e) => setForm({ ...form, brand: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Modelo *</label>
              <input type="text" value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })} required className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">IMEI</label>
              <input type="text" value={form.imei} onChange={(e) => setForm({ ...form, imei: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Cor</label>
              <input type="text" value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nº Série</label>
              <input type="text" value={form.serial_number} onChange={(e) => setForm({ ...form, serial_number: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Condição Física</label>
            <textarea value={form.physical_condition} onChange={(e) => setForm({ ...form, physical_condition: e.target.value })} rows={2} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <button type="submit" disabled={loading} className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50">
            {loading ? "Salvando..." : "Salvar"}
          </button>
        </form>
      </div>
    </div>
  );
}
