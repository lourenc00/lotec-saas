const API_BASE = "/api/v1";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

function setToken(token: string) {
  localStorage.setItem("token", token);
}

function clearToken() {
  localStorage.removeItem("token");
}

export async function apiFetch(
  path: string,
  options: RequestInit = {},
): Promise<any> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearToken();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("Não autorizado");
  }

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || "Erro na requisição");
  }

  return data;
}

export const auth = {
  async login(email: string, password: string) {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setToken(data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    return data;
  },

  async register(name: string, email: string, password: string) {
    return apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    });
  },

  async me() {
    return apiFetch("/auth/me");
  },

  logout() {
    clearToken();
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
  },
};

export const companies = {
  async create(data: { name: string; legal_name?: string; document?: string; email?: string; phone?: string }) {
    return apiFetch("/company", { method: "POST", body: JSON.stringify(data) });
  },
  async get() {
    return apiFetch("/company");
  },
  async update(data: Record<string, any>) {
    return apiFetch("/company", { method: "PUT", body: JSON.stringify(data) });
  },
};

export const customers = {
  async list(params?: { page?: number; page_size?: number; q?: string }) {
    const qs = new URLSearchParams();
    if (params?.page) qs.set("page", String(params.page));
    if (params?.page_size) qs.set("page_size", String(params.page_size));
    if (params?.q) qs.set("q", params.q);
    const query = qs.toString();
    return apiFetch(`/customers${query ? "?" + query : ""}`);
  },
  async get(id: string) {
    return apiFetch(`/customers/${id}`);
  },
  async create(data: any) {
    return apiFetch("/customers", { method: "POST", body: JSON.stringify(data) });
  },
  async update(id: string, data: any) {
    return apiFetch(`/customers/${id}`, { method: "PUT", body: JSON.stringify(data) });
  },
  async remove(id: string) {
    return apiFetch(`/customers/${id}`, { method: "DELETE" });
  },
  async devices(id: string) {
    return apiFetch(`/customers/${id}/devices`);
  },
  async serviceOrders(id: string) {
    return apiFetch(`/customers/${id}/service-orders`);
  },
};

export const devices = {
  async list(params?: { page?: number; page_size?: number; q?: string }) {
    const qs = new URLSearchParams();
    if (params?.page) qs.set("page", String(params.page));
    if (params?.page_size) qs.set("page_size", String(params.page_size));
    if (params?.q) qs.set("q", params.q);
    const query = qs.toString();
    return apiFetch(`/devices${query ? "?" + query : ""}`);
  },
  async get(id: string) {
    return apiFetch(`/devices/${id}`);
  },
  async create(data: any) {
    return apiFetch("/devices", { method: "POST", body: JSON.stringify(data) });
  },
  async update(id: string, data: any) {
    return apiFetch(`/devices/${id}`, { method: "PUT", body: JSON.stringify(data) });
  },
  async remove(id: string) {
    return apiFetch(`/devices/${id}`, { method: "DELETE" });
  },
};

export const serviceOrders = {
  async list(params?: { page?: number; page_size?: number; status?: string; q?: string; customer_id?: string }) {
    const qs = new URLSearchParams();
    if (params?.page) qs.set("page", String(params.page));
    if (params?.page_size) qs.set("page_size", String(params.page_size));
    if (params?.status) qs.set("status", params.status);
    if (params?.q) qs.set("q", params.q);
    if (params?.customer_id) qs.set("customer_id", params.customer_id);
    const query = qs.toString();
    return apiFetch(`/service-orders${query ? "?" + query : ""}`);
  },
  async get(id: string) {
    return apiFetch(`/service-orders/${id}`);
  },
  async create(data: any) {
    return apiFetch("/service-orders", { method: "POST", body: JSON.stringify(data) });
  },
  async update(id: string, data: any) {
    return apiFetch(`/service-orders/${id}`, { method: "PUT", body: JSON.stringify(data) });
  },
  async changeStatus(id: string, status: string, notes?: string) {
    return apiFetch(`/service-orders/${id}/status`, {
      method: "POST",
      body: JSON.stringify({ status, notes }),
    });
  },
  async history(id: string) {
    return apiFetch(`/service-orders/${id}/history`);
  },
  async listServices(id: string) {
    return apiFetch(`/service-orders/${id}/services`);
  },
  async addService(id: string, data: any) {
    return apiFetch(`/service-orders/${id}/services`, { method: "POST", body: JSON.stringify(data) });
  },
  async removeService(orderId: string, serviceId: string) {
    return apiFetch(`/service-orders/${orderId}/services/${serviceId}`, { method: "DELETE" });
  },
  async listParts(id: string) {
    return apiFetch(`/service-orders/${id}/parts`);
  },
  async addPart(id: string, data: any) {
    return apiFetch(`/service-orders/${id}/parts`, { method: "POST", body: JSON.stringify(data) });
  },
  async removePart(orderId: string, partId: string) {
    return apiFetch(`/service-orders/${orderId}/parts/${partId}`, { method: "DELETE" });
  },
};

