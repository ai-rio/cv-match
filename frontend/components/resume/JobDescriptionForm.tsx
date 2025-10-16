'use client';

import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface JobDescriptionData {
  jobTitle: string;
  company: string;
  description: string;
}

interface JobDescriptionFormProps {
  onJobDescriptionSubmit: (data: JobDescriptionData) => void;
  isDisabled: boolean;
}

// Portuguese translations
const translations = {
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
  },
  errors: {
    jobTitleRequired: 'Cargo é obrigatório',
    companyRequired: 'Empresa é obrigatória',
    descriptionTooShort: 'Descrição da vaga deve ter pelo menos 50 caracteres',
    descriptionTooLong: 'Descrição da vaga não pode exceder 5000 caracteres',
  },
};

export function JobDescriptionForm({
  onJobDescriptionSubmit,
  isDisabled,
}: JobDescriptionFormProps) {
  const [jobTitle, setJobTitle] = useState('');
  const [company, setCompany] = useState('');
  const [description, setDescription] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!jobTitle.trim()) {
      newErrors.jobTitle = translations.errors.jobTitleRequired;
    }

    if (!company.trim()) {
      newErrors.company = translations.errors.companyRequired;
    }

    if (description.length < 50) {
      newErrors.description = translations.errors.descriptionTooShort;
    }

    if (description.length > 5000) {
      newErrors.description = translations.errors.descriptionTooLong;
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
