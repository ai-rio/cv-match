# Agent Prompt: Frontend Integration

**Agent**: frontend-specialist
**Phase**: 4 - Frontend (Parallel with Testing)
**Priority**: P0
**Estimated Time**: 1.5 hours
**Dependencies**: Phase 3 complete (API endpoints must exist)

---

## 🎯 Mission

Update the frontend optimize page to use real API endpoints instead of mocks, integrate authentication, and ensure the complete user workflow works end-to-end.

---

## 📋 Tasks

### Task 1: Update Optimize Page with Real APIs (45 min)

**File**: `frontend/app/optimize/page.tsx`

**Actions**:

1. Update the file to use real API calls:

   ```typescript
   // frontend/app/optimize/page.tsx

   'use client';

   import { useState } from 'react';
   import { useRouter } from 'next/navigation';
   import { createClient } from '@/lib/supabase/client';

   export default function OptimizePage() {
     const [resumeFile, setResumeFile] = useState<File | null>(null);
     const [jobDescription, setJobDescription] = useState({
       title: '',
       company: '',
       description: ''
     });
     const [isUploading, setIsUploading] = useState(false);
     const [isOptimizing, setIsOptimizing] = useState(false);
     const [error, setError] = useState<string | null>(null);
     const router = useRouter();

     const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

     // Get Supabase session for auth token
     const getAuthToken = async () => {
       const supabase = createClient();
       const { data: { session } } = await supabase.auth.getSession();
       return session?.access_token;
     };

     // Step 1: Upload Resume
     const handleResumeUpload = async (file: File) => {
       setIsUploading(true);
       setError(null);

       try {
         const token = await getAuthToken();
         if (!token) {
           throw new Error('Você precisa estar autenticado');
         }

         const formData = new FormData();
         formData.append('file', file);

         const response = await fetch(`${API_URL}/api/resumes/upload`, {
           method: 'POST',
           headers: {
             'Authorization': `Bearer ${token}`
           },
           body: formData
         });

         if (!response.ok) {
           const error = await response.json();
           throw new Error(error.detail || 'Erro ao enviar currículo');
         }

         const data = await response.json();
         return data.resume_id;

       } catch (err: any) {
         setError(err.message);
         throw err;
       } finally {
         setIsUploading(false);
       }
     };

     // Step 2: Start Optimization
     const handleStartOptimization = async (resumeId: string) => {
       setIsOptimizing(true);
       setError(null);

       try {
         const token = await getAuthToken();
         if (!token) {
           throw new Error('Você precisa estar autenticado');
         }

         const response = await fetch(`${API_URL}/api/optimizations/start`, {
           method: 'POST',
           headers: {
             'Authorization': `Bearer ${token}`,
             'Content-Type': 'application/json'
           },
           body: JSON.stringify({
             resume_id: resumeId,
             job_title: jobDescription.title,
             company: jobDescription.company,
             job_description: jobDescription.description
           })
         });

         if (!response.ok) {
           const error = await response.json();
           throw new Error(error.detail || 'Erro ao iniciar otimização');
         }

         const data = await response.json();
         return data.optimization_id;

       } catch (err: any) {
         setError(err.message);
         throw err;
       } finally {
         setIsOptimizing(false);
       }
     };

     // Step 3: Handle Form Submit
     const handleSubmit = async (e: React.FormEvent) => {
       e.preventDefault();

       if (!resumeFile) {
         setError('Por favor, envie seu currículo');
         return;
       }

       if (!jobDescription.title || !jobDescription.company || !jobDescription.description) {
         setError('Por favor, preencha todos os campos da vaga');
         return;
       }

       try {
         // Upload resume
         const resumeId = await handleResumeUpload(resumeFile);

         // Start optimization
         const optimizationId = await handleStartOptimization(resumeId);

         // Redirect to results page
         router.push(`/results/${optimizationId}`);

       } catch (err) {
         console.error('Optimization error:', err);
       }
     };

     return (
       <div className="container mx-auto px-4 py-8">
         <h1 className="text-3xl font-bold mb-8">Otimize seu Currículo</h1>

         {error && (
           <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
             {error}
           </div>
         )}

         <form onSubmit={handleSubmit} className="space-y-6">
           {/* Resume Upload */}
           <div>
             <label className="block text-sm font-medium mb-2">
               Currículo (PDF ou DOCX)
             </label>
             <input
               type="file"
               accept=".pdf,.docx"
               onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
               className="block w-full"
               disabled={isUploading || isOptimizing}
             />
           </div>

           {/* Job Title */}
           <div>
             <label className="block text-sm font-medium mb-2">
               Cargo
             </label>
             <input
               type="text"
               value={jobDescription.title}
               onChange={(e) => setJobDescription({...jobDescription, title: e.target.value})}
               className="block w-full px-3 py-2 border rounded"
               placeholder="Ex: Desenvolvedor Python Sênior"
               disabled={isUploading || isOptimizing}
             />
           </div>

           {/* Company */}
           <div>
             <label className="block text-sm font-medium mb-2">
               Empresa
             </label>
             <input
               type="text"
               value={jobDescription.company}
               onChange={(e) => setJobDescription({...jobDescription, company: e.target.value})}
               className="block w-full px-3 py-2 border rounded"
               placeholder="Ex: TechCorp Brasil"
               disabled={isUploading || isOptimizing}
             />
           </div>

           {/* Job Description */}
           <div>
             <label className="block text-sm font-medium mb-2">
               Descrição da Vaga
             </label>
             <textarea
               value={jobDescription.description}
               onChange={(e) => setJobDescription({...jobDescription, description: e.target.value})}
               className="block w-full px-3 py-2 border rounded"
               rows={6}
               placeholder="Cole aqui a descrição completa da vaga..."
               disabled={isUploading || isOptimizing}
             />
           </div>

           {/* Submit Button */}
           <button
             type="submit"
             disabled={isUploading || isOptimizing}
             className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 disabled:bg-gray-400"
           >
             {isUploading && 'Enviando currículo...'}
             {isOptimizing && 'Otimizando...'}
             {!isUploading && !isOptimizing && 'Otimizar Currículo'}
           </button>
         </form>
       </div>
     );
   }
   ```

