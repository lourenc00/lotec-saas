"use client";

import { useEffect, useState } from "react";
import { admin as adminApi } from "@/lib/api";

const SECTIONS = [
  {
    id: "features",
    title: "Recursos",
    description: "Habilite ou desabilite funcionalidades do sistema",
    type: "toggles",
    toggles: [
      { key: "feature_mercadopago", label: "Mercado Pago (cobranças e assinaturas)", default: true },
      { key: "feature_emails", label: "E-mails automáticos (SMTP)", default: false },
      { key: "feature_photos", label: "Upload de fotos nas OS (S3/MinIO)", default: false },
      { key: "feature_portal", label: "Portal público de acompanhamento", default: true },
      { key: "feature_trial", label: "Período de teste gratuito", default: true },
    ],
  },
  {
    id: "mercadopago",
    title: "Mercado Pago",
    description: "Credenciais para cobranças e assinaturas",
    fields: [
      { key: "mp_access_token", label: "Access Token", type: "password", placeholder: "APP_USR-..." },
      { key: "mp_public_key", label: "Public Key", type: "text", placeholder: "APP_USR-..." },
      { key: "mp_webhook_secret", label: "Webhook Secret", type: "password", placeholder: "Opcional" },
      { key: "mp_basic_plan_id", label: "Plano Básico - ID", type: "text", placeholder: "ID do plano no MP" },
      { key: "mp_pro_plan_id", label: "Plano Profissional - ID", type: "text", placeholder: "ID do plano no MP" },
      { key: "mp_premium_plan_id", label: "Plano Premium - ID", type: "text", placeholder: "ID do plano no MP" },
    ],
  },
  {
    id: "plans",
    title: "Planos",
    description: "Ative ou desative planos de assinatura",
    type: "toggles",
    toggles: [
      { key: "plan_basic_active", label: "Plano Básico (R$ 29,90/mês)", default: true },
      { key: "plan_pro_active", label: "Plano Profissional (R$ 49,90/mês)", default: true },
      { key: "plan_premium_active", label: "Plano Premium (R$ 79,90/mês)", default: true },
    ],
  },
  {
    id: "smtp",
    title: "E-mails (SMTP)",
    description: "Configuração do servidor de e-mails",
    fields: [
      { key: "smtp_host", label: "Host", type: "text", placeholder: "smtp.gmail.com" },
      { key: "smtp_port", label: "Porta", type: "text", placeholder: "587" },
      { key: "smtp_user", label: "Usuário", type: "text", placeholder: "seu@email.com" },
      { key: "smtp_password", label: "Senha", type: "password", placeholder: "••••••••" },
      { key: "smtp_from", label: "E-mail remetente", type: "text", placeholder: "noreply@lotec.com.br" },
    ],
  },
  {
    id: "s3",
    title: "Armazenamento (S3/MinIO)",
    description: "Para upload de fotos de OS",
    fields: [
      { key: "s3_endpoint", label: "Endpoint", type: "text", placeholder: "https://s3.amazonaws.com" },
      { key: "s3_access_key", label: "Access Key", type: "password", placeholder: "••••••••" },
      { key: "s3_secret_key", label: "Secret Key", type: "password", placeholder: "••••••••" },
      { key: "s3_bucket", label: "Bucket", type: "text", placeholder: "lotec-files" },
      { key: "s3_region", label: "Região", type: "text", placeholder: "us-east-1" },
    ],
  },
  {
    id: "general",
    title: "Geral",
    description: "Configurações gerais do sistema",
    fields: [
      { key: "grace_period_days", label: "Dias de tolerância (pós-cancelamento)", type: "text", placeholder: "5" },
      { key: "trial_days", label: "Dias de teste gratuito", type: "text", placeholder: "14" },
      { key: "max_users_free", label: "Máx. usuários (plano grátis)", type: "text", placeholder: "1" },
    ],
  },
];

function Toggle({ checked, onChange }: { checked: boolean; onChange: () => void }) {
  return (
    <button
      type="button"
      onClick={onChange}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        checked ? "bg-blue-600" : "bg-gray-300"
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          checked ? "translate-x-6" : "translate-x-1"
        }`}
      />
    </button>
  );
}

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [activeSection, setActiveSection] = useState("features");

  useEffect(() => {
    adminApi
      .getSettings()
      .then(setSettings)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const getToggleValue = (key: string, defaultVal: boolean): boolean => {
    const val = settings[key]?.value;
    if (val === undefined || val === null || val === "") return defaultVal;
    return val === "true" || val === "1";
  };

  const handleToggle = (key: string, defaultVal: boolean) => {
    const current = getToggleValue(key, defaultVal);
    setSettings((prev) => ({
      ...prev,
      [key]: { value: (!current).toString(), description: null },
    }));
  };

  const handleChange = (key: string, value: string) => {
    setSettings((prev) => ({
      ...prev,
      [key]: { ...prev[key], value },
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      const data: Record<string, any> = {};
      for (const [key, setting] of Object.entries(settings)) {
        data[key] = setting.value;
      }
      await adminApi.updateSettings(data);
      setMessage("Configurações salvas com sucesso!");
      setTimeout(() => setMessage(""), 3000);
    } catch (err: any) {
      setMessage("Erro: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="text-gray-500">Carregando...</div>;

  const section = SECTIONS.find((s) => s.id === activeSection)!;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Configurações</h1>
        <button
          onClick={handleSave}
          disabled={saving}
          className="bg-blue-600 text-white px-6 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Salvando..." : "Salvar Alterações"}
        </button>
      </div>

      {message && (
        <div className={`rounded-lg p-3 mb-4 text-sm ${
          message.startsWith("Erro") ? "bg-red-50 text-red-700" : "bg-green-50 text-green-700"
        }`}>
          {message}
        </div>
      )}

      <div className="flex gap-6">
        <div className="w-56 flex-shrink-0">
          <nav className="space-y-1">
            {SECTIONS.map((s) => (
              <button
                key={s.id}
                onClick={() => setActiveSection(s.id)}
                className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                  activeSection === s.id
                    ? "bg-blue-50 text-blue-700"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                {s.title}
              </button>
            ))}
          </nav>
        </div>

        <div className="flex-1 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-1">{section.title}</h2>
          <p className="text-sm text-gray-500 mb-6">{section.description}</p>

          {section.type === "toggles" && section.toggles && (
            <div className="space-y-4">
              {section.toggles.map((toggle) => (
                <div key={toggle.key} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <span className="text-sm font-medium text-gray-700">{toggle.label}</span>
                  <Toggle
                    checked={getToggleValue(toggle.key, toggle.default)}
                    onChange={() => handleToggle(toggle.key, toggle.default)}
                  />
                </div>
              ))}
            </div>
          )}

          {section.type !== "toggles" && section.fields && (
            <div className="space-y-4">
              {section.fields.map((field) => (
                <div key={field.key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {field.label}
                  </label>
                  <input
                    type={field.type}
                    value={settings[field.key]?.value || ""}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    placeholder={field.placeholder}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
