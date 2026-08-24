"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { serviceOrders } from "@/lib/api";
import Link from "next/link";

const VALID_TRANSITIONS: Record<string, string[]> = {
  RECEIVED: ["IN_ANALYSIS", "CANCELED"],
  IN_ANALYSIS: ["WAITING_APPROVAL", "IN_REPAIR", "CANCELED", "NO_REPAIR"],
  WAITING_APPROVAL: ["IN_REPAIR", "CANCELED", "NO_REPAIR"],
  WAITING_PART: ["IN_REPAIR", "CANCELED"],
  IN_REPAIR: ["READY", "WAITING_PART", "CANCELED"],
  READY: ["DELIVERED", "IN_REPAIR"],
  DELIVERED: [],
  CANCELED: [],
  NO_REPAIR: [],
};

const STATUS_LABELS: Record<string, string> = {
  RECEIVED: "Recebido", IN_ANALYSIS: "Em Análise", WAITING_APPROVAL: "Aguard. Aprovação",
  WAITING_PART: "Aguard. Peça", IN_REPAIR: "Em Reparo", READY: "Pronto",
  DELIVERED: "Entregue", CANCELED: "Cancelado", NO_REPAIR: "Sem Reparo",
};

const STATUS_COLORS: Record<string, string> = {
  RECEIVED: "bg-blue-100 text-blue-800", IN_ANALYSIS: "bg-yellow-100 text-yellow-800",
  WAITING_APPROVAL: "bg-orange-100 text-orange-800", WAITING_PART: "bg-purple-100 text-purple-800",
  IN_REPAIR: "bg-indigo-100 text-indigo-800", READY: "bg-green-100 text-green-800",
  DELIVERED: "bg-gray-100 text-gray-800", CANCELED: "bg-red-100 text-red-800",
  NO_REPAIR: "bg-red-100 text-red-700",
};

type Tab = "resumo" | "servicos" | "pecas" | "historico";

