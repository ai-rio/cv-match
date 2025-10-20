# 08 - Optimize Flow UI

**Agent**: `frontend-specialist`
**Phase**: 4
**Duration**: 4h
**Dependencies**: Previous phase complete

---

## 🎯 Objective

Implement upload, form, and results using Kokonut UI components following design system specs.

---

## 📋 Key Tasks

1. Review design system docs
2. Install and configure Kokonut UI components for optimize flow
3. Implement file upload with animated interactions
4. Create form with animated buttons
5. Display results with animated text
6. Apply theme styling
7. Test responsive behavior
8. Verify accessibility

---

## 📚 Reference

- [Design System](../../design-system/README.md)
- [Wireframes](../../design-system/wireframes.md)
- [Components](../../design-system/components.md)
- [Kokonut UI Installation](04-kokonut-installation.md)
- [Kokonut UI Migration Guide](_design-reference/KOKONUT-UI-MIGRATION-GUIDE.md)

---

## 🛠️ Implementation Steps

### 1. Component Installation

```bash
# Install required Kokonut UI components for optimize flow
bunx shadcn@latest add @kokonutui/gradient-button
bunx shadcn@latest add @kokonutui/particle-button
bunx shadcn@latest add @kokonutui/shimmer-text
bunx shadcn@latest add @kokonutui/type-writer
bunx shadcn@latest add @kokonutui/attract-button

# Verify installation
ls frontend/components/ui/gradient-button.tsx
ls frontend/components/ui/particle-button.tsx
ls frontend/components/ui/shimmer-text.tsx
ls frontend/components/ui/type-writer.tsx
ls frontend/components/ui/attract-button.tsx
```

### 2. File Upload Implementation

Create an animated file upload component:

```typescript
// frontend/components/optimize/file-upload.tsx
import { AttractButton } from '@/components/ui/attract-button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useState } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isUploading?: boolean;
}

export function FileUpload({ onFileSelect, isUploading = false }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  return (
    <Card className={`transition-all duration-300 ${dragActive ? 'border-primary' : ''}`}>
      <CardHeader>
        <CardTitle>Upload Your CV</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="space-y-4">
            <div className="text-4xl">📄</div>
            <div>
              <p className="text-lg font-medium">Drop your CV here</p>
              <p className="text-sm text-muted-foreground">or click to browse</p>
            </div>
            <AttractButton disabled={isUploading}>
              {isUploading ? 'Uploading...' : 'Choose File'}
            </AttractButton>
            <p className="text-xs text-muted-foreground">
              Supports PDF, DOC, DOCX (Max 5MB)
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

### 3. Job Description Form Implementation

Create an animated form component:

```typescript
// frontend/components/optimize/job-form.tsx
import { GradientButton } from '@/components/ui/gradient-button';
import { ParticleButton } from '@/components/ui/particle-button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useState } from 'react';

interface JobFormProps {
  onSubmit: (jobDescription: string) => void;
  isLoading?: boolean;
}

export function JobForm({ onSubmit, isLoading = false }: JobFormProps) {
  const [jobDescription, setJobDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (jobDescription.trim()) {
      onSubmit(jobDescription);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Job Description</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="job-description">Paste the job description</Label>
            <Textarea
              id="job-description"
              placeholder="Paste the full job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={6}
              className="mt-2"
            />
          </div>
          <div className="flex gap-2">
            <GradientButton 
              type="submit" 
              disabled={!jobDescription.trim() || isLoading}
              className="flex-1"
            >
              {isLoading ? 'Analyzing...' : 'Optimize CV'}
            </GradientButton>
            <ParticleButton 
              type="button"
              variant="outline"
              onClick={() => setJobDescription('')}
              disabled={isLoading}
            >
              Clear
            </ParticleButton>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
```

### 4. Results Display Implementation

Create an animated results component:

```typescript
// frontend/components/optimize/results-display.tsx
import { ShimmerText } from '@/components/ui/shimmer-text';
import { TypeWriter } from '@/components/ui/type-writer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ResultsDisplayProps {
  results: {
    score: number;
    suggestions: string[];
    improvements: string[];
  };
}

export function ResultsDisplay({ results }: ResultsDisplayProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Optimization Results</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6">
            <ShimmerText className="text-6xl font-bold text-primary mb-2">
              {results.score}%
            </ShimmerText>
            <p className="text-lg text-muted-foreground">Match Score</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Key Suggestions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {results.suggestions.map((suggestion, index) => (
              <div key={index} className="flex items-start gap-3">
                <Badge variant="secondary" className="mt-1">
                  {index + 1}
                </Badge>
                <TypeWriter
                  text={suggestion}
                  speed={30}
                  className="text-sm"
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recommended Improvements</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {results.improvements.map((improvement, index) => (
              <div key={index} className="flex items-center gap-2">
                <div className="w-2 h-2 bg-primary rounded-full"></div>
                <p className="text-sm">{improvement}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## 🎨 Component Mapping

| Original Component | Kokonut UI Component | Usage |
|-------------------|----------------------|-------|
| Moving Border | gradient-button, particle-button | Form submit and action buttons |
| Sparkles | attract-button | File upload button |
| Text Reveal | shimmer-text, type-writer | Results display and animations |

---

## 🔍 Type Checking Integration

### Post-Implementation Type Check Instructions

After implementing the optimize flow UI components, perform comprehensive type checking to ensure type safety across the upload, form, and results components.

### Phase-Specific Type Validation Commands

Execute the following commands in sequence to validate types:

```bash
# Run the project's type check script
bun run type-check

# Strict type checking for optimize app routes
npx tsc --noEmit src/app/optimize/**/*.tsx --strict

# Strict type checking for optimize components
npx tsc --noEmit src/components/optimize/**/*.tsx --strict

# Type validation for Kokonut UI components
npx tsc --noEmit src/components/ui/kokonutui/**/*.tsx --strict

# Type validation for flow-specific types
npx tsc --noEmit src/types/flow.ts --strict
```

### Type Validation Checklist

- [ ] All optimize app routes compile without type errors
- [ ] File upload components have proper prop types
- [ ] Form validation maintains type safety
- [ ] Results display components are properly typed
- [ ] Flow state management is type-safe
- [ ] File handling operations have correct types
- [ ] Kokonut UI components integrate without type conflicts

### Type Error Resolution Guidance

If encountering type errors:

1. **File Upload Types**: Ensure file objects and event handlers are properly typed
2. **Form Validation**: Verify form data structures match validation schemas
3. **Results Types**: Check that API response types match results component expectations
4. **Flow State**: Ensure state transitions between upload, form, and results are typed
5. **File Processing**: Verify file processing functions have proper input/output types
6. **Kokonut UI Integration**: Resolve type conflicts between Kokonut UI and existing components

---

## ✅ Verification

- [ ] Matches wireframes
- [ ] Uses design tokens
- [ ] Responsive (320px-1920px)
- [ ] Theme works (light/dark)
- [ ] Accessible (WCAG AA)
- [ ] No console errors
- [ ] All type checks pass
- [ ] File upload drag-and-drop works
- [ ] Form validation functions correctly
- [ ] Results animations render smoothly
- [ ] Button interactions are responsive

---

**Status**: Template - Expand with full implementation steps
**Updated**: October 20, 2025 - Migrated from Aceternity UI to Kokonut UI
