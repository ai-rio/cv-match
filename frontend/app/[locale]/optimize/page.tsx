'use client';

import {
  AlertCircle,
  CheckCircle,
  Download,
  FileText,
  Loader2,
  Rocket,
  Sparkles,
} from 'lucide-react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense, useCallback, useEffect, useState } from 'react';

import { JobDescriptionForm } from '@/components/resume/JobDescriptionForm';
import { ResumeUpload } from '@/components/resume/ResumeUpload';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';

// Portuguese translations
const translations = {
  title: 'Otimização de Currículo com IA',
  subtitle:
    'Transforme seu currículo para corresponder perfeitamente à descrição da vaga desejada com otimização alimentada por IA',
  steps: {
    upload: 'Enviar Currículo',
    jobDetails: 'Detalhes da Vaga',
    payment: 'Pagamento',
    processing: 'Processando',
    results: 'Resultados',
  },
  upload: {
    title: 'Envie seu Currículo',
    subtitle:
      'Envie seu currículo atual em formato PDF ou DOCX para começar o processo de otimização',
    dragDrop: 'Arraste e solte seu currículo aqui',
    formats: 'PDF ou DOCX (máx 2MB)',
    button: 'Escolher Arquivo',
    uploading: 'Enviando...',
    invalidType: 'Tipo de arquivo inválido. Use PDF ou DOCX.',
    tooLarge: 'Arquivo muito grande. Tamanho máximo é 2MB.',
    charCount: (current: number, max: number) => `${current}/${max} caracteres`,
  },
  jobDescription: {
    title: 'Detalhes da Vaga',
    subtitle: 'Digite os detalhes da vaga que você deseja se candidatar',
    jobTitle: 'Cargo',
    company: 'Empresa',
    description: 'Descrição da Vaga',
    jobTitlePlaceholder: 'ex: Desenvolvedor Python Sênior',
    companyPlaceholder: 'ex: TechCorp Brasil',
    descriptionPlaceholder: 'Cole aqui a descrição completa da vaga...',
    minChars: 'Mínimo: 50 caracteres',
    maxChars: 'Máximo: 5000 caracteres',
    charCount: (current: number, max: number) => `${current}/${max}`,
    submit: 'Continuar para Pagamento',
    startOptimization: 'Iniciar Otimização',
  },
  payment: {
    title: 'Pagamento',
    subtitle: 'Complete sua compra para desbloquear a otimização de currículo com IA',
    orderSummary: 'Resumo do Pedido',
    resume: 'Currículo:',
    position: 'Posição:',
    total: 'Total:',
    processing: 'Processando pagamento...',
    securePayment: 'Pagamento seguro processado por Stripe',
  },
  processing: {
    title: 'Otimizando seu Currículo',
    subtitle:
      'Nossa IA está analisando e otimizando seu currículo. Isso geralmente leva 2-3 minutos.',
    extracting: 'Extraindo texto do currículo',
    analyzing: 'Analisando requisitos da vaga',
    optimizing: 'Otimização com IA em andamento',
    generating: 'Gerando documento otimizado',
  },
  results: {
    title: 'Seu Currículo Otimizado',
    subtitle: 'Seu currículo foi otimizado e está pronto para download',
    download: 'Baixar Currículo Otimizado',
    viewOptimized: 'Visualizar Conteúdo Otimizado',
    matchScore: 'Score de Compatibilidade',
    improvements: 'Melhorias Principais',
    keywords: 'Palavras-chave Adicionadas',
    downloadAnother: 'Otimizar Outro Currículo',
    goToDashboard: 'Ir para Dashboard',
  },
  errors: {
    notAuthenticated: 'Você precisa estar autenticado para continuar.',
    paymentFailed: 'Pagamento falhou. Tente novamente.',
    optimizationFailed: 'Otimização falhou. Tente novamente.',
    downloadFailed: 'Download falhou. Tente novamente.',
  },
  common: {
    loading: 'Carregando...',
    error: 'Erro',
    back: 'Voltar',
    next: 'Próximo',
    startOver: 'Recomeçar',
    tryAgain: 'Tentar Novamente',
  },
};

interface ResumeData {
  id: string;
  name: string;
}

interface JobDescriptionData {
  jobTitle: string;
  company: string;
  description: string;
}

const OPTIMIZATION_TIER = {
  id: 'basic-credit',
  name: 'Pacote de Créditos Básico',
  price: 1900, // R$19 in cents
  currency: 'BRL',
  interval: 'lifetime' as const,
  description: '10 créditos para otimização de currículo com IA',
  features: [
    '10 otimizações de currículo com IA',
    'Formatação compatível com ATS',
    'Otimização de palavras-chave',
    'Aprimoramento profissional',
    'Download em formato .docx',
    'Resultados em 2-3 minutos',
    'Créditos não expiram',
  ],
  isFree: false,
};