**Success Criteria**:

- [x] File updated with real API calls
- [x] Authentication integrated
- [x] Error handling implemented
- [x] Loading states shown
- [x] Form validation working

---

### Task 2: Update Results Page (30 min)

**File**: `frontend/app/results/[id]/page.tsx`

**Actions**:

1. Update to fetch real optimization results:

   ```typescript
   // frontend/app/results/[id]/page.tsx

   'use client';

   import { useEffect, useState } from 'react';
   import { useParams } from 'next/navigation';
   import { createClient } from '@/lib/supabase/client';

   interface OptimizationResult {
     id: string;
     match_score: number;
     improvements: Array<{suggestion: string}>;
     keywords: string[];
     strengths: string[];
     weaknesses: string[];
     status: string;
   }

   export default function ResultsPage() {
     const params = useParams();
     const optimizationId = params.id as string;
     const [result, setResult] = useState<OptimizationResult | null>(null);
     const [loading, setLoading] = useState(true);
     const [error, setError] = useState<string | null>(null);

     const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

     useEffect(() => {
       const fetchResult = async () => {
         try {
           const supabase = createClient();
           const { data: { session } } = await supabase.auth.getSession();

           if (!session) {
             throw new Error('Não autenticado');
           }

           const response = await fetch(
             `${API_URL}/api/optimizations/${optimizationId}`,
             {
               headers: {
                 'Authorization': `Bearer ${session.access_token}`
               }
             }
           );

           if (!response.ok) {
             throw new Error('Erro ao carregar resultados');
           }

           const data = await response.json();
           setResult(data);

           // Poll if still processing
           if (data.status === 'processing' || data.status === 'pending_payment') {
             setTimeout(fetchResult, 3000); // Poll every 3 seconds
           }

         } catch (err: any) {
           setError(err.message);
         } finally {
           setLoading(false);
         }
       };

       fetchResult();
     }, [optimizationId]);

     if (loading) {
       return (
         <div className="container mx-auto px-4 py-8">
           <div className="text-center">
             <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
             <p className="mt-4">Carregando resultados...</p>
           </div>
         </div>
       );
     }

     if (error) {
       return (
         <div className="container mx-auto px-4 py-8">
           <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
             {error}
           </div>
         </div>
       );
     }

     if (!result) {
       return (
         <div className="container mx-auto px-4 py-8">
           <p>Nenhum resultado encontrado</p>
         </div>
       );
     }

     if (result.status === 'processing' || result.status === 'pending_payment') {
       return (
         <div className="container mx-auto px-4 py-8">
           <div className="text-center">
             <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
             <p className="mt-4">Processando otimização...</p>
             <p className="text-sm text-gray-600">Isso pode levar 2-3 minutos</p>
           </div>
         </div>
       );
     }

     return (
       <div className="container mx-auto px-4 py-8">
         <h1 className="text-3xl font-bold mb-8">Resultados da Otimização</h1>

         {/* Match Score */}
         <div className="bg-white rounded-lg shadow p-6 mb-6">
           <h2 className="text-xl font-semibold mb-4">Score de Compatibilidade</h2>
           <div className="text-4xl font-bold text-blue-600">
             {result.match_score}%
           </div>
         </div>

         {/* Keywords */}
         {result.keywords && result.keywords.length > 0 && (
           <div className="bg-white rounded-lg shadow p-6 mb-6">
             <h2 className="text-xl font-semibold mb-4">Palavras-chave</h2>
             <div className="flex flex-wrap gap-2">
               {result.keywords.map((keyword, idx) => (
                 <span key={idx} className="bg-blue-100 text-blue-800 px-3 py-1 rounded">
                   {keyword}
                 </span>
               ))}
             </div>
           </div>
         )}

         {/* Improvements */}
         {result.improvements && result.improvements.length > 0 && (
           <div className="bg-white rounded-lg shadow p-6 mb-6">
             <h2 className="text-xl font-semibold mb-4">Sugestões de Melhoria</h2>
             <ul className="space-y-2">
               {result.improvements.map((improvement: any, idx) => (
                 <li key={idx} className="flex items-start">
                   <span className="text-blue-600 mr-2">•</span>
                   <span>{improvement.suggestion || improvement}</span>
                 </li>
               ))}
             </ul>
           </div>
         )}
       </div>
     );
   }
   ```

