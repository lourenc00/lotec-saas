"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { serviceOrders, customers, devices } from "@/lib/api";
import Link from "next/link";

export default function NewServiceOrderPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const presetCustomerId = searchParams.get("customer_id") || "";

  const [customersList, setCustomersList] = useState<any[]>([]);
  const [devicesList, setDevicesList] = useState<any[]>([]);
  const [customerId, setCustomerId] = useState(presetCustomerId);
  const [form, setForm] = useState({
    device_id: "",
    problem_reported: "",
    service_requested: "",
    estimated_delivery_at: "",
    estimated_value: "",
  });
  const [services, setServices] = useState([{ description: "", quantity: "1", unit_price: "" }]);
  const [parts, setParts] = useState([{ description: "", quantity: "1", unit_price: "" }]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    customers.list({ page_size: 100 }).then((data) => {
      setCustomersList(Array.isArray(data) ? data : []);
    });
  }, []);

  useEffect(() => {
    if (customerId) {
      customers.devices(customerId).then((data) => {
        setDevicesList(Array.isArray(data) ? data : []);
        setForm((f) => ({ ...f, device_id: "" }));
      });
    } else {
      setDevicesList([]);
    }
  }, [customerId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data: any = {
        customer_id: customerId,
        device_id: form.device_id,
        problem_reported: form.problem_reported,
      };
      if (form.service_requested) data.service_requested = form.service_requested;
      if (form.estimated_delivery_at) data.estimated_delivery_at = new Date(form.estimated_delivery_at).toISOString();
      if (form.estimated_value) data.estimated_value = parseFloat(form.estimated_value);

      data.services = services
        .filter((s) => s.description)
        .map((s) => ({
          description: s.description,
          quantity: parseFloat(s.quantity) || 1,
          unit_price: parseFloat(s.unit_price) || 0,
        }));

      data.parts = parts
        .filter((p) => p.description)
        .map((p) => ({
          description: p.description,
          quantity: parseFloat(p.quantity) || 1,
          unit_price: parseFloat(p.unit_price) || 0,
        }));

      const created = await serviceOrders.create(data);
      router.push(`/dashboard/os/${created.id}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addService = () => setServices([...services, { description: "", quantity: "1", unit_price: "" }]);
  const removeService = (i: number) => setServices(services.filter((_, idx) => idx !== i));
  const updateService = (i: number, field: string, value: string) => {
    const next = [...services];
    (next[i] as any)[field] = value;
    setServices(next);
  };

  const addPart = () => setParts([...parts, { description: "", quantity: "1", unit_price: "" }]);
  const removePart = (i: number) => setParts(parts.filter((_, idx) => idx !== i));
  const updatePart = (i: number, field: string, value: string) => {
    const next = [...parts];
    (next[i] as any)[field] = value;
    setParts(next);
  };

  return (
    <div className="max-w-3xl">
      <div className="mb-6">
        <Link href="/dashboard/os" className="text-blue-600 hover:underline text-sm">← Voltar</Link>
        <h1 className="text-2xl font-bold mt-2">Nova Ordem de Serviço</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && <div className="bg-red-50 text-red-700 px-4 py-3 rounded text-sm">{error}</div>}

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">Dados do Atendimento</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Cliente *</label>
              <select value={customerId} onChange={(e) => setCustomerId(e.target.value)} required className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">Selecione</option>
                {customersList.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Aparelho *</label>
              <select value={form.device_id} onChange={(e) => setForm({ ...form, device_id: e.target.value })} required disabled={!customerId} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50">
                <option value="">Selecione</option>
                {devicesList.map((d: any) => <option key={d.id} value={d.id}>{d.brand} {d.model}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Data Prevista</label>
              <input type="date" value={form.estimated_delivery_at} onChange={(e) => setForm({ ...form, estimated_delivery_at: e.target.value })} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Valor Estimado (R$)</label>
              <input type="number" step="0.01" value={form.estimated_value} onChange={(e) => setForm({ ...form, estimated_value: e.target.value })} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Problema Relatado *</label>
            <textarea value={form.problem_reported} onChange={(e) => setForm({ ...form, problem_reported: e.target.value })} required rows={3} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Serviço Solicitado</label>
            <textarea value={form.service_requested} onChange={(e) => setForm({ ...form, service_requested: e.target.value })} rows={2} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Serviços</h2>
            <button type="button" onClick={addService} className="text-blue-600 text-sm hover:underline">+ Adicionar</button>
          </div>
          {services.map((s, i) => (
            <div key={i} className="flex gap-2 mb-2 items-end">
              <input placeholder="Descrição" value={s.description} onChange={(e) => updateService(i, "description", e.target.value)} className="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              <input placeholder="Qtd" type="number" value={s.quantity} onChange={(e) => updateService(i, "quantity", e.target.value)} className="w-20 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              <input placeholder="Preço" type="number" step="0.01" value={s.unit_price} onChange={(e) => updateService(i, "unit_price", e.target.value)} className="w-28 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              {services.length > 1 && <button type="button" onClick={() => removeService(i)} className="text-red-500 hover:text-red-700 px-2">×</button>}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Peças</h2>
            <button type="button" onClick={addPart} className="text-blue-600 text-sm hover:underline">+ Adicionar</button>
          </div>
          {parts.map((p, i) => (
            <div key={i} className="flex gap-2 mb-2 items-end">
              <input placeholder="Descrição" value={p.description} onChange={(e) => updatePart(i, "description", e.target.value)} className="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              <input placeholder="Qtd" type="number" value={p.quantity} onChange={(e) => updatePart(i, "quantity", e.target.value)} className="w-20 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              <input placeholder="Preço" type="number" step="0.01" value={p.unit_price} onChange={(e) => updatePart(i, "unit_price", e.target.value)} className="w-28 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              {parts.length > 1 && <button type="button" onClick={() => removePart(i)} className="text-red-500 hover:text-red-700 px-2">×</button>}
            </div>
          ))}
        </div>

        <button type="submit" disabled={loading} className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 font-medium">
          {loading ? "Criando..." : "Criar Ordem de Serviço"}
        </button>
      </form>
    </div>
  );
}
