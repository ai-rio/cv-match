'use client';

import { AlertCircle, CheckCircle, FileText } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';

interface ResumeUploadProps {
  onUploadSuccess: (resumeId: string, fileName: string) => void;
}

// Portuguese translations
const translations = {
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
  },
};

export function ResumeUpload({ onUploadSuccess }: ResumeUploadProps) {
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

  const handleFile = async (file: File) => {
    setError(null);
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setUploadProgress(0);
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        throw new Error('Você precisa estar autenticado');
      }

      const formData = new FormData();
      formData.append('file', file);

      const xhr = new XMLHttpRequest();
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(progress);
        }
      });

      return new Promise<void>((resolve, reject) => {
        xhr.onload = async () => {
          if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            setUploadedFile(file);
            onUploadSuccess(data.resume_id, file.name);
            resolve();
          } else {
            const error = JSON.parse(xhr.responseText);
            reject(new Error(error.detail || 'Erro ao enviar currículo'));
          }
        };

        xhr.onerror = () => {
          reject(new Error('Erro de conexão ao enviar arquivo'));
        };

        xhr.open('POST', `${API_URL}/api/resumes/upload`);
        xhr.setRequestHeader('Authorization', `Bearer ${session.access_token}`);
        xhr.send(formData);
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao enviar arquivo';
      setError(errorMessage);
      setUploadProgress(0);
    }
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
    <Card>
      <CardHeader>
        <CardTitle>{translations.upload.title}</CardTitle>
        <CardDescription>{translations.upload.subtitle}</CardDescription>
      </CardHeader>
      <CardContent>
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
      </CardContent>
    </Card>
  );
}