**Success Criteria**:

- [x] Results page fetches real data
- [x] Polling for processing status
- [x] Loading states shown
- [x] Results displayed correctly
- [x] Error handling working

---

### Task 3: Test End-to-End Workflow (15 min)

**Actions**:

1. Test complete workflow manually:

   ```bash
   # Start frontend
   cd /home/carlos/projects/cv-match/frontend
   bun run dev

   # Navigate to optimize page
   open http://localhost:3001/pt-br/optimize
   ```

2. Complete the workflow:
   - Log in to the application
   - Upload a test resume (PDF)
   - Fill in job description
   - Submit form
   - Wait for processing
   - View results

3. Verify all steps work:
   - Resume uploads successfully
   - Optimization starts
   - Redirects to results page
   - Results display after processing
   - All text in Portuguese

**Success Criteria**:

- [x] Can complete full workflow
- [x] No console errors
- [x] All UI elements work
- [x] Portuguese translations show
- [x] Results display correctly

---

## 🔧 Technical Details

### Environment Variables

Ensure these are set in `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

### API Error Handling Pattern

```typescript
try {
  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Erro desconhecido");
  }

  const data = await response.json();
  return data;
} catch (err: any) {
  setError(err.message);
  console.error("API Error:", err);
}
```

---

## 📊 Verification Checklist

```bash
cd /home/carlos/projects/cv-match/frontend

# 1. Check files updated
git diff app/optimize/page.tsx
git diff app/results/[id]/page.tsx

# 2. Start dev server
bun run dev

# 3. Open in browser
open http://localhost:3001/pt-br/optimize

# 4. Test workflow
# - Upload resume
# - Fill job details
# - Submit
# - View results

# 5. Check console for errors
# (Open browser DevTools)
```

---

## 📝 Deliverables

### Files to Update:

1. `frontend/app/optimize/page.tsx`
2. `frontend/app/results/[id]/page.tsx`

### Git Commit:

```bash
git add frontend/app/optimize/page.tsx
git add frontend/app/results/[id]/page.tsx
git commit -m "feat(frontend): Integrate real API endpoints

- Update optimize page with real API calls
- Add authentication with Supabase
- Implement resume upload flow
- Add optimization start flow
- Update results page with real data fetching
- Add polling for processing status
- Implement comprehensive error handling
- Add loading states throughout
- Test complete E2E workflow

Related: P0 Frontend integration
Tested: Full workflow verified in Portuguese"
```

---

## ⏱️ Timeline

- **00:00-00:45**: Task 1 (Update optimize page)
- **00:45-01:15**: Task 2 (Update results page)
- **01:15-01:30**: Task 3 (E2E testing)

**Total**: 1.5 hours

---

## 🎯 Success Definition

Mission complete when:

1. Optimize page uses real APIs
2. Results page fetches real data
3. Authentication integrated
4. Complete E2E workflow works
5. All UI in Portuguese
6. No console errors
7. Loading and error states working
8. Ready for production use

---

**Status**: Ready for deployment 🚀
