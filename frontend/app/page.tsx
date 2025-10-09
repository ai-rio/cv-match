import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
              <span className="block">Otimize Seu Currículo</span>
              <span className="block text-blue-600">com Inteligência Artificial</span>
            </h1>
            <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
              Transforme seu currículo para se destacar no mercado brasileiro. Nossa IA analisa sua
              experiência e a vaga desejada para criar um documento otimizado que passa pelos
              sistemas de ATS e impressiona recrutadores.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/optimize"
                className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10 transition-colors"
              >
                Começar Agora
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 md:py-4 md:text-lg md:px-10 transition-colors"
              >
                Ver Dashboard
              </Link>
            </div>
          </div>
        </div>

        {/* Background decoration */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-40 -right-32 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
          <div className="absolute -bottom-32 -left-32 w-80 h-80 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Como o CV-Match Funciona</h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Nossa plataforma utiliza tecnologia de ponta para garantir que seu currículo se destaque
            no competitivo mercado de trabalho brasileiro.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <FeatureCard
            step="1"
            title="Envie seu Currículo"
            description="Carregue seu currículo atual em PDF ou DOCX"
            icon="📄"
          />
          <FeatureCard
            step="2"
            title="Descreva a Vaga"
            description="Cole a descrição completa da vaga desejada"
            icon="💼"
          />
          <FeatureCard
            step="3"
            title="IA Otimiza"
            description="Nossa IA analisa e otimiza seu currículo"
            icon="🤖"
          />
          <FeatureCard
            step="4"
            title="Baixe o Resultado"
            description="Receba seu currículo otimizado em minutos"
            icon="⬇️"
          />
        </div>
      </div>

      {/* Benefits Section */}
      <div className="bg-white py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Por Que Escolher o CV-Match?</h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Ferramentas avançadas desenvolvidas especificamente para o mercado brasileiro
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            <BenefitCard
              title="Otimização ATS-Friendly"
              description="Sistema inteligente que formata seu currículo para passar pelos filtros automáticos das empresas"
              features={[
                'Análise de palavras-chave',
                'Formatação otimizada',
                'Estrutura padrão brasileira',
              ]}
            />
            <BenefitCard
              title="Inteligência Artificial"
              description="Tecnologia avançada que melhora seu conteúdo destacando suas qualificações mais relevantes"
              features={['Análise semântica', 'Sugestões personalizadas', 'Melhoria de linguagem']}
            />
            <BenefitCard
              title="Foco Brasil"
              description="Desenvolvido para o mercado brasileiro com atenção às particularidades locais"
              features={[
                'Formatos em português',
                'Real brasileiro (R$)',
                'Vagas de empresas brasileiras',
              ]}
            />
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-blue-600 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Pronto para Transformar Sua Carreira?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Junte-se a milhares de profissionais que já conseguiram suas vagas dos sonhos com
            currículos otimizados.
          </p>
          <Link
            href="/optimize"
            className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10 transition-colors"
          >
            Otimizar Meu Currículo Agora
          </Link>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 lg:grid-cols-4 text-center">
            <div>
              <div className="text-3xl font-bold text-blue-600">10K+</div>
              <div className="text-sm text-gray-600 mt-1">Currículos Otimizados</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600">85%</div>
              <div className="text-sm text-gray-600 mt-1">Taxa de Sucesso</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600">500+</div>
              <div className="text-sm text-gray-600 mt-1">Empresas Parceiras</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600">4.9★</div>
              <div className="text-sm text-gray-600 mt-1">Avaliação dos Usuários</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({
  step,
  title,
  description,
  icon,
}: {
  step: string;
  title: string;
  description: string;
  icon: string;
}) {
  return (
    <div className="relative text-center">
      <div className="flex flex-col items-center">
        <div className="flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full text-3xl mb-4">
          {icon}
        </div>
        <div className="absolute -top-2 -right-2 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
          {step}
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
      </div>
    </div>
  );
}

function BenefitCard({
  title,
  description,
  features,
}: {
  title: string;
  description: string;
  features: string[];
}) {
  return (
    <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-xl font-semibold text-gray-900 mb-4">{title}</h3>
      <p className="text-gray-600 mb-6">{description}</p>
      <ul className="space-y-3">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center gap-2">
            <svg
              className="w-5 h-5 text-green-500 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span className="text-gray-700">{feature}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
