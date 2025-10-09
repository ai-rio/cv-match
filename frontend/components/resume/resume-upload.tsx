'use client';

import { AlertCircle, CheckCircle2, FileText, Upload, X } from 'lucide-react';
import { useCallback, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface ResumeUploadProps {
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  disabled?: boolean;
  className?: string;
}

const MAX_FILE_SIZE = 4 * 1024 * 1024; // 4MB for CV-Match (increased from 2MB)
const ACCEPTED_FILE_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
  'text/plain',
];

export function ResumeUpload({
  onFileSelect,
  onFileRemove,
  disabled = false,
  className,
}: ResumeUploadProps) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const validateFile = (file: File): string | null => {
    if (!ACCEPTED_FILE_TYPES.includes(file.type)) {
      return 'Tipo de arquivo inválido. Aceitamos PDF, DOC, DOCX e TXT.';
    }
    if (file.size > MAX_FILE_SIZE) {
      return 'Arquivo muito grande. O tamanho máximo é 4MB.';
    }
    return null;
  };

  const handleFile = useCallback(
    (file: File) => {
      setError(null);

      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        return;
      }

      setUploadedFile(file);
      setUploadProgress(0);

      // Simulate upload progress
      const interval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            onFileSelect(file);
            return 100;
          }
          return prev + 10;
        });
      }, 100);
    },
    [onFileSelect]
  );

  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleRemove = () => {
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
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <CardTitle>Enviar Currículo</CardTitle>
        <CardDescription>
          Envie seu currículo em formato PDF, DOC, DOCX ou TXT. Tamanho máximo: 4MB.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!uploadedFile ? (
          <div
            className={cn(
              'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
              isDragging
                ? 'border-primary bg-primary/5'
                : 'border-muted-foreground/25 hover:border-muted-foreground/50',
              disabled && 'opacity-50 cursor-not-allowed'
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center space-y-4">
              <div className="p-4 bg-muted rounded-full">
                <Upload className="h-8 w-8 text-muted-foreground" />
              </div>
              <div>
                <p className="text-lg font-medium">Arraste seu currículo aqui</p>
                <p className="text-sm text-muted-foreground">ou clique para selecionar</p>
              </div>
              <input
                type="file"
                accept={ACCEPTED_FILE_TYPES.join(',')}
                onChange={handleFileInput}
                disabled={disabled}
                className="hidden"
                id="resume-upload"
              />
              <Button asChild disabled={disabled}>
                <label htmlFor="resume-upload" className="cursor-pointer">
                  Selecionar Arquivo
                </label>
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-4 border rounded-lg">
              <div className="p-2 bg-primary/10 rounded">
                <FileText className="h-6 w-6 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{uploadedFile.name}</p>
                <p className="text-xs text-muted-foreground">{formatFileSize(uploadedFile.size)}</p>
              </div>
              <Button variant="ghost" size="icon" onClick={handleRemove} disabled={disabled}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            {uploadProgress < 100 && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Enviando...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <Progress value={uploadProgress} />
              </div>
            )}

            {uploadProgress === 100 && (
              <div className="flex items-center space-x-2 text-green-600">
                <CheckCircle2 className="h-4 w-4" />
                <span className="text-sm">Currículo enviado com sucesso!</span>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="flex items-center space-x-2 text-destructive mt-4">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">{error}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
