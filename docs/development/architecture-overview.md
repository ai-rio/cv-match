# CV-Match Architecture Overview

## System Architecture

The CV-Match platform is built on a modern, scalable architecture that combines the proven Resume-Matcher core functionality with a robust FastAPI/Next.js boilerplate.

```mermaid
graph TB
    subgraph Frontend[Frontend - Next.js]
        A[Dashboard Components]
        B[Resume Upload Components]
        C[Analytics Components]
        A --> D[HTTP/REST API]
        B --> D
        C --> D
    end

    subgraph Backend[Backend - FastAPI]
        D --> E[Resume Services]
        D --> F[Job Services]
        D --> G[Matching Services]
        E --> H[LLM & Embedding Managers]
        F --> I[Usage & Billing Services]
        G --> J[Payment Integration]
        H --> K[Supabase Database]
        I --> K
        J --> K
    end

    subgraph Database[Supabase - Database & Auth]
        K --> L[User Auth & Profiles]
        K --> M[Vector Storage]
        K --> N[Usage Data & Credits]
        K --> O[Resume & Job Data]
        K --> P[Match Results & Analytics]
        K --> Q[Subscription Data]
    end
```

## Component Architecture

### Core Component Relationships

```mermaid
graph LR
    subgraph Frontend[Frontend Components]
        A[FileUpload] --> B[ResumeUpload Page]
        C[ResumeAnalysis] --> D[Dashboard]
        E[JobListings] --> D
        F[UsageComponents] --> G[Settings Page]
        H[PaymentComponents] --> I[Billing Page]
    end

    subgraph Backend[Backend Services]
        J[ResumeService] --> K[ScoreImprovementService]
        L[JobService] --> K
        M[AgentManager] --> N[LLM Providers]
        O[EmbeddingManager] --> P[Vector Storage]
        Q[UsageLimitService] --> R[Credit System]
        S[PaymentService] --> T[Stripe Integration]
    end

    subgraph Data[Data Layer]
        U[Resumes Table]
        V[Jobs Table]
        W[MatchResults Table]
        X[UserProfiles Table]
        Y[UsageTracking Table]
        Z[Subscriptions Table]
    end

    A --> J
    B --> J
    D --> K
    E --> L
    F --> Q
    G --> Q
    H --> S
    I --> S

    J --> U
    L --> V
    K --> W
    Q --> Y
    R --> X
    S --> Z
```

## Core Components

### Frontend (Next.js + TypeScript)

#### **UI Components** (from Resume-Matcher)
- **FileUpload Component**: Advanced drag-drop file upload with PDF/DOCX support
- **ResumeAnalysis Component**: Interactive score display with improvement suggestions
- **Dashboard Components**: Complete UI for job listings and resume management
- **Usage Components**: Credit tracking and subscription management UI
- **Payment Components**: Stripe integration for billing

#### **Pages & Routes**
- `/dashboard` - Main dashboard with resume and job management
- `/upload` - Resume upload interface
- `/jobs` - Job description input and analysis
- `/analytics` - Usage analytics and insights
- `/settings` - Account and subscription management

### Backend (FastAPI + Python)

#### **Core Services** (from Resume-Matcher)
1. **ResumeService**:
   - PDF/DOCX parsing with MarkItDown
   - Structured data extraction using LLM
   - Keyword extraction and processing

2. **JobService**:
   - Job description parsing and structuring
   - Extract job requirements and keywords
   - Store processed job data

3. **ScoreImprovementService**:
   - Cosine similarity calculation between resumes and jobs
   - LLM-powered improvement suggestions
   - Real-time streaming responses
   - Advanced retry logic with validation

#### **AI & Infrastructure Services**
1. **AgentManager**: Multi-provider LLM abstraction (OpenAI, OpenRouter, Ollama)
2. **EmbeddingManager**: Vector embeddings with multiple providers
3. **UsageLimitService**: Credit-based usage tracking and validation
4. **PaymentService**: Stripe integration for subscription management

### Database Layer (Supabase)

#### **Core Tables**
- **resumes**: Raw resume content and metadata
- **processed_resumes**: Structured resume data (skills, experience, etc.)
- **jobs**: Job descriptions and requirements
- **processed_jobs**: Structured job data
- **match_results**: Matching scores and improvement suggestions

