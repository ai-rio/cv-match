# Next.js Frontend Development Standards

## Component Structure

Follow this pattern for all React components:

```tsx
'use client'

import { useState, useEffect } from 'react'
import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'

interface ResumeAnalysisProps {
  resumeId: string
  onComplete?: (score: number) => void
  className?: string
}

export default function ResumeAnalysis({
  resumeId,
  onComplete,
  className = ''
}: ResumeAnalysisProps) {
  // Internationalization
  const t = useTranslations('resume')

  // State management
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [score, setScore] = useState<number | null>(null)

  // Effects
  useEffect(() => {
    loadAnalysis()
  }, [resumeId])

  // Event handlers
  const loadAnalysis = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/resumes/${resumeId}/analysis`)
      const data = await response.json()

      setScore(data.score)
      onComplete?.(data.score)
    } catch (err) {
      console.error('Failed to load analysis:', err)
      setError(t('errors.loadFailed'))
    } finally {
      setLoading(false)
    }
  }

  // Render helpers
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  // Loading state
  if (loading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className={`p-4 bg-red-50 border border-red-200 rounded-lg ${className}`}>
        <p className="text-red-600">{error}</p>
        <Button onClick={loadAnalysis} className="mt-2">
          {t('actions.retry')}
        </Button>
      </div>
    )
  }

  // Main render
  return (
    <div className={`p-6 bg-white rounded-lg shadow-sm ${className}`}>
      <h2 className="text-2xl font-bold mb-4">
        {t('analysis.title')}
      </h2>

      {score !== null && (
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            {t('analysis.score')}:
          </span>
          <span className={`text-4xl font-bold ${getScoreColor(score)}`}>
            {score.toFixed(1)}
          </span>
        </div>
      )}
    </div>
  )
}
```

## App Router Structure

Use Next.js 13+ App Router patterns:

### Page Structure
```tsx
// app/dashboard/page.tsx
import { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import DashboardContent from '@/components/dashboard/DashboardContent'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('dashboard')

  return {
    title: t('meta.title'),
    description: t('meta.description')
  }
}

export default async function DashboardPage() {
  return (
    <div className="container mx-auto py-8">
      <DashboardContent />
    </div>
  )
}
```

### Layout Structure
```tsx
// app/dashboard/layout.tsx
import { ReactNode } from 'react'
import Sidebar from '@/components/dashboard/Sidebar'
import Header from '@/components/dashboard/Header'

interface DashboardLayoutProps {
  children: ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1">
        <Header />
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
```

### Loading State
```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="flex flex-col items-center gap-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
        <p className="text-gray-600">Carregando...</p>
      </div>
    </div>
  )
}
```

### Error Boundary
```tsx
// app/dashboard/error.tsx
'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Dashboard error:', error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold mb-4">Algo deu errado!</h2>
      <p className="text-gray-600 mb-6">
        Desculpe, ocorreu um erro inesperado.
      </p>
      <Button onClick={reset}>
        Tentar novamente
      </Button>
    </div>
  )
}
```

## Styling with Tailwind CSS

Follow Tailwind best practices:

### Semantic Grouping
```tsx
<div className="
  // Layout
  flex items-center justify-between
  // Spacing
  p-4 gap-3
  // Appearance
  bg-white rounded-lg shadow-sm
  // States
  hover:shadow-md hover:bg-gray-50
  transition-all duration-200
">
  {/* Content */}
</div>
```

### Responsive Design
```tsx
<div className="
  // Mobile first
  grid grid-cols-1 gap-4
  // Tablet
  md:grid-cols-2 md:gap-6
  // Desktop
  lg:grid-cols-3 lg:gap-8
  // Wide screens
  xl:grid-cols-4
">
  {/* Grid items */}
</div>
```

### Conditional Styles
```tsx
import { cn } from '@/lib/utils'

<div className={cn(
  // Base styles
  "p-4 rounded-lg border",
  // Conditional styles
  isActive && "bg-blue-50 border-blue-500",
  isError && "bg-red-50 border-red-500",
  // Custom className prop
  className
)}>
  {/* Content */}
</div>
```

## Internationalization (i18n)

Always use next-intl for all user-facing text:

### In Components
```tsx
'use client'

import { useTranslations } from 'next-intl'

export default function PricingCard() {
  const t = useTranslations('pricing')

  return (
    <div className="p-6 bg-white rounded-lg">
      <h3 className="text-xl font-bold">{t('flex.title')}</h3>
      <p className="text-gray-600">{t('flex.description')}</p>

      <div className="mt-4">
        <span className="text-3xl font-bold">
          {t('flex.price', { amount: 59.90 })}
        </span>
      </div>

      <button className="mt-4 w-full bg-blue-500 text-white rounded-lg py-2">
        {t('flex.cta')}
      </button>
    </div>
  )
}
```

### In Server Components
```tsx
import { getTranslations } from 'next-intl/server'

export default async function PricingPage() {
  const t = await getTranslations('pricing')

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('subtitle')}</p>
    </div>
  )
}
```

### Translation Files
```json
// messages/pt-br.json
{
  "pricing": {
    "title": "Planos e Preços",
    "flex": {
      "title": "Flex 25",
      "description": "Para quem busca emprego ocasionalmente",
      "price": "R$ {amount, number, ::currency/BRL}",
      "cta": "Comprar Créditos"
    }
  },
  "errors": {
    "loadFailed": "Falha ao carregar dados",
    "networkError": "Erro de conexão. Verifique sua internet."
  }
}
```

## State Management

Use appropriate state management patterns:

### Local State
```tsx
'use client'