export const search = {
  async global(q: string) {
    return apiFetch(`/search?q=${encodeURIComponent(q)}`);
  },
};

export const plans = {
  async list() {
    return apiFetch("/plans");
  },
};

export const subscription = {
  async get() {
    return apiFetch("/subscription");
  },
  async checkout(planId: string) {
    return apiFetch("/subscription/checkout", {
      method: "POST",
      body: JSON.stringify({ plan_id: planId }),
    });
  },
  async changePlan(planId: string) {
    return apiFetch("/subscription/change-plan", {
      method: "POST",
      body: JSON.stringify({ plan_id: planId }),
    });
  },
  async cancel() {
    return apiFetch("/subscription/cancel", { method: "POST" });
  },
};

export const dashboard = {
  async summary() {
    return apiFetch("/dashboard/summary");
  },
  async serviceOrders(params?: { days?: number }) {
    const qs = params?.days ? `?days=${params.days}` : "";
    return apiFetch(`/dashboard/service-orders/status${qs}`);
  },
  async services(params?: { days?: number }) {
    const qs = params?.days ? `?days=${params.days}` : "";
    return apiFetch(`/dashboard/services/top${qs}`);
  },
  async technicians(params?: { days?: number }) {
    const qs = params?.days ? `?days=${params.days}` : "";
    return apiFetch(`/dashboard/technicians/top${qs}`);
  },
  async deviceModels() {
    return apiFetch("/dashboard/device-models");
  },
};

export const reports = {
  async serviceOrders(params?: { start_date?: string; end_date?: string; status?: string }) {
    const qs = new URLSearchParams();
    if (params?.start_date) qs.set("start_date", params.start_date);
    if (params?.end_date) qs.set("end_date", params.end_date);
    if (params?.status) qs.set("status", params.status);
    const query = qs.toString();
    return apiFetch(`/reports/service-orders${query ? "?" + query : ""}`);
  },
  async services(params?: { start_date?: string; end_date?: string }) {
    const qs = new URLSearchParams();
    if (params?.start_date) qs.set("start_date", params.start_date);
    if (params?.end_date) qs.set("end_date", params.end_date);
    const query = qs.toString();
    return apiFetch(`/reports/services${query ? "?" + query : ""}`);
  },
  async deviceModels() {
    return apiFetch("/reports/device-models");
  },
};

export const admin = {
  async dashboard() {
    return apiFetch("/admin/dashboard");
  },
  async companies(params?: { page?: number; limit?: number; status?: string }) {
    const qs = new URLSearchParams();
    if (params?.page) qs.set("page", String(params.page));
    if (params?.limit) qs.set("limit", String(params.limit));
    if (params?.status) qs.set("status", params.status);
    const query = qs.toString();
    return apiFetch(`/admin/companies${query ? "?" + query : ""}`);
  },
  async updateStatus(id: string, data: { status: string; reason?: string }) {
    return apiFetch(`/admin/companies/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },
  async subscriptions() {
    return apiFetch("/admin/subscriptions");
  },
  async payments() {
    return apiFetch("/admin/payments");
  },
  async webhookEvents() {
    return apiFetch("/admin/webhooks");
  },
  async getSettings() {
    return apiFetch("/admin/settings");
  },
  async updateSettings(data: Record<string, any>) {
    return apiFetch("/admin/settings", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },
};

export const exportsApi = {
  async customers() {
    const token = getToken();
    const res = await fetch(`${API_BASE}/exports/customers`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) throw new Error("Erro ao exportar");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `clientes_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  },
  async serviceOrders() {
    const token = getToken();
    const res = await fetch(`${API_BASE}/exports/service-orders`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) throw new Error("Erro ao exportar");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `os_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  },
};

export const portal = {
  async track(trackingCode: string) {
    return apiFetch(`/portal/track/${encodeURIComponent(trackingCode)}`);
  },
};
