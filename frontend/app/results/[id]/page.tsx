'use client';

import { CheckCircle2, Download, FileText, Loader2, XCircle } from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

// Mock translation object - will be replaced with next-intl later
const translations = {
  common: {
    loading: 'Carregando...',
    error: 'Erro',
    back: 'Voltar',
  },
  results: {
    processing: 'Processando Otimização',
    processingDescription: 'Seu currículo está sendo otimizado por IA. Isso leva alguns minutos.',
    download: 'Baixar Currículo Otimizado',
    viewOptimized: 'Visualizar Currículo Otimizado',
    error: 'Erro ao processar otimização',
    title: 'Currículo Otimizado com Sucesso!',
    subtitle: 'Seu currículo foi otimizado e está pronto para download.',
  },
};

interface ResumeImprovementStatus {
  id: string;
  resume_id: string;
  job_id: string;
  user_id: string;
  status: string;
  optimized_content: string | null;
  docx_storage_path: string | null;
  match_percentage: number | null;
  suggestions: string[] | null;
  keywords: string[] | null;
  error_message: string | null;
  created_at: string;
  processing_started_at: string | null;
  processing_completed_at: string | null;
}

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const improvementId = params.id as string;

  const [status, setStatus] = useState<ResumeImprovementStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  // Poll for resume improvement status
  useEffect(() => {
    if (!improvementId) return;

    const fetchStatus = async () => {
      try {
        // TODO: Replace with actual CV-Match API endpoint
        // For now, simulate the API call
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Mock data for development
        const mockStatus: ResumeImprovementStatus = {
          id: improvementId,
          resume_id: 'mock-resume-id',
          job_id: 'mock-job-id',
          user_id: 'mock-user-id',
          status: Math.random() > 0.5 ? 'completed' : 'processing',
          optimized_content:
            Math.random() > 0.5 ? 'Este é o conteúdo otimizado do currículo...' : null,
          docx_storage_path: Math.random() > 0.5 ? 'optimized-resumes/mock-file.docx' : null,
          match_percentage: Math.random() > 0.5 ? 85 : null,
          suggestions:
            Math.random() > 0.5
              ? ['Adicione mais palavras-chave técnicas', 'Quantifique suas conquistas']
              : null,
          keywords: Math.random() > 0.5 ? ['React', 'TypeScript', 'Node.js', 'AWS'] : null,
          error_message: null,
          created_at: new Date().toISOString(),
          processing_started_at: new Date().toISOString(),
          processing_completed_at: Math.random() > 0.5 ? new Date().toISOString() : null,
        };

        setStatus(mockStatus);
        setLoading(false);

        // Stop polling if completed or failed
        if (mockStatus.status === 'completed' || mockStatus.status === 'failed') {
          // Will be cleared in useEffect cleanup
        }
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : translations.results.error);
        setLoading(false);
        // Will be cleared in useEffect cleanup
      }
    };

    // Set up polling interval
    const pollInterval: NodeJS.Timeout = setInterval(fetchStatus, 3000);

    // Initial fetch
    fetchStatus();

    return () => {
      clearInterval(pollInterval);
    };
  }, [improvementId]);

  const handleDownload = async () => {
    if (!status?.docx_storage_path) return;

    setDownloading(true);

    try {
      // TODO: Replace with actual CV-Match API endpoint
      // This would be a new endpoint like GET /api/resumes/:id/download

      // For now, simulate the download
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Simulate file download
      const blob = new Blob(['Mock optimized resume content'], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `curriculo_otimizado_${improvementId}.docx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      setError('Erro ao baixar arquivo. Por favor, tente novamente.');
    } finally {
      setDownloading(false);
    }
  };

  // Render loading state
  if (loading) {
    return (
      <div className="container max-w-4xl mx-auto py-16 px-4">
        <div className="flex flex-col items-center justify-center gap-4">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
          <p className="text-lg text-muted-foreground">{translations.common.loading}</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="container max-w-4xl mx-auto py-16 px-4">
        <Card className="border-red-200">
          <CardHeader>
            <div className="flex items-center gap-2">
              <XCircle className="w-6 h-6 text-red-600" />
              <CardTitle className="text-red-600">{translations.common.error}</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={() => router.push('/upload')} variant="outline">
              {translations.common.back}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Render processing state
  if (status && status.status !== 'completed' && status.status !== 'failed') {
    return (
      <div className="container max-w-4xl mx-auto py-16 px-4">
        <Card>
          <CardHeader>
            <CardTitle>{translations.results.processing}</CardTitle>
            <CardDescription>{translations.results.processingDescription}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              <div className="flex-1">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full animate-pulse"
                    style={{ width: '60%' }}
                  />
                </div>
                <p className="text-sm text-muted-foreground mt-2">Status: {status.status}</p>
              </div>
            </div>

            <div className="p-4 bg-muted/50 rounded-lg">
              <h4 className="font-medium mb-2">Aguarde enquanto processamos:</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li>✓ Extração do texto do currículo</li>
                <li>✓ Análise de compatibilidade com a vaga</li>
                <li>
                  {status.status === 'processing' ? '⏳' : '○'} Otimização com Inteligência
                  Artificial
                </li>
                <li>○ Geração do arquivo final</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Render failed state
  if (status && status.status === 'failed') {
    return (
      <div className="container max-w-4xl mx-auto py-16 px-4">
        <Card className="border-red-200">
          <CardHeader>
            <div className="flex items-center gap-2">
              <XCircle className="w-6 h-6 text-red-600" />
              <CardTitle className="text-red-600">Erro no Processamento</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">
              {status.error_message || translations.results.error}
            </p>
            <div className="flex gap-2">
              <Button onClick={() => router.push('/upload')} variant="outline">
                Tentar Novamente
              </Button>
              <Button onClick={() => router.push('/dashboard')} variant="ghost">
                Ir para Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Render completed state
  return (
    <div className="container max-w-4xl mx-auto py-8 px-4">
      {/* Success Header */}
      <div className="mb-8 text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <CheckCircle2 className="w-8 h-8 text-green-600" />
          <h1 className="text-3xl font-bold">{translations.results.title}</h1>
        </div>
        <p className="text-muted-foreground">{translations.results.subtitle}</p>
      </div>

      {/* Match Score */}
      {status?.match_percentage && (
        <Card className="mb-6 border-blue-200 bg-blue-50/50">
          <CardHeader>
            <CardTitle className="text-blue-800">Compatibilidade com a Vaga</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="text-4xl font-bold text-blue-600">
                {Math.round(status.match_percentage)}%
              </div>
              <div className="flex-1">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${status.match_percentage}%` }}
                  />
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  Seu currículo corresponde a {Math.round(status.match_percentage)}% dos requisitos
                  da vaga
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Keywords */}
      {status?.keywords && status.keywords.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Palavras-chave Identificadas</CardTitle>
            <CardDescription>
              Termos importantes que foram destacados na sua otimização
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {status.keywords.map((keyword, index) => (
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
      )}

      {/* Suggestions */}
      {status?.suggestions && status.suggestions.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Sugestões de Melhoria</CardTitle>
            <CardDescription>
              Recomendações para fortalecer ainda mais seu currículo
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {status.suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{suggestion}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Download Card */}
      <Card className="mb-6 border-green-200 bg-green-50/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Currículo Otimizado
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Button onClick={handleDownload} disabled={downloading} size="lg" className="w-full">
            {downloading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Baixando...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                {translations.results.download}
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Optimized Text Preview */}
      {status?.optimized_content && (
        <Card>
          <CardHeader>
            <CardTitle>{translations.results.viewOptimized}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <pre className="whitespace-pre-wrap text-sm font-sans bg-muted p-4 rounded-lg">
                {status.optimized_content}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="mt-6 flex gap-4">
        <Button onClick={() => router.push('/upload')} variant="outline">
          Otimizar Outro Currículo
        </Button>
        <Button onClick={() => router.push('/dashboard')} variant="ghost">
          Ir para Dashboard
        </Button>
      </div>
    </div>
  );
}
