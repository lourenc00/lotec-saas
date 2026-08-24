"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { customers } from "@/lib/api";
import Link from "next/link";

export default function CustomerDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [customer, setCustomer] = useState<any>(null);
  const [devicesList, setDevicesList] = useState<any[]>([]);
  const [ordersList, setOrdersList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<any>({});
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      customers.get(id),
      customers.devices(id),
      customers.serviceOrders(id),
    ])
      .then(([c, d, o]) => {
        setCustomer(c);
        setForm(c);
        setDevicesList(d);
        setOrdersList(o);
      })
      .catch(() => router.push("/dashboard/clientes"))
      .finally(() => setLoading(false));
  }, [id, router]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await customers.update(id, {
        name: form.name,
        document: form.document || null,
        phone: form.phone || null,
        whatsapp: form.whatsapp || null,
        email: form.email || null,
        notes: form.notes || null,
      });
      setEditing(false);
      setCustomer({ ...customer, ...form });
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Tem certeza que deseja remover este cliente?")) return;
    try {
      await customers.remove(id);
      router.push("/dashboard/clientes");
    } catch (err: any) {
      alert(err.message);
    }
  };

  const statusLabels: Record<string, string> = {
    RECEIVED: "Recebido", IN_ANALYSIS: "Em Análise", WAITING_APPROVAL: "Aguard. Aprovação",
    WAITING_PART: "Aguard. Peça", IN_REPAIR: "Em Reparo", READY: "Pronto",
    DELIVERED: "Entregue", CANCELED: "Cancelado", NO_REPAIR: "Sem Reparo",
  };

  if (loading) return <div className="text-gray-500 py-8 text-center">Carregando...</div>;
  if (!customer) return null;

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <Link href="/dashboard/clientes" className="text-blue-600 hover:underline text-sm">
          ← Voltar
        </Link>
        <div className="flex items-center justify-between mt-2">
          <h1 className="text-2xl font-bold">{customer.name}</h1>
          <div className="flex gap-2">
            {!editing && (
              <button
                onClick={() => setEditing(true)}
                className="bg-gray-100 px-4 py-2 rounded-md text-sm hover:bg-gray-200"
              >
                Editar
              </button>
            )}
            <button
              onClick={handleDelete}
              className="bg-red-50 text-red-600 px-4 py-2 rounded-md text-sm hover:bg-red-100"
            >
              Remover
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        {editing ? (
          <form onSubmit={handleSave} className="space-y-4">
            {error && (
              <div className="bg-red-50 text-red-700 px-4 py-3 rounded text-sm">{error}</div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
                <input type="text" value={form.name || ""} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
                <input type="text" value={form.phone || ""} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
                <input type="email" value={form.email || ""} onChange={(e) => setForm({ ...form, email: e.target.value })} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">CPF/CNPJ</label>
                <input type="text" value={form.document || ""} onChange={(e) => setForm({ ...form, document: e.target.value })} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
            <div className="flex gap-2">
              <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700">Salvar</button>
              <button type="button" onClick={() => { setEditing(false); setForm(customer); }} className="bg-gray-100 px-4 py-2 rounded-md text-sm hover:bg-gray-200">Cancelar</button>
            </div>
          </form>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div><span className="text-gray-500">Telefone:</span> {customer.phone || "-"}</div>
            <div><span className="text-gray-500">WhatsApp:</span> {customer.whatsapp || "-"}</div>
            <div><span className="text-gray-500">E-mail:</span> {customer.email || "-"}</div>
            <div><span className="text-gray-500">CPF/CNPJ:</span> {customer.document || "-"}</div>
            <div className="md:col-span-2"><span className="text-gray-500">Observações:</span> {customer.notes || "-"}</div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b flex items-center justify-between">
            <h2 className="font-semibold">Aparelhos</h2>
            <Link href={`/dashboard/aparelhos/novo?customer_id=${id}`} className="text-blue-600 text-sm hover:underline">
              + Novo
            </Link>
          </div>
          {devicesList.length === 0 ? (
            <div className="p-6 text-gray-400 text-center text-sm">Nenhum aparelho</div>
          ) : (
            <div className="divide-y divide-gray-100">
              {devicesList.map((d: any) => (
                <div key={d.id} className="px-6 py-3">
                  <div className="font-medium text-sm">{d.brand} {d.model}</div>
                  <div className="text-xs text-gray-500">{d.category} {d.imei ? `• IMEI: ${d.imei}` : ""}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b flex items-center justify-between">
            <h2 className="font-semibold">Ordens de Serviço</h2>
            <Link href={`/dashboard/os/nova?customer_id=${id}`} className="text-blue-600 text-sm hover:underline">
              + Nova OS
            </Link>
          </div>
          {ordersList.length === 0 ? (
            <div className="p-6 text-gray-400 text-center text-sm">Nenhuma OS</div>
          ) : (
            <div className="divide-y divide-gray-100">
              {ordersList.map((o: any) => (
                <Link key={o.id} href={`/dashboard/os/${o.id}`} className="block px-6 py-3 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm">OS #{o.os_number}</span>
                    <span className="text-xs text-gray-500">{statusLabels[o.status] || o.status}</span>
                  </div>
                  <div className="text-xs text-gray-600 mt-0.5 truncate">{o.problem_reported}</div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