#### **SaaS Infrastructure Tables**
- **user_profiles**: Subscription tiers and credit management
- **usage_tracking**: Detailed usage logs and credit consumption
- **subscriptions**: Stripe subscription data

## Data Flow

### Resume Upload and Analysis Flow

```mermaid
flowchart TD
    A[User uploads resume PDF/DOCX] --> B[MarkItDown converts to text]
    B --> C[LLM extracts structured data]
    C --> D[Vector embeddings generated and stored]
    D --> E[User provides job description]
    E --> F[LLM extracts job requirements and keywords]
    F --> G[Cosine similarity calculated]
    G --> H[LLM generates improvement suggestions]
    H --> I[Results displayed with score and recommendations]

    style A fill:#e1f5fe
    style I fill:#e8f5e8
    style C fill:#fff3e0
    style F fill:#fff3e0
```

### Credit Usage Flow

```mermaid
flowchart TD
    A[User initiates action] --> B{Check available credits}
    B -->|Sufficient| C[Process request]
    B -->|Insufficient| D[Show upgrade prompt]
    C --> E[Deduct credits]
    E --> F[Log usage]
    F --> G[Return results]
    D --> H[Redirect to payment flow]

    style B fill:#ffecb3
    style D fill:#ffebee
    style G fill:#e8f5e8
    style H fill:#fff3e0
```

## Technology Stack

### Frontend
- **Next.js 15+**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Shadcn/ui**: Professional component library
- **Lucide React**: Icon library

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and settings
- **SQLAlchemy**: Python SQL toolkit and ORM
- **MarkItDown**: Document parsing library
- **NumPy**: Numerical computing for similarity calculations

### Database & Infrastructure
- **Supabase**: PostgreSQL database with real-time features
- **pgvector**: Vector similarity search
- **Stripe**: Payment processing
- **OpenAI/OpenRouter**: LLM providers
- **Docker**: Containerization

## Security Architecture

### Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Supabase Auth
    participant B as Backend API
    participant D as Database

    U->>F: Login Request
    F->>A: Authenticate with email/password
    A->>F: JWT Token
    F->>F: Store token in localStorage

    Note over U,D: Subsequent API requests
    U->>F: Resume Upload Request
    F->>F: Add JWT to headers
    F->>B: API Call with JWT
    B->>A: Validate JWT
    A->>B: User info
    B->>D: Process with user_id
    D->>B: Response
    B->>F: JSON Response
    F->>U: Display results
```

### Multi-tenancy Data Isolation

```mermaid
graph TB
    subgraph "User A (Tier: Pro)"
        A1[Resume Data]
        A2[Job Data]
        A3[Match Results]
        A4[Usage Logs]
    end

    subgraph "User B (Tier: Free)"
        B1[Resume Data]
        B2[Job Data]
        B3[Match Results]
        B4[Usage Logs]
    end

    subgraph "User C (Tier: Enterprise)"
        C1[Resume Data]
        C2[Job Data]
        C3[Match Results]
        C4[Usage Logs]
    end

    subgraph Database[Supabase with RLS]
        D1[User Profiles Table]
        D2[Resumes Table]
        D3[Jobs Table]
        D4[Match Results Table]
        D5[Usage Tracking Table]
    end

    A1 --> D2
    A2 --> D3
    A3 --> D4
    A4 --> D5

    B1 --> D2
    B2 --> D3
    B3 --> D4
    B4 --> D5

    C1 --> D2
    C2 --> D3
    C3 --> D4
    C4 --> D5

    style A1 fill:#e3f2fd
    style A2 fill:#e3f2fd
    style B1 fill:#fff3e0
    style B2 fill:#fff3e0
    style C1 fill:#e8f5e8
    style C2 fill:#e8f5e8
```

### Data Protection Layers

```mermaid
graph TD
    subgraph SecurityLayers[Security Layers]
        A[Input Validation]
        B[Authentication & Authorization]
        C[Data Encryption]
        D[Access Control]
        E[Audit Logging]
    end

    subgraph DataFlow[Data Processing Flow]
        F[User Input] --> A
        A --> B
        B --> C
        C --> D
        D --> E
        E --> G[Database Storage]
    end

    subgraph ProtectionMechanisms[Protection Mechanisms]
        H[File Type Validation]
        I[Malware Scanning]
        J[Content Sanitization]
        K[Rate Limiting]
        L[Backup & Recovery]
    end

    F --> H
    H --> I
    I --> J
    J --> K
    K --> L