import { useState } from 'react'

export default function ResumeUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    try {
      // Upload logic
    } finally {
      setUploading(false)
    }
  }

  return <div>{/* Component */}</div>
}
```

### URL State (Shareable)
```tsx
'use client'

import { useSearchParams, useRouter } from 'next/navigation'

export default function JobList() {
  const searchParams = useSearchParams()
  const router = useRouter()

  const page = parseInt(searchParams.get('page') || '1')

  const changePage = (newPage: number) => {
    const params = new URLSearchParams(searchParams)
    params.set('page', newPage.toString())
    router.push(`?${params.toString()}`)
  }

  return <div>{/* Component */}</div>
}
```

### Server State (with SWR)
```tsx
'use client'

import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export default function Dashboard() {
  const { data, error, isLoading, mutate } = useSWR(
    '/api/dashboard/stats',
    fetcher,
    {
      refreshInterval: 60000, // Refresh every minute
      revalidateOnFocus: true
    }
  )

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading stats</div>

  return (
    <div>
      <h2>Credits: {data.credits}</h2>
      <button onClick={() => mutate()}>Refresh</button>
    </div>
  )
}
```

## API Integration

Use consistent patterns for API calls:

### API Client
```typescript
// lib/api/client.ts
import { getSession } from '@/lib/auth'

export class APIClient {
  private baseURL: string

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }

  private async getHeaders(): Promise<HeadersInit> {
    const session = await getSession()

    return {
      'Content-Type': 'application/json',
      ...(session?.access_token && {
        Authorization: `Bearer ${session.access_token}`
      })
    }
  }

  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'GET',
      headers: await this.getHeaders()
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }

    return response.json()
  }

  async post<T>(path: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseURL}${path}`, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }

    return response.json()
  }
}

export const apiClient = new APIClient()
```

### Using API Client
```tsx
'use client'

import { useState } from 'react'
import { apiClient } from '@/lib/api/client'
import { useToast } from '@/components/ui/use-toast'

export default function ResumeForm() {
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async (data: FormData) => {
    setLoading(true)

    try {
      const result = await apiClient.post('/api/v1/resumes/analyze', {
        resume_text: data.get('resume'),
        job_description: data.get('job')
      })

      toast({
        title: 'Sucesso!',
        description: 'Análise concluída com sucesso.'
      })

      // Handle success
    } catch (error) {
      console.error('Analysis failed:', error)

      toast({
        variant: 'destructive',
        title: 'Erro',
        description: 'Falha ao analisar currículo. Tente novamente.'
      })
    } finally {
      setLoading(false)
    }
  }

  return <form>{/* Form fields */}</form>
}
```

## Form Handling

Use react-hook-form with Zod validation:

```tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Form, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'

const formSchema = z.object({
  name: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
  email: z.string().email('Email inválido'),
  resume: z.instanceof(File).refine(
    (file) => file.size <= 5000000,
    'Arquivo deve ter no máximo 5MB'
  )
})

type FormData = z.infer<typeof formSchema>

export default function ResumeUploadForm() {
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      email: ''
    }
  })

  const onSubmit = async (data: FormData) => {
    console.log('Form data:', data)
    // Handle submission
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nome</FormLabel>
              <Input {...field} placeholder="Seu nome completo" />
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <Input {...field} type="email" placeholder="seu@email.com" />
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? 'Enviando...' : 'Enviar'}
        </Button>
      </form>
    </Form>
  )
}
```

## Performance Optimization

### Image Optimization
```tsx
import Image from 'next/image'

<Image
  src="/logo.png"
  alt="CV-Match Logo"
  width={200}
  height={50}
  priority // For above-the-fold images
/>
```

### Dynamic Imports
```tsx
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(
  () => import('@/components/HeavyComponent'),
  {
    loading: () => <div>Loading...</div>,
    ssr: false // Disable SSR if not needed
  }
)
```

### Memoization
```tsx
import { useMemo, useCallback } from 'react'

export default function ExpensiveComponent({ data }: Props) {
  // Memoize expensive calculations
  const processedData = useMemo(() => {
    return data.map(item => /* expensive operation */)
  }, [data])

  // Memoize callbacks
  const handleClick = useCallback(() => {
    console.log('Clicked')
  }, [])

  return <div>{/* Component */}</div>
}
```

## Testing

Write tests for components:

```tsx
// __tests__/components/ResumeAnalysis.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ResumeAnalysis from '@/components/ResumeAnalysis'

describe('ResumeAnalysis', () => {
  it('renders loading state', () => {
    render(<ResumeAnalysis resumeId="123" />)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('displays score after loading', async () => {
    render(<ResumeAnalysis resumeId="123" />)

    await waitFor(() => {
      expect(screen.getByText(/85\.5/)).toBeInTheDocument()
    })
  })

  it('handles retry on error', async () => {
    const user = userEvent.setup()
    render(<ResumeAnalysis resumeId="invalid" />)

    await waitFor(() => {
      expect(screen.getByText(/erro/i)).toBeInTheDocument()
    })

    const retryButton = screen.getByRole('button', { name: /tentar novamente/i })
    await user.click(retryButton)

    // Assert retry behavior
  })
})
```

---

**Key Principles**:
1. Always use TypeScript with proper interfaces
2. Use next-intl for all user-facing text (PT-BR support)
3. Follow App Router conventions
4. Use Tailwind CSS for styling
5. Implement proper loading and error states
6. Use SWR for server state management
7. Optimize images and heavy components
8. Write tests for critical functionality
