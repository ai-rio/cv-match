'use client';

import { ArrowRight, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';

// Mock translation object - will be replaced with next-intl later
const translations = {
  title: 'Otimizar Currículo',
  subtitle:
    'Envie seu currículo e a descrição da vaga para receber uma versão otimizada com Inteligência Artificial',
  upload: {
    title: 'Enviar Seu Currículo',
    subtitle: 'Carregue seu currículo em PDF ou DOCX para começar a otimização',
    dragDrop: 'Arraste e solte o arquivo aqui',
    formats: 'PDF ou DOCX (máx. 2MB)',
    button: 'Escolher Arquivo',
    uploading: 'Carregando...',
    invalidType: 'Tipo de arquivo inválido. Use PDF ou DOCX.',
    tooLarge: 'Arquivo muito grande. Máximo 2MB.',
    charCount: (current: number, max: number) => `${current}/${max} caracteres`,
  },
  jobDescription: {
    title: 'Descrição da Vaga',
    subtitle: 'Cole a descrição completa da vaga que você quer se candidatar',
    placeholder:
      'Cole aqui a descrição completa da vaga...\n\nInclua:\n• Título da vaga\n• Responsabilidades\n• Requisitos\n• Habilidades desejadas\n• Benefícios',
    minChars: 'Mínimo: 50 caracteres',
    maxChars: 'Máximo: 5000 caracteres',
    charCount: (current: number, max: number) => `${current}/${max}`,
  },
  payment: {
    button: 'Otimizar Currículo - R$ 50,00',
    processing: 'Processando pagamento...',
    securePayment: 'Pagamento seguro processado pelo Stripe',
    errors: {
      notAuthenticated: 'Você precisa estar autenticado para continuar.',
    },
  },
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

interface ResumeUploadProps {
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  disabled?: boolean;
}

function ResumeUpload({ onFileSelect, onFileRemove, disabled = false }: ResumeUploadProps) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2MB
  const ACCEPTED_FILE_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ];

  const validateFile = (file: File): string | null => {
    if (!ACCEPTED_FILE_TYPES.includes(file.type)) {
      return translations.upload.invalidType;
    }
    if (file.size > MAX_FILE_SIZE) {
      return translations.upload.tooLarge;
    }
    return null;
  };

  const handleFile = (file: File) => {
    setError(null);

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    // Simulate upload progress
    setUploadProgress(0);
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 100);

    setTimeout(() => {
      setUploadedFile(file);
      onFileSelect(file);
    }, 1000);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setUploadProgress(0);
    setError(null);
    onFileRemove();
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{translations.upload.title}</CardTitle>
        <CardDescription>{translations.upload.subtitle}</CardDescription>
      </CardHeader>
      <CardContent>
        {!uploadedFile ? (
          <>
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`
                border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
                ${isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'}
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary hover:bg-primary/5'}
              `}
            >
              <input
                type="file"
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={handleFileChange}
                disabled={disabled}
                className="hidden"
                id="resume-file-input"
              />
              <label htmlFor="resume-file-input" className="cursor-pointer">
                <div className="flex flex-col items-center gap-4">
                  <svg
                    className="w-12 h-12 text-muted-foreground"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                  <div>
                    <p className="text-sm font-medium">{translations.upload.dragDrop}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {translations.upload.formats}
                    </p>
                  </div>
                  {!disabled && (
                    <Button type="button" variant="outline" size="sm">
                      {translations.upload.button}
                    </Button>
                  )}
                </div>
              </label>
            </div>

            {uploadProgress > 0 && uploadProgress < 100 && (
              <div className="mt-4">
                <p className="text-sm text-muted-foreground mb-2">
                  {translations.upload.uploading}
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-start gap-2">
                <svg
                  className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}
          </>
        ) : (
          <div className="border rounded-lg p-4 bg-muted/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className="flex-shrink-0">
                  <svg
                    className="w-10 h-10 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{uploadedFile.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatFileSize(uploadedFile.size)}
                  </p>
                </div>
                <svg
                  className="w-5 h-5 text-green-600 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              {!disabled && (
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={handleRemoveFile}
                  className="ml-2 flex-shrink-0"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </Button>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface JobDescriptionInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

function JobDescriptionInput({ value, onChange, disabled = false }: JobDescriptionInputProps) {
  const MIN_CHARS = 50;
  const MAX_CHARS = 5000;

  const charCount = value.length;
  const isValid = charCount >= MIN_CHARS && charCount <= MAX_CHARS;
  const isTooShort = charCount > 0 && charCount < MIN_CHARS;
  const isTooLong = charCount > MAX_CHARS;

  // Get character count color
  const getCharCountColor = () => {
    if (isTooLong) return 'text-red-600';
    if (isTooShort) return 'text-yellow-600';
    if (isValid) return 'text-green-600';
    return 'text-muted-foreground';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{translations.jobDescription.title}</CardTitle>
        <CardDescription>{translations.jobDescription.subtitle}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <label htmlFor="job-description" className="text-sm font-medium">
            {translations.jobDescription.title}
          </label>
          <textarea
            id="job-description"
            placeholder={translations.jobDescription.placeholder}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            className={`min-h-[200px] resize-y w-full p-3 border rounded-md text-sm ${
              isTooShort || isTooLong
                ? 'border-yellow-500 focus:border-yellow-500'
                : 'border-gray-300 focus:border-blue-500'
            } focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50`}
            maxLength={MAX_CHARS + 100} // Allow typing a bit over to show error
          />

          {/* Character count */}
          <div className="flex items-center justify-between text-xs">
            <div className="text-muted-foreground">
              <span className="font-medium">{translations.jobDescription.minChars}</span>
              <span className="mx-2">•</span>
              <span className="font-medium">{translations.jobDescription.maxChars}</span>
            </div>
            <div className={`font-medium ${getCharCountColor()}`}>
              {translations.jobDescription.charCount(charCount, MAX_CHARS)}
            </div>
          </div>

          {/* Validation messages */}
          {isTooShort && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md flex items-start gap-2">
              <svg
                className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-xs text-yellow-700">
                A descrição da vaga precisa ter no mínimo {MIN_CHARS} caracteres. Faltam{' '}
                {MIN_CHARS - charCount} caracteres.
              </p>
            </div>
          )}

          {isTooLong && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md flex items-start gap-2">
              <svg
                className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-xs text-red-600">
                A descrição da vaga ultrapassou o limite de {MAX_CHARS} caracteres. Remova{' '}
                {charCount - MAX_CHARS} caracteres.
              </p>
            </div>
          )}

          {isValid && charCount >= MIN_CHARS + 50 && (
            <div className="text-xs text-green-600">✓ Descrição da vaga válida</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function UploadPage() {
  const router = useRouter();
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Validation
  const isFormValid =
    resumeFile !== null && jobDescription.length >= 50 && jobDescription.length <= 5000;

  const handleFileSelect = (file: File) => {
    setResumeFile(file);
    setError(null);
  };

  const handleFileRemove = () => {
    setResumeFile(null);
  };

  const handleJobDescriptionChange = (value: string) => {
    setJobDescription(value);
  };

  const handleSubmit = async () => {
    if (!isFormValid) return;

    setIsSubmitting(true);
    setError(null);

    try {
      // Get current user
      const supabase = createClient();
      const {
        data: { user },
        error: authError,
      } = await supabase.auth.getUser();

      if (authError || !user) {
        setError(translations.payment.errors.notAuthenticated);
        router.push('/auth/login');
        return;
      }

      // TODO: Implement CV-Match backend API calls
      // 1. Upload resume file to backend
      // const resumeUploadResponse = await api.uploadFile('/api/resumes/upload', resumeFile!);

      // 2. Create job from description
      // const jobResponse = await api.post('/api/jobs/create', {
      //   job_description: jobDescription,
      // });

      // 3. Create Stripe payment intent
      // const paymentResponse = await api.post('/api/payments/create-intent', {
      //   resume_id: resumeId,
      //   job_id: jobId,
      //   user_id: user.id,
      //   user_email: user.email,
      //   amount: 5000, // R$ 50.00
      //   currency: 'brl',
      //   success_url: `${window.location.origin}/payment/success?payment_intent_id={PAYMENT_INTENT_ID}&resume_id=${resumeId}&job_id=${jobId}`,
      //   cancel_url: `${window.location.origin}/upload?cancelled=true`,
      // });

      // For now, just simulate the process
      // TODO: Implement proper logging
      // eslint-disable-next-line no-console
      console.log('Form submitted:', { resumeFile: resumeFile?.name, jobDescription });

      // Redirect to a mock processing page for now
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } catch (err: any) {
      // TODO: Implement proper error logging
      // eslint-disable-next-line no-console
      console.error('Error submitting form:', err);
      setError(err.message || 'Erro ao processar solicitação. Por favor, tente novamente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container max-w-4xl mx-auto py-8 px-4">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">{translations.title}</h1>
        <p className="text-muted-foreground">{translations.subtitle}</p>
      </div>

      {/* Form */}
      <div className="space-y-6">
        {/* Resume Upload */}
        <ResumeUpload
          onFileSelect={handleFileSelect}
          onFileRemove={handleFileRemove}
          disabled={isSubmitting}
        />

        {/* Job Description */}
        <JobDescriptionInput
          value={jobDescription}
          onChange={handleJobDescriptionChange}
          disabled={isSubmitting}
        />

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex flex-col gap-4">
          <Button
            onClick={handleSubmit}
            disabled={!isFormValid || isSubmitting}
            size="lg"
            className="w-full"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                {translations.payment.processing}
              </>
            ) : (
              <>
                {translations.payment.button}
                <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </Button>

          <p className="text-xs text-center text-muted-foreground">
            {translations.payment.securePayment}
          </p>
        </div>
      </div>

      {/* Info Card */}
      <div className="mt-8 p-6 bg-muted/50 rounded-lg border">
        <h3 className="font-semibold mb-2">Como funciona?</h3>
        <ol className="space-y-2 text-sm text-muted-foreground">
          <li>1. Envie seu currículo em PDF ou DOCX</li>
          <li>2. Cole a descrição completa da vaga desejada</li>
          <li>3. Realize o pagamento seguro via Stripe (R$ 50,00)</li>
          <li>4. Aguarde alguns minutos enquanto a IA otimiza seu currículo</li>
          <li>5. Baixe seu currículo otimizado em formato .docx</li>
        </ol>
      </div>
    </div>
  );
}
