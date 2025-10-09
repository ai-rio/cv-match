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
import { useCallback, useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';

// Mock translation object - will be replaced with next-intl later
const translations = {
  title: 'AI Resume Optimization',
  subtitle:
    'Transform your resume to perfectly match your target job description with AI-powered optimization',
  steps: {
    upload: 'Upload Resume',
    jobDetails: 'Job Details',
    payment: 'Payment',
    processing: 'Processing',
    results: 'Results',
  },
  upload: {
    title: 'Upload Your Resume',
    subtitle: 'Upload your current resume in PDF or DOCX format to begin the optimization process',
    dragDrop: 'Drag and drop your resume here',
    formats: 'PDF or DOCX (max 2MB)',
    button: 'Choose File',
    uploading: 'Uploading...',
    invalidType: 'Invalid file type. Please use PDF or DOCX.',
    tooLarge: 'File too large. Maximum size is 2MB.',
    charCount: (current: number, max: number) => `${current}/${max} characters`,
  },
  jobDescription: {
    title: 'Job Details',
    subtitle: 'Enter the details of the job you want to apply for',
    jobTitle: 'Job Title',
    company: 'Company',
    description: 'Job Description',
    jobTitlePlaceholder: 'e.g. Senior Software Engineer',
    companyPlaceholder: 'e.g. Google',
    descriptionPlaceholder: 'Paste the complete job description here...',
    minChars: 'Minimum: 50 characters',
    maxChars: 'Maximum: 5000 characters',
    charCount: (current: number, max: number) => `${current}/${max}`,
    submit: 'Continue to Payment',
    startOptimization: 'Start Optimization',
  },
  payment: {
    title: 'Payment',
    subtitle: 'Complete your purchase to unlock AI resume optimization',
    orderSummary: 'Order Summary',
    resume: 'Resume:',
    position: 'Position:',
    total: 'Total:',
    processing: 'Processing payment...',
    securePayment: 'Secure payment processed by Stripe',
  },
  processing: {
    title: 'Optimizing Your Resume',
    subtitle: 'Our AI is analyzing and optimizing your resume. This usually takes 2-3 minutes.',
    extracting: 'Extracting text from resume',
    analyzing: 'Analyzing job requirements',
    optimizing: 'AI-powered optimization in progress',
    generating: 'Generating optimized document',
  },
  results: {
    title: 'Your Optimized Resume',
    subtitle: 'Your resume has been optimized and is ready for download',
    download: 'Download Optimized Resume',
    viewOptimized: 'View Optimized Content',
    matchScore: 'Match Score',
    improvements: 'Key Improvements',
    keywords: 'Keywords Added',
    downloadAnother: 'Optimize Another Resume',
    goToDashboard: 'Go to Dashboard',
  },
  errors: {
    notAuthenticated: 'You must be logged in to continue.',
    paymentFailed: 'Payment failed. Please try again.',
    optimizationFailed: 'Optimization failed. Please try again.',
    downloadFailed: 'Download failed. Please try again.',
  },
  common: {
    loading: 'Loading...',
    error: 'Error',
    back: 'Back',
    next: 'Next',
    startOver: 'Start Over',
    tryAgain: 'Try Again',
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
  id: 'ai-optimization',
  name: 'AI Resume Optimization',
  price: 1999, // $19.99 in cents
  currency: 'USD',
  interval: 'lifetime' as const,
  description: 'One-time AI-powered resume optimization to match your target job description',
  features: [
    'AI-powered resume optimization',
    'ATS-friendly formatting',
    'Keyword optimization',
    'Professional enhancement',
    'Side-by-side comparison',
    'Download optimized .docx file',
    'Results in 2-3 minutes',
  ],
  isFree: false,
};

type WorkflowStep = 'upload' | 'job-details' | 'payment' | 'processing' | 'results';

export default function OptimizePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const resumeId = searchParams.get('resume_id');

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
      setError('Missing resume or job description data');
      return;
    }

    try {
      // TODO: Replace with actual CV-Match API call
      // const response = await fetch('/api/optimizations/start', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     resume_id: resumeData.id,
      //     job_description: jobDescription.description,
      //     job_title: jobDescription.jobTitle,
      //     company: jobDescription.company,
      //   }),
      // });

      // if (!response.ok) {
      //   throw new Error('Failed to start optimization');
      // }

      // const data = await response.json();
      // setOptimizationId(data.optimization_id);

      // For now, simulate the process
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setOptimizationId('mock-optimization-id');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start optimization');
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

        // TODO: Check if user can optimize (has credits or is pro)
        // For now, proceed to payment
        setCurrentStep('payment');
      } catch (error) {
        setError(error instanceof Error ? error.message : 'Failed to check usage limits');
      }
    },
    [router]
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
      // TODO: Replace with actual CV-Match API call
      // const response = await fetch(`/api/optimizations/${optimizationId}/download`);
      // if (!response.ok) throw new Error('Download failed');

      // const blob = await response.blob();
      // const url = window.URL.createObjectURL(blob);
      // const a = document.createElement('a');
      // a.href = url;
      // a.download = `optimized-resume-${Date.now()}.docx`;
      // document.body.appendChild(a);
      // a.click();
      // document.body.removeChild(a);
      // window.URL.revokeObjectURL(url);

      // For now, simulate the download
      const blob = new Blob(['Mock optimized resume content'], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `optimized-resume-${Date.now()}.docx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed');
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
              <Card className="text-center">
                <CardHeader>
                  <CardTitle className="flex items-center justify-center gap-2">
                    <FileText className="h-5 w-5" />
                    {translations.upload.title}
                  </CardTitle>
                  <CardDescription>{translations.upload.subtitle}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="max-w-2xl mx-auto">
                    <ResumeUploadComponent
                      onUploadSuccess={(resumeId, fileName) => {
                        handleResumeUploaded({ id: resumeId, name: fileName });
                      }}
                    />
                  </div>
                </CardContent>
              </Card>

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
                      <span>${(OPTIMIZATION_TIER.price / 100).toFixed(2)} USD</span>
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

// Helper components for the optimization workflow

function ResumeUploadComponent({
  onUploadSuccess,
}: {
  onUploadSuccess: (resumeId: string, fileName: string) => void;
}) {
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
      onUploadSuccess('mock-resume-id', file.name);
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

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}
          hover:border-blue-500 hover:bg-blue-50
        `}
      >
        <input
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleFileChange}
          className="hidden"
          id="resume-file-input-optimize"
        />
        <label htmlFor="resume-file-input-optimize" className="cursor-pointer">
          <div className="flex flex-col items-center gap-4">
            <svg
              className="w-12 h-12 text-gray-400"
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
              <p className="text-xs text-gray-500 mt-1">{translations.upload.formats}</p>
            </div>
            <Button type="button" variant="outline" size="sm">
              {translations.upload.button}
            </Button>
          </div>
        </label>
      </div>

      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="mt-4">
          <p className="text-sm text-gray-500 mb-2">{translations.upload.uploading}</p>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {uploadedFile && (
        <div className="border rounded-lg p-4 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <FileText className="w-10 h-10 text-blue-600" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{uploadedFile.name}</p>
                <p className="text-xs text-gray-500">{formatFileSize(uploadedFile.size)}</p>
              </div>
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function JobDescriptionForm({
  onJobDescriptionSubmit,
  isDisabled,
}: {
  onJobDescriptionSubmit: (data: JobDescriptionData) => void;
  isDisabled: boolean;
}) {
  const [jobTitle, setJobTitle] = useState('');
  const [company, setCompany] = useState('');
  const [description, setDescription] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!jobTitle.trim()) {
      newErrors.jobTitle = 'Job title is required';
    }

    if (!company.trim()) {
      newErrors.company = 'Company is required';
    }

    if (description.length < 50) {
      newErrors.description = 'Job description must be at least 50 characters';
    }

    if (description.length > 5000) {
      newErrors.description = 'Job description cannot exceed 5000 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onJobDescriptionSubmit({
        jobTitle: jobTitle.trim(),
        company: company.trim(),
        description: description.trim(),
      });
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{translations.jobDescription.title}</CardTitle>
        <CardDescription>{translations.jobDescription.subtitle}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            {translations.jobDescription.jobTitle}
          </label>
          <input
            type="text"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            placeholder={translations.jobDescription.jobTitlePlaceholder}
            className="w-full p-2 border rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            disabled={isDisabled}
          />
          {errors.jobTitle && <p className="text-sm text-red-600 mt-1">{errors.jobTitle}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {translations.jobDescription.company}
          </label>
          <input
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder={translations.jobDescription.companyPlaceholder}
            className="w-full p-2 border rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            disabled={isDisabled}
          />
          {errors.company && <p className="text-sm text-red-600 mt-1">{errors.company}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {translations.jobDescription.description}
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder={translations.jobDescription.descriptionPlaceholder}
            className="w-full p-3 border rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500 min-h-[150px] resize-y"
            disabled={isDisabled}
            maxLength={5000}
          />
          <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
            <span>
              {translations.jobDescription.minChars} • {translations.jobDescription.maxChars}
            </span>
            <span
              className={
                description.length < 50
                  ? 'text-yellow-600'
                  : description.length > 5000
                    ? 'text-red-600'
                    : 'text-green-600'
              }
            >
              {translations.jobDescription.charCount(description.length, 5000)}
            </span>
          </div>
          {errors.description && <p className="text-sm text-red-600 mt-1">{errors.description}</p>}
        </div>

        <Button onClick={handleSubmit} disabled={isDisabled} className="w-full">
          {translations.jobDescription.submit}
        </Button>
      </CardContent>
    </Card>
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
      // TODO: Replace with actual Stripe integration
      await new Promise((resolve) => setTimeout(resolve, 2000));
      onSuccess();
    } catch (error) {
      // Payment error will be handled by the parent component
      console.error('Payment failed:', error);
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
          <div className="text-3xl font-bold mb-6">${(tier.price / 100).toFixed(2)}</div>

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
              `Pay $${(tier.price / 100).toFixed(2)} USD`
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