export default function ServiceOrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [order, setOrder] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [servicesList, setServicesList] = useState<any[]>([]);
  const [partsList, setPartsList] = useState<any[]>([]);
  const [tab, setTab] = useState<Tab>("resumo");
  const [loading, setLoading] = useState(true);
  const [statusNotes, setStatusNotes] = useState("");
  const [showStatusForm, setShowStatusForm] = useState(false);

  const loadOrder = () => {
    return Promise.all([
      serviceOrders.get(id),
      serviceOrders.history(id),
      serviceOrders.listServices(id),
      serviceOrders.listParts(id),
    ]).then(([o, h, s, p]) => {
      setOrder(o);
      setHistory(h);
      setServicesList(s);
      setPartsList(p);
    });
  };

  useEffect(() => {
    loadOrder()
      .catch(() => router.push("/dashboard/os"))
      .finally(() => setLoading(false));
  }, [id, router]);

  const handleStatusChange = async (newStatus: string) => {
    try {
      await serviceOrders.changeStatus(id, newStatus, statusNotes || undefined);
      setShowStatusForm(false);
      setStatusNotes("");
      await loadOrder();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleAddService = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const desc = (form.elements.namedItem("svc_desc") as HTMLInputElement).value;
    const qty = (form.elements.namedItem("svc_qty") as HTMLInputElement).value;
    const price = (form.elements.namedItem("svc_price") as HTMLInputElement).value;
    if (!desc) return;
    await serviceOrders.addService(id, { description: desc, quantity: parseFloat(qty) || 1, unit_price: parseFloat(price) || 0 });
    form.reset();
    await loadOrder();
  };

  const handleRemoveService = async (svcId: string) => {
    if (!confirm("Remover este serviço?")) return;
    await serviceOrders.removeService(id, svcId);
    await loadOrder();
  };

  const handleAddPart = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const desc = (form.elements.namedItem("part_desc") as HTMLInputElement).value;
    const qty = (form.elements.namedItem("part_qty") as HTMLInputElement).value;
    const price = (form.elements.namedItem("part_price") as HTMLInputElement).value;
    if (!desc) return;
    await serviceOrders.addPart(id, { description: desc, quantity: parseFloat(qty) || 1, unit_price: parseFloat(price) || 0 });
    form.reset();
    await loadOrder();
  };

  const handleRemovePart = async (partId: string) => {
    if (!confirm("Remover esta peça?")) return;
    await serviceOrders.removePart(id, partId);
    await loadOrder();
  };

  if (loading) return <div className="text-gray-500 py-8 text-center">Carregando...</div>;
  if (!order) return null;

  const allowed = VALID_TRANSITIONS[order.status] || [];
  const servicesTotal = servicesList.reduce((acc: number, s: any) => acc + Number(s.total_price || 0), 0);
  const partsTotal = partsList.reduce((acc: number, p: any) => acc + Number(p.total_price || 0), 0);
  const subtotal = servicesTotal + partsTotal;

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <Link href="/dashboard/os" className="text-blue-600 hover:underline text-sm">← Voltar</Link>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mt-2 gap-2">
          <div>
            <h1 className="text-2xl font-bold">OS #{order.os_number}</h1>
            <p className="text-sm text-gray-500">Criada em {new Date(order.created_at).toLocaleDateString("pt-BR")}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${STATUS_COLORS[order.status] || "bg-gray-100"}`}>
              {STATUS_LABELS[order.status] || order.status}
            </span>
            {allowed.length > 0 && (
              <button
                onClick={() => setShowStatusForm(!showStatusForm)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
              >
                Alterar Status
              </button>
            )}
          </div>
        </div>
      </div>

      {showStatusForm && (
        <div className="bg-white rounded-lg shadow p-4 mb-4">
          <h3 className="font-medium mb-3">Alterar para:</h3>
          <div className="flex flex-wrap gap-2 mb-3">
            {allowed.map((s) => (
              <button
                key={s}
                onClick={() => handleStatusChange(s)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium border hover:opacity-80 ${STATUS_COLORS[s] || "bg-gray-100"}`}
              >
                {STATUS_LABELS[s] || s}
              </button>
            ))}
          </div>
          <input
            type="text"
            value={statusNotes}
            onChange={(e) => setStatusNotes(e.target.value)}
            placeholder="Observação (opcional)"
            className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-4 mb-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div><span className="text-gray-500">Cliente:</span> {order.customer_id}</div>
          <div><span className="text-gray-500">Aparelho:</span> {order.device_id}</div>
          <div className="md:col-span-2"><span className="text-gray-500">Problema:</span> {order.problem_reported}</div>
          {order.estimated_value && <div><span className="text-gray-500">Valor Estimado:</span> R$ {Number(order.estimated_value).toFixed(2)}</div>}
          {order.diagnosis && <div className="md:col-span-2"><span className="text-gray-500">Diagnóstico:</span> {order.diagnosis}</div>}
        </div>
      </div>

      <div className="flex gap-1 border-b border-gray-200 mb-4">
        {(["resumo", "servicos", "pecas", "historico"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {t === "resumo" ? "Resumo" : t === "servicos" ? `Serviços (${servicesList.length})` : t === "pecas" ? `Peças (${partsList.length})` : `Histórico (${history.length})`}
          </button>
        ))}
      </div>

      {tab === "resumo" && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="space-y-3 text-sm">
            {order.service_requested && <div><span className="text-gray-500">Serviço Solicitado:</span> {order.service_requested}</div>}
            {order.service_performed_summary && <div><span className="text-gray-500">Serviço Realizado:</span> {order.service_performed_summary}</div>}
            {order.internal_notes && <div><span className="text-gray-500">Notas Internas:</span> {order.internal_notes}</div>}
            {order.customer_notes && <div><span className="text-gray-500">Notas para Cliente:</span> {order.customer_notes}</div>}
            {order.estimated_delivery_at && <div><span className="text-gray-500">Previsão de Entrega:</span> {new Date(order.estimated_delivery_at).toLocaleDateString("pt-BR")}</div>}
            {order.completion_at && <div><span className="text-gray-500">Concluído em:</span> {new Date(order.completion_at).toLocaleDateString("pt-BR")}</div>}
            {order.delivery_at && <div><span className="text-gray-500">Entregue em:</span> {new Date(order.delivery_at).toLocaleDateString("pt-BR")}</div>}
          </div>
        </div>
      )}

      {tab === "servicos" && (
        <div className="bg-white rounded-lg shadow p-6">
          {servicesList.length > 0 && (
            <div className="mb-4 divide-y divide-gray-100">
              {servicesList.map((s: any) => (
                <div key={s.id} className="flex items-center justify-between py-2">
                  <div>
                    <span className="text-sm">{s.description}</span>
                    <span className="text-xs text-gray-500 ml-2">
                      {s.quantity}x R$ {Number(s.unit_price).toFixed(2)}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium">R$ {Number(s.total_price).toFixed(2)}</span>
                    <button onClick={() => handleRemoveService(s.id)} className="text-red-500 hover:text-red-700 text-xs">Remover</button>
                  </div>
                </div>
              ))}
            </div>
          )}
          <form onSubmit={handleAddService} className="flex gap-2 items-end">
            <input name="svc_desc" placeholder="Descrição do serviço" required className="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <input name="svc_qty" type="number" placeholder="Qtd" defaultValue="1" className="w-20 px-3 py-2 border rounded-md text-sm" />
            <input name="svc_price" type="number" step="0.01" placeholder="Preço" className="w-28 px-3 py-2 border rounded-md text-sm" />
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700">Adicionar</button>
          </form>
        </div>
      )}

      {tab === "pecas" && (
        <div className="bg-white rounded-lg shadow p-6">
          {partsList.length > 0 && (
            <div className="mb-4 divide-y divide-gray-100">
              {partsList.map((p: any) => (
                <div key={p.id} className="flex items-center justify-between py-2">
                  <div>
                    <span className="text-sm">{p.description}</span>
                    <span className="text-xs text-gray-500 ml-2">
                      {p.quantity}x R$ {Number(p.unit_price).toFixed(2)}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium">R$ {Number(p.total_price).toFixed(2)}</span>
                    <button onClick={() => handleRemovePart(p.id)} className="text-red-500 hover:text-red-700 text-xs">Remover</button>
                  </div>
                </div>
              ))}
            </div>
          )}
          <form onSubmit={handleAddPart} className="flex gap-2 items-end">
            <input name="part_desc" placeholder="Descrição da peça" required className="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <input name="part_qty" type="number" placeholder="Qtd" defaultValue="1" className="w-20 px-3 py-2 border rounded-md text-sm" />
            <input name="part_price" type="number" step="0.01" placeholder="Preço" className="w-28 px-3 py-2 border rounded-md text-sm" />
            <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700">Adicionar</button>
          </form>
        </div>
      )}

      {tab === "historico" && (
        <div className="bg-white rounded-lg shadow p-6">
          {history.length === 0 ? (
            <div className="text-gray-400 text-center text-sm">Nenhum registro</div>
          ) : (
            <div className="space-y-3">
              {[...history].reverse().map((h: any) => (
                <div key={h.id} className="border-l-4 border-gray-200 pl-4 py-1">
                  <div className="flex items-center gap-2">
                    {h.previous_status && (
                      <>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[h.previous_status] || "bg-gray-100"}`}>
                          {STATUS_LABELS[h.previous_status] || h.previous_status}
                        </span>
                        <span className="text-gray-400">→</span>
                      </>
                    )}
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[h.new_status] || "bg-gray-100"}`}>
                      {STATUS_LABELS[h.new_status] || h.new_status}
                    </span>
                  </div>
                  {h.notes && <p className="text-xs text-gray-500 mt-1">{h.notes}</p>}
                  <p className="text-xs text-gray-400 mt-0.5">
                    {new Date(h.created_at).toLocaleString("pt-BR")}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {(servicesTotal > 0 || partsTotal > 0) && (
        <div className="bg-white rounded-lg shadow p-4 mt-4">
          <div className="text-sm space-y-1">
            {servicesTotal > 0 && <div className="flex justify-between"><span className="text-gray-500">Serviços:</span><span>R$ {servicesTotal.toFixed(2)}</span></div>}
            {partsTotal > 0 && <div className="flex justify-between"><span className="text-gray-500">Peças:</span><span>R$ {partsTotal.toFixed(2)}</span></div>}
            <div className="flex justify-between font-semibold border-t pt-1">
              <span>Subtotal:</span>
              <span>R$ {subtotal.toFixed(2)}</span>
            </div>
            {order.discount > 0 && <div className="flex justify-between text-red-600"><span>Desconto:</span><span>- R$ {Number(order.discount).toFixed(2)}</span></div>}
          </div>
        </div>
      )}
    </div>
  );
}
