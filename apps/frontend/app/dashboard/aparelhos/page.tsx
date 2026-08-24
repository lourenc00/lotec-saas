"use client";

import { useEffect, useState } from "react";
import { devices } from "@/lib/api";
import Link from "next/link";

export default function DevicesPage() {
  const [items, setItems] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const load = (q?: string) => {
    setLoading(true);
    devices
      .list({ q, page_size: 50 })
      .then((data) => setItems(Array.isArray(data) ? data : []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    load(search);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Aparelhos</h1>
        <Link href="/dashboard/aparelhos/novo" className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700">
          + Novo Aparelho
        </Link>
      </div>

      <form onSubmit={handleSearch} className="mb-4 flex gap-2">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar por modelo, marca ou IMEI..."
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button type="submit" className="bg-gray-100 px-4 py-2 rounded-md hover:bg-gray-200 text-sm">Buscar</button>
      </form>

      {loading ? (
        <div className="text-gray-500 py-8 text-center">Carregando...</div>
      ) : items.length === 0 ? (
        <div className="text-gray-400 py-8 text-center bg-white rounded-lg shadow">Nenhum aparelho encontrado</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Marca/Modelo</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600 hidden md:table-cell">Categoria</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600 hidden md:table-cell">IMEI</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {items.map((d: any) => (
                <tr key={d.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className="font-medium">{d.brand} {d.model}</span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600 hidden md:table-cell">{d.category}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 hidden md:table-cell font-mono">{d.imei || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