```

**Security Features:**
- **Supabase Auth**: User authentication with JWT tokens
- **Row Level Security (RLS)**: Database-level access control
- **Multi-tenancy**: User data isolation with per-user permissions
- **API Rate Limiting**: Prevent abuse and manage costs by subscription tier
- **File Validation**: Malicious file detection and scanning
- **Content Sanitization**: Clean and validate all user inputs
- **Secure File Storage**: Isolated file storage per user with access controls
- **Data Encryption**: Encryption at rest and in transit with TLS 1.3+

## Performance Optimizations

### Performance Architecture

```mermaid
graph TD
    subgraph FrontendCache[Frontend Caching]
        A[Browser Cache] --> B[Service Worker]
        B --> C[CDN Cache]
    end

    subgraph BackendCache[Backend Caching]
        D[Response Cache] --> E[Vector Cache]
        E --> F[Session Cache]
        F --> G[Database Cache]
    end

    subgraph Processing[Async Processing]
        H[Background Workers] --> I[Task Queue]
        I --> J[Priority Processing]
        J --> K[Streaming Responses]
    end

    subgraph Database[Database Layer]
        L[Vector Indexing] --> M[Connection Pooling]
        M --> N[Query Optimization]
        N --> O[Read Replicas]
    end

    C --> D
    G --> H
    K --> L
```

### Caching Strategy
- **Response Caching**: Cache LLM responses when appropriate (TTL: 1 hour)
- **Vector Cache**: Cache frequently used embeddings (Redis)
- **User Session Cache**: Store user preferences and recent activity
- **CDN Caching**: Static assets and UI components delivered via CDN

### Async Processing
- **Background Tasks**: Heavy processing moved to background workers (Celery/Redis)
- **Streaming Responses**: Real-time progress updates for long-running tasks
- **Queue Management**: Prioritize processing based on subscription tier
- **Result Caching**: Store processing results to avoid re-computation

### Database Optimization
- **Vector Indexing**: Optimized similarity search with pgvector (HNSW index)
- **Connection Pooling**: Efficient database connection management (pgbouncer)
- **Query Optimization**: Indexed queries for common operations
- **Read Replicas**: Separate read database for analytics and reporting

## Scalability Considerations

### Horizontal Scaling
- **Load Balancing**: Multiple backend instances
- **Database Read Replicas**: Read scaling for analytics
- **CDN Integration**: Static asset delivery

### Resource Management
- **Rate Limiting**: Per-user and per-tier rate limits
- **Resource Quotas**: Fair usage enforcement
- **Auto-scaling**: Dynamic resource allocation

## Monitoring & Analytics

### Application Monitoring
- **Health Checks**: API endpoint monitoring
- **Performance Metrics**: Response times and throughput
- **Error Tracking**: Comprehensive error logging and alerting
- **Usage Analytics**: User behavior and feature adoption

### Business Metrics
- **Conversion Rates**: Free to paid conversions
- **User Engagement**: Active users and session duration
- **Revenue Tracking**: Subscription revenue and churn
- **Feature Usage**: Most/least used features

## Development Workflow

### Local Development
- **Hot Reload**: Fast development with automatic updates
- **Database Migrations**: Schema versioning and deployment
- **Environment Management**: Consistent development environments
- **Testing Suite**: Unit, integration, and end-to-end tests

### Deployment Pipeline
- **CI/CD**: Automated testing and deployment
- **Staging Environment**: Production-like testing environment
- **Blue-Green Deployments**: Zero-downtime deployments
- **Rollback Capability**: Quick recovery from issues

## Future Architecture Enhancements

### AI/ML Improvements
- **Custom Models**: Fine-tuned models for specific industries
- **Batch Processing**: Bulk analysis capabilities
- **Advanced Analytics**: Predictive insights and recommendations
- **Multi-modal AI**: Image and video resume analysis

### Enterprise Features
- **API Access**: Programmatic access for enterprise customers
- **SSO Integration**: Single sign-on for corporate customers
- **Advanced Analytics**: Custom reports and data export
- **White-labeling**: Custom branding for B2B customers

This architecture provides a solid foundation for a scalable, maintainable, and feature-rich CV matching SaaS platform that can grow from a simple matching tool to a comprehensive talent optimization platform.