type WorkflowStep = 'upload' | 'job-details' | 'payment' | 'processing' | 'results';

function OptimizePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const resumeId = searchParams?.get('resume_id');

  const [currentStep, setCurrentStep] = useState<WorkflowStep>(resumeId ? 'job-details' : 'upload');
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [jobDescription, setJobDescription] = useState<JobDescriptionData | null>(null);
  const [optimizationId, setOptimizationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleResumeUploaded = useCallback((data: ResumeData) => {
    setResumeData(data);
    setCurrentStep('job-details');
    setError(null);
  }, []);

  const startOptimization = useCallback(async () => {
    if (!resumeData || !jobDescription) {
      setError('Dados do currículo ou da vaga ausentes');
      return;
    }

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      // Get Supabase session for auth token
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        throw new Error('Você precisa estar autenticado');
      }

      const response = await fetch(`${API_URL}/api/optimizations/start`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_id: resumeData.id,
          job_title: jobDescription.jobTitle,
          company: jobDescription.company,
          job_description: jobDescription.description,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao iniciar otimização');
      }

      const data = await response.json();
      setOptimizationId(data.optimization_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao iniciar otimização');
      setCurrentStep('payment');
      throw err;
    }
  }, [resumeData, jobDescription]);

  const handleJobDescriptionSubmit = useCallback(
    async (data: JobDescriptionData) => {
      setJobDescription(data);
      setError(null);

      try {
        // Check if user is authenticated
        const supabase = createClient();
        const {
          data: { user },
          error: authError,
        } = await supabase.auth.getUser();

        if (authError || !user) {
          setError(translations.errors.notAuthenticated);
          router.push('/auth/login');
          return;
        }

        // Check if user has available credits
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const {
          data: { session },
        } = await supabase.auth.getSession();

        if (!session) {
          setError(translations.errors.notAuthenticated);
          router.push('/auth/login');
          return;
        }

        const creditsResponse = await fetch(`${API_URL}/api/optimizations/credits/check`, {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
        });

        if (creditsResponse.ok) {
          const creditsData = await creditsResponse.json();
          if (creditsData.credits > 0) {
            // User has credits, proceed to optimization
            setCurrentStep('processing');
            await startOptimization();
            return;
          }
        }

        // No credits available, proceed to payment
        setCurrentStep('payment');
      } catch (error) {
        setError(error instanceof Error ? error.message : 'Failed to check usage limits');
      }
    },
    [router, startOptimization]
  );

  const handlePaymentSuccess = useCallback(async () => {
    if (!resumeData || !jobDescription) {
      setError('Missing resume or job description data');
      return;
    }

    try {
      setCurrentStep('processing');
      await startOptimization();
    } catch {
      // Error is already handled in startOptimization
    }
  }, [resumeData, jobDescription, startOptimization]);

  const handleOptimizationComplete = useCallback(() => {
    setCurrentStep('results');
  }, []);

  const handleDownloadOptimized = useCallback(async () => {
    if (!optimizationId) return;

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      // Get Supabase session for auth token
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        throw new Error('Você precisa estar autenticado');
      }

      const response = await fetch(`${API_URL}/api/optimizations/${optimizationId}/download`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao baixar arquivo');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `curriculo_otimizado_${Date.now()}.docx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao baixar arquivo');
    }
  }, [optimizationId]);

  const handleStartOver = useCallback(() => {
    setCurrentStep('upload');
    setResumeData(null);
    setJobDescription(null);
    setOptimizationId(null);
    setError(null);
    router.push('/optimize');
  }, [router]);

  const isStepCompleted = (step: WorkflowStep): boolean => {
    const steps: WorkflowStep[] = ['upload', 'job-details', 'payment', 'processing', 'results'];
    const currentIndex = steps.indexOf(currentStep);
    const stepIndex = steps.indexOf(step);
    return stepIndex < currentIndex;
  };

  const isStepActive = (step: WorkflowStep): boolean => {
    return currentStep === step;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Sparkles className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">{translations.title}</h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">{translations.subtitle}</p>
        </div>

        {/* Progress Steps */}
        <Card className="mb-8 max-w-4xl mx-auto">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              {[
                {
                  step: 'upload' as WorkflowStep,
                  label: translations.steps.upload,
                  icon: FileText,
                },
                {
                  step: 'job-details' as WorkflowStep,
                  label: translations.steps.jobDetails,
                  icon: FileText,
                },
                {
                  step: 'payment' as WorkflowStep,
                  label: translations.steps.payment,
                  icon: Sparkles,
                },
                {
                  step: 'processing' as WorkflowStep,
                  label: translations.steps.processing,
                  icon: Rocket,
                },
                {
                  step: 'results' as WorkflowStep,
                  label: translations.steps.results,
                  icon: CheckCircle,
                },
              ].map(({ step, label, icon: Icon }) => (
                <div key={step} className="flex items-center">
                  <div className="flex flex-col items-center">
                    <div
                      className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors ${
                        isStepCompleted(step)
                          ? 'bg-green-500 border-green-500 text-white'
                          : isStepActive(step)
                            ? 'bg-blue-500 border-blue-500 text-white'
                            : 'bg-white border-gray-300 text-gray-400'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                    </div>
                    <span
                      className={`mt-2 text-sm font-medium ${
                        isStepActive(step)
                          ? 'text-blue-600'
                          : isStepCompleted(step)
                            ? 'text-green-600'
                            : 'text-gray-500'
                      }`}
                    >
                      {label}
                    </span>
                  </div>
                  {step !== 'results' && (
                    <div
                      className={`flex-1 h-0.5 mx-2 transition-colors ${
                        isStepCompleted(step) ? 'bg-green-500' : 'bg-gray-300'
                      }`}
                    />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <div className="mb-6 max-w-2xl mx-auto p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-red-600 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {/* Upload Step */}
          {currentStep === 'upload' && (
            <div className="space-y-6">
              <ResumeUpload
                onUploadSuccess={(resumeId, fileName) => {
                  handleResumeUploaded({ id: resumeId, name: fileName });
                }}
              />

              {/* Features */}
              <div className="grid md:grid-cols-3 gap-4">
                {OPTIMIZATION_TIER.features.slice(0, 3).map((feature, index) => (
                  <Card key={index} className="text-center">
                    <CardContent className="pt-6">
                      <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
                      <p className="text-sm font-medium">{feature}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Job Details Step */}
          {currentStep === 'job-details' && (
            <div className="space-y-6">
              <JobDescriptionForm
                onJobDescriptionSubmit={handleJobDescriptionSubmit}
                isDisabled={false}
              />

              {/* Resume Summary */}
              {resumeData && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Uploaded Resume</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-blue-600" />
                      <span className="font-medium">{resumeData.name}</span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                        Ready for optimization
                      </span>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Payment Step */}
          {currentStep === 'payment' && (
            <div className="space-y-6">
              <PaymentFlow tier={OPTIMIZATION_TIER} onSuccess={handlePaymentSuccess} />

              {/* Summary */}
              <Card>
                <CardHeader>
                  <CardTitle>{translations.payment.orderSummary}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>{translations.payment.resume}</span>
                    <span className="font-medium">{resumeData?.name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>{translations.payment.position}</span>
                    <span className="font-medium">
                      {jobDescription?.jobTitle} at {jobDescription?.company}
                    </span>
                  </div>
                  <div className="border-t pt-4">
                    <div className="flex items-center justify-between text-lg font-bold">
                      <span>{translations.payment.total}</span>
                      <span>R${(OPTIMIZATION_TIER.price / 100).toFixed(2)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Processing Step */}
          {currentStep === 'processing' && optimizationId && (
            <OptimizationProgress onComplete={handleOptimizationComplete} />
          )}

          {/* Results Step */}
          {currentStep === 'results' && optimizationId && (
            <ResultsDisplay
              optimizationId={optimizationId}
              onDownload={handleDownloadOptimized}
              onStartOver={handleStartOver}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default function OptimizePage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <OptimizePageContent />
    </Suspense>
  );
}

function LoadingFallback() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  );
}

function PaymentFlow({
  tier,
  onSuccess,
}: {
  tier: typeof OPTIMIZATION_TIER;
  onSuccess: () => void;
}) {
  const [isProcessing, setIsProcessing] = useState(false);

  const handlePayment = async () => {
    setIsProcessing(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      // Get Supabase session for auth token
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        throw new Error('Você precisa estar autenticado');
      }

      const response = await fetch(`${API_URL}/api/payments/create-checkout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tier_id: tier.id,
          price: tier.price,
          currency: 'brl', // Using Brazilian Real for the market
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao processar pagamento');
      }

      const data = await response.json();

      // Redirect to Stripe Checkout
      window.location.href = data.checkout_url;
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{translations.payment.title}</CardTitle>
        <CardDescription>{translations.payment.subtitle}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-center">
          <div className="mb-4">
            <h3 className="text-xl font-semibold">{tier.name}</h3>
            <p className="text-gray-600">{tier.description}</p>
          </div>
          <div className="text-3xl font-bold mb-6">R${(tier.price / 100).toFixed(2)}</div>

          <div className="text-left mb-6">
            <h4 className="font-medium mb-2">Features:</h4>
            <ul className="space-y-1">
              {tier.features.map((feature, index) => (
                <li key={index} className="flex items-center gap-2 text-sm">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  {feature}
                </li>
              ))}
            </ul>
          </div>

          <Button onClick={handlePayment} disabled={isProcessing} size="lg" className="w-full">
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                {translations.payment.processing}
              </>
            ) : (
              `Pagar R$${(tier.price / 100).toFixed(2)}`
            )}
          </Button>
        </div>

        <p className="text-xs text-center text-gray-500 mt-4">
          {translations.payment.securePayment}
        </p>
      </CardContent>
    </Card>
  );
}

function OptimizationProgress({ onComplete }: { onComplete: () => void }) {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    translations.processing.extracting,
    translations.processing.analyzing,
    translations.processing.optimizing,
    translations.processing.generating,
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= steps.length - 1) {
          clearInterval(interval);
          // Simulate completion
          setTimeout(() => {
            onComplete();
          }, 1000);
          return prev;
        }
        return prev + 1;
      });
    }, 1500);

    return () => clearInterval(interval);
  }, [steps, onComplete]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{translations.processing.title}</CardTitle>
        <CardDescription>{translations.processing.subtitle}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          {steps.map((step, index) => (
            <div key={index} className="flex items-center gap-3">
              <div
                className={`w-4 h-4 rounded-full border-2 ${
                  index < currentStep
                    ? 'bg-green-500 border-green-500'
                    : index === currentStep
                      ? 'bg-blue-500 border-blue-500 animate-pulse'
                      : 'border-gray-300'
                }`}
              />
              <span
                className={`text-sm ${
                  index < currentStep
                    ? 'text-green-600'
                    : index === currentStep
                      ? 'text-blue-600 font-medium'
                      : 'text-gray-400'
                }`}
              >
                {step}
              </span>
            </div>
          ))}
        </div>

        <div className="text-center py-4">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
          <p className="text-sm text-gray-600">This usually takes 2-3 minutes...</p>
        </div>
      </CardContent>
    </Card>
  );
}

function ResultsDisplay({
  optimizationId,
  onDownload,
  onStartOver,
}: {
  optimizationId: string;
  onDownload: () => void;
  onStartOver: () => void;
}) {
  const [results, setResults] = useState<{
    optimizedContent: string;
    matchScore: number;
    improvements: string[];
    keywords: string[];
  } | null>(null);

  useEffect(() => {
    // Mock results data
    setResults({
      optimizedContent: 'Mock optimized resume content with improvements...',
      matchScore: 85,
      improvements: [
        'Added relevant keywords from job description',
        'Improved action verbs and achievements',
        'Enhanced formatting for ATS compatibility',
        'Quantified achievements with metrics',
      ],
      keywords: ['React', 'TypeScript', 'Node.js', 'AWS', 'Agile', 'REST API'],
    });
  }, [optimizationId]);

  if (!results) {
    return (
      <div className="text-center py-8">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
        <p className="text-gray-600">Loading results...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Success Header */}
      <Card className="border-green-200 bg-green-50">
        <CardContent className="pt-6 text-center">
          <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-green-800 mb-2">{translations.results.title}</h2>
          <p className="text-green-700">{translations.results.subtitle}</p>
        </CardContent>
      </Card>

      {/* Match Score */}
      <Card>
        <CardHeader>
          <CardTitle>{translations.results.matchScore}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="text-4xl font-bold text-blue-600">{results.matchScore}%</div>
            <div className="flex-1">
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full"
                  style={{ width: `${results.matchScore}%` }}
                />
              </div>
              <p className="text-sm text-gray-600 mt-1">
                Your resume matches {results.matchScore}% of the job requirements
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Download Button */}
      <Card>
        <CardContent className="pt-6">
          <Button onClick={onDownload} size="lg" className="w-full">
            <Download className="w-4 h-4 mr-2" />
            {translations.results.download}
          </Button>
        </CardContent>
      </Card>

      {/* Improvements */}
      <Card>
        <CardHeader>
          <CardTitle>{translations.results.improvements}</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {results.improvements.map((improvement: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span className="text-sm">{improvement}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Keywords */}
      <Card>
        <CardHeader>
          <CardTitle>{translations.results.keywords}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {results.keywords.map((keyword: string, index: number) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
              >
                {keyword}
              </span>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex gap-4">
        <Button onClick={onStartOver} variant="outline">
          {translations.results.downloadAnother}
        </Button>
        <Button onClick={() => (window.location.href = '/dashboard')} variant="ghost">
          {translations.results.goToDashboard}
        </Button>
      </div>
    </div>
  );
}
