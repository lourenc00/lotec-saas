import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-600 to-blue-800 text-white">
      <nav className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Lotec</h1>
        <div className="flex items-center gap-4">
          <Link href="/acompanhar" className="text-blue-200 hover:text-white text-sm">
            Acompanhar OS
          </Link>
          <Link href="/login" className="text-blue-200 hover:text-white text-sm">
            Entrar
          </Link>
          <Link href="/cadastro" className="bg-white text-blue-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-50">
            Começar Grátis
          </Link>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-20 text-center">
        <h2 className="text-5xl font-bold mb-6 leading-tight">
          Gestão completa para<br />assistências técnicas
        </h2>
        <p className="text-xl text-blue-200 mb-10 max-w-2xl mx-auto">
          Ordens de serviço, clientes, aparelhos, estoque e financeiro — tudo em um só lugar.
          Multi-tenant, seguro e escalável.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link href="/cadastro" className="bg-white text-blue-700 px-8 py-3 rounded-lg font-semibold text-lg hover:bg-blue-50">
            Criar Conta Grátis
          </Link>
          <Link href="/planos" className="border border-blue-400 text-white px-8 py-3 rounded-lg font-semibold text-lg hover:bg-blue-700">
            Ver Planos
          </Link>
        </div>
      </main>

      <section className="max-w-6xl mx-auto px-4 py-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-blue-700/50 rounded-xl p-6">
          <div className="text-3xl mb-3">🔧</div>
          <h3 className="font-semibold text-lg mb-2">Ordens de Serviço</h3>
          <p className="text-blue-200 text-sm">Crie, acompanhe e gerencie todas as OS com histórico completo e status em tempo real.</p>
        </div>
        <div className="bg-blue-700/50 rounded-xl p-6">
          <div className="text-3xl mb-3">👥</div>
          <h3 className="font-semibold text-lg mb-2">Clientes e Aparelhos</h3>
          <p className="text-blue-200 text-sm">Cadastre clientes e dispositivos. Histórico de atendimentos sempre disponível.</p>
        </div>
        <div className="bg-blue-700/50 rounded-xl p-6">
          <div className="text-3xl mb-3">📊</div>
          <h3 className="font-semibold text-lg mb-2">Relatórios</h3>
          <p className="text-blue-200 text-sm">Dashboards, relatórios por período, exportação CSV e métricas do seu negócio.</p>
        </div>
      </section>

      <footer className="max-w-6xl mx-auto px-4 py-8 text-center text-blue-300 text-sm border-t border-blue-700">
        &copy; {new Date().getFullYear()} Lotec. Todos os direitos reservados.
      </footer>
    </div>
  );
}
