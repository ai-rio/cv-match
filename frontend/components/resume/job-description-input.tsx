'use client';

import { Briefcase, FileText, Link2, Upload } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

interface JobDescriptionInputProps {
  onSubmit: (data: { text?: string; file?: File; url?: string }) => void;
  disabled?: boolean;
  className?: string;
}

const ACCEPTED_FILE_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
];

export function JobDescriptionInput({
  onSubmit,
  disabled = false,
  className,
}: JobDescriptionInputProps) {
  const [inputMethod, setInputMethod] = useState<'text' | 'file' | 'url'>('text');
  const [jobText, setJobText] = useState('');
  const [jobFile, setJobFile] = useState<File | null>(null);
  const [jobUrl, setJobUrl] = useState('');
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    if (!ACCEPTED_FILE_TYPES.includes(file.type)) {
      return 'Tipo de arquivo inválido. Aceitamos PDF, DOCX e TXT.';
    }
    if (file.size > 2 * 1024 * 1024) {
      return 'Arquivo muito grande. O tamanho máximo é 2MB.';
    }
    return null;
  };

  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        return;
      }
      setJobFile(file);
      setError(null);
    }
  };

  const validateUrl = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = () => {
    setError(null);

    switch (inputMethod) {
      case 'text':
        if (!jobText.trim()) {
          setError('Por favor, insira a descrição da vaga.');
          return;
        }
        onSubmit({ text: jobText });
        break;

      case 'file':
        if (!jobFile) {
          setError('Por favor, selecione um arquivo.');
          return;
        }
        onSubmit({ file: jobFile });
        break;

      case 'url':
        if (!jobUrl.trim()) {
          setError('Por favor, insira a URL da vaga.');
          return;
        }
        if (!validateUrl(jobUrl)) {
          setError('Por favor, insira uma URL válida.');
          return;
        }
        onSubmit({ url: jobUrl });
        break;
    }
  };

  const handleReset = () => {
    setJobText('');
    setJobFile(null);
    setJobUrl('');
    setError(null);
  };

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Briefcase className="h-5 w-5" />
          <span>Descrição da Vaga</span>
        </CardTitle>
        <CardDescription>
          Adicione a descrição da vaga para analisar a compatibilidade com seu currículo.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Input Method Selection */}
        <div className="flex flex-col space-y-2">
          <Label>Como deseja adicionar a descrição da vaga?</Label>
          <div className="grid grid-cols-3 gap-2">
            <Button
              variant={inputMethod === 'text' ? 'default' : 'outline'}
              onClick={() => setInputMethod('text')}
              disabled={disabled}
              className="flex items-center space-x-2"
            >
              <FileText className="h-4 w-4" />
              <span>Texto</span>
            </Button>
            <Button
              variant={inputMethod === 'file' ? 'default' : 'outline'}
              onClick={() => setInputMethod('file')}
              disabled={disabled}
              className="flex items-center space-x-2"
            >
              <Upload className="h-4 w-4" />
              <span>Arquivo</span>
            </Button>
            <Button
              variant={inputMethod === 'url' ? 'default' : 'outline'}
              onClick={() => setInputMethod('url')}
              disabled={disabled}
              className="flex items-center space-x-2"
            >
              <Link2 className="h-4 w-4" />
              <span>URL</span>
            </Button>
          </div>
        </div>

        {/* Text Input */}
        {inputMethod === 'text' && (
          <div className="space-y-2">
            <Label htmlFor="job-text">Descrição da Vaga</Label>
            <Textarea
              id="job-text"
              placeholder="Cole aqui a descrição completa da vaga..."
              value={jobText}
              onChange={(e) => setJobText(e.target.value)}
              disabled={disabled}
              rows={8}
              className="resize-none"
            />
          </div>
        )}

        {/* File Input */}
        {inputMethod === 'file' && (
          <div className="space-y-4">
            <div className="border-2 border-dashed rounded-lg p-6 text-center">
              <div className="flex flex-col items-center space-y-2">
                <Upload className="h-8 w-8 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  Arraste um arquivo aqui ou clique para selecionar
                </p>
                <p className="text-xs text-muted-foreground">PDF, DOCX ou TXT (máx. 2MB)</p>
                <input
                  type="file"
                  accept={ACCEPTED_FILE_TYPES.join(',')}
                  onChange={handleFileInput}
                  disabled={disabled}
                  className="hidden"
                  id="job-file-input"
                />
                <Button asChild variant="outline" disabled={disabled}>
                  <label htmlFor="job-file-input" className="cursor-pointer">
                    Selecionar Arquivo
                  </label>
                </Button>
              </div>
            </div>

            {jobFile && (
              <div className="flex items-center space-x-2 p-3 bg-muted rounded-lg">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm truncate flex-1">{jobFile.name}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setJobFile(null)}
                  disabled={disabled}
                >
                  Remover
                </Button>
              </div>
            )}
          </div>
        )}

        {/* URL Input */}
        {inputMethod === 'url' && (
          <div className="space-y-2">
            <Label htmlFor="job-url">URL da Vaga</Label>
            <Input
              id="job-url"
              type="url"
              placeholder="https://exemplo.com/vaga"
              value={jobUrl}
              onChange={(e) => setJobUrl(e.target.value)}
              disabled={disabled}
            />
            <p className="text-xs text-muted-foreground">
              Cole o link da vaga de sites como LinkedIn, Glassdoor, etc.
            </p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-2">
          <Button onClick={handleSubmit} disabled={disabled} className="flex-1">
            Analisar Compatibilidade
          </Button>
          <Button variant="outline" onClick={handleReset} disabled={disabled}>
            Limpar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
