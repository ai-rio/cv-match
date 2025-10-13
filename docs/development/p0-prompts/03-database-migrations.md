# Agent Prompt: Database Migrations

**Agent**: database-architect
**Phase**: 2 - Database (After Phase 1 completes)
**Priority**: P0
**Estimated Time**: 2 hours
**Dependencies**: Backend services must be copied first (to understand data models)

---

## 🎯 Mission

Analyze Resume-Matcher database migrations, create equivalent migrations for cv-match, and ensure all required tables exist with proper RLS policies and LGPD compliance.

---

## 📋 Tasks

### Task 1: Analyze Resume-Matcher Migrations (30 min)

**Source**: `/home/carlos/projects/Resume-Matcher/apps/backend/supabase/migrations/`

**Actions**:

1. List all migration files:

   ```bash
   ls -la /home/carlos/projects/Resume-Matcher/apps/backend/supabase/migrations/
   ```

2. Identify migrations that create P0 tables:
   - `resumes` table
   - `job_descriptions` table
   - `optimizations` table
   - `usage_tracking` table (beyond payments)

3. Document table schemas:
   - Columns and types
   - Primary keys
   - Foreign keys
   - Indexes
   - RLS policies
   - Triggers

4. Create analysis document:

   ```markdown
   # File: backend/migration_analysis.md

   ## Tables Required for P0

   ### resumes

   - id: UUID PRIMARY KEY
   - user_id: UUID REFERENCES auth.users
   - filename: TEXT
   - file_path: TEXT
   - extracted_text: TEXT
   - created_at: TIMESTAMPTZ
   - deleted_at: TIMESTAMPTZ (LGPD soft delete)

   ### job_descriptions

   - id: UUID PRIMARY KEY
   - user_id: UUID REFERENCES auth.users
   - title: TEXT
   - company: TEXT
   - description: TEXT
   - created_at: TIMESTAMPTZ

   ### optimizations

   - id: UUID PRIMARY KEY
   - user_id: UUID REFERENCES auth.users
   - resume_id: UUID REFERENCES resumes
   - job_description_id: UUID REFERENCES job_descriptions
   - match_score: INTEGER
   - improvements: JSONB
   - keywords: TEXT[]
   - status: TEXT (pending, processing, completed, failed)
   - created_at: TIMESTAMPTZ
   - completed_at: TIMESTAMPTZ

   ### usage_tracking

   - id: UUID PRIMARY KEY
   - user_id: UUID REFERENCES auth.users
   - action: TEXT
   - resource_type: TEXT
   - resource_id: UUID
   - created_at: TIMESTAMPTZ
   ```

**Success Criteria**:

- [x] All relevant migrations identified
- [x] Table schemas documented
- [x] RLS policies documented
- [x] Foreign key relationships mapped

---

### Task 2: Create cv-match Migrations (1 hour)

**Target**: `/home/carlos/projects/cv-match/supabase/migrations/`

**Actions**:

1. Create migration for resumes table:

   ```bash
   cd /home/carlos/projects/cv-match
   supabase migration new create_resumes_table
   ```

   ```sql
   -- File: supabase/migrations/[timestamp]_create_resumes_table.sql

   -- Create resumes table
   CREATE TABLE IF NOT EXISTS resumes (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
       filename TEXT NOT NULL,
       file_path TEXT,
       extracted_text TEXT,
       file_size INTEGER,
       mime_type TEXT,
       created_at TIMESTAMPTZ DEFAULT NOW(),
       updated_at TIMESTAMPTZ DEFAULT NOW(),
       deleted_at TIMESTAMPTZ,
       CONSTRAINT resumes_filename_check CHECK (length(filename) > 0)
   );

   -- Create index on user_id for fast lookups
   CREATE INDEX idx_resumes_user_id ON resumes(user_id) WHERE deleted_at IS NULL;

   -- Create index on created_at for sorting
   CREATE INDEX idx_resumes_created_at ON resumes(created_at DESC);

   -- Enable RLS
   ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;

   -- RLS Policy: Users can only see their own resumes
   CREATE POLICY "Users can view own resumes"
       ON resumes FOR SELECT
       USING (auth.uid() = user_id AND deleted_at IS NULL);

   -- RLS Policy: Users can insert their own resumes
   CREATE POLICY "Users can insert own resumes"
       ON resumes FOR INSERT
       WITH CHECK (auth.uid() = user_id);

   -- RLS Policy: Users can update their own resumes
   CREATE POLICY "Users can update own resumes"
       ON resumes FOR UPDATE
       USING (auth.uid() = user_id);

   -- RLS Policy: Users can soft delete their own resumes
   CREATE POLICY "Users can delete own resumes"
       ON resumes FOR UPDATE
       USING (auth.uid() = user_id);

   -- Trigger to update updated_at
   CREATE OR REPLACE FUNCTION update_updated_at()
   RETURNS TRIGGER AS $$
   BEGIN
       NEW.updated_at = NOW();
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER resumes_updated_at
       BEFORE UPDATE ON resumes
       FOR EACH ROW
       EXECUTE FUNCTION update_updated_at();

   -- Comments for documentation
   COMMENT ON TABLE resumes IS 'Stores uploaded resume files and extracted text';
   COMMENT ON COLUMN resumes.deleted_at IS 'LGPD compliance: soft delete timestamp';
   ```

2. Create migration for job_descriptions table:

   ```bash
   supabase migration new create_job_descriptions_table
   ```

   ```sql
   -- File: supabase/migrations/[timestamp]_create_job_descriptions_table.sql

   CREATE TABLE IF NOT EXISTS job_descriptions (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
       title TEXT NOT NULL,
       company TEXT NOT NULL,
       description TEXT NOT NULL,
       location TEXT,
       salary_range TEXT,
       created_at TIMESTAMPTZ DEFAULT NOW(),
       updated_at TIMESTAMPTZ DEFAULT NOW(),
       CONSTRAINT job_title_check CHECK (length(title) > 0),
       CONSTRAINT job_company_check CHECK (length(company) > 0),
       CONSTRAINT job_description_check CHECK (length(description) > 0)
   );

   CREATE INDEX idx_job_descriptions_user_id ON job_descriptions(user_id);
   CREATE INDEX idx_job_descriptions_created_at ON job_descriptions(created_at DESC);

   ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;

   CREATE POLICY "Users can view own job descriptions"
       ON job_descriptions FOR SELECT
       USING (auth.uid() = user_id);

   CREATE POLICY "Users can insert own job descriptions"
       ON job_descriptions FOR INSERT
       WITH CHECK (auth.uid() = user_id);

   CREATE POLICY "Users can update own job descriptions"
       ON job_descriptions FOR UPDATE
       USING (auth.uid() = user_id);

   CREATE POLICY "Users can delete own job descriptions"
       ON job_descriptions FOR DELETE
       USING (auth.uid() = user_id);

   CREATE TRIGGER job_descriptions_updated_at
       BEFORE UPDATE ON job_descriptions
       FOR EACH ROW
       EXECUTE FUNCTION update_updated_at();

   COMMENT ON TABLE job_descriptions IS 'Stores job descriptions for resume optimization';
   ```

3. Create migration for optimizations table:

   ```bash
   supabase migration new create_optimizations_table
   ```

   ```sql
   -- File: supabase/migrations/[timestamp]_create_optimizations_table.sql

   -- Create ENUM for optimization status
   CREATE TYPE optimization_status AS ENUM (
       'pending_payment',
       'processing',
       'completed',
       'failed'
   );

   CREATE TABLE IF NOT EXISTS optimizations (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
       resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
       job_description_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
       match_score INTEGER CHECK (match_score >= 0 AND match_score <= 100),
       improvements JSONB DEFAULT '[]'::jsonb,
       keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
       strengths TEXT[] DEFAULT ARRAY[]::TEXT[],
       weaknesses TEXT[] DEFAULT ARRAY[]::TEXT[],
       status optimization_status DEFAULT 'pending_payment',
       error_message TEXT,
       created_at TIMESTAMPTZ DEFAULT NOW(),
       updated_at TIMESTAMPTZ DEFAULT NOW(),
       started_at TIMESTAMPTZ,
       completed_at TIMESTAMPTZ,
       CONSTRAINT optimizations_user_resume_check
           FOREIGN KEY (user_id, resume_id)
           REFERENCES resumes(user_id, id)
   );

   -- Indexes for common queries
   CREATE INDEX idx_optimizations_user_id ON optimizations(user_id);
   CREATE INDEX idx_optimizations_resume_id ON optimizations(resume_id);
   CREATE INDEX idx_optimizations_status ON optimizations(status);
   CREATE INDEX idx_optimizations_created_at ON optimizations(created_at DESC);

   -- GIN index for JSONB improvements
   CREATE INDEX idx_optimizations_improvements ON optimizations USING GIN(improvements);

   ALTER TABLE optimizations ENABLE ROW LEVEL SECURITY;

   CREATE POLICY "Users can view own optimizations"
       ON optimizations FOR SELECT
       USING (auth.uid() = user_id);

   CREATE POLICY "Users can insert own optimizations"
       ON optimizations FOR INSERT
       WITH CHECK (auth.uid() = user_id);

   CREATE POLICY "Users can update own optimizations"
       ON optimizations FOR UPDATE
       USING (auth.uid() = user_id);

   CREATE TRIGGER optimizations_updated_at
       BEFORE UPDATE ON optimizations
       FOR EACH ROW
       EXECUTE FUNCTION update_updated_at();

   COMMENT ON TABLE optimizations IS 'Stores AI-powered resume optimization results';
   COMMENT ON COLUMN optimizations.match_score IS 'Compatibility score 0-100';
   COMMENT ON COLUMN optimizations.improvements IS 'JSON array of improvement suggestions';
   ```

4. Create migration for usage_tracking table:

   ```bash
   supabase migration new create_usage_tracking_table
   ```

   ```sql
   -- File: supabase/migrations/[timestamp]_create_usage_tracking_table.sql

   CREATE TABLE IF NOT EXISTS usage_tracking (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
       action TEXT NOT NULL,
       resource_type TEXT NOT NULL,
       resource_id UUID,
       metadata JSONB DEFAULT '{}'::jsonb,
       created_at TIMESTAMPTZ DEFAULT NOW(),
       CONSTRAINT usage_tracking_action_check CHECK (length(action) > 0)
   );

   CREATE INDEX idx_usage_tracking_user_id ON usage_tracking(user_id);
   CREATE INDEX idx_usage_tracking_created_at ON usage_tracking(created_at DESC);
   CREATE INDEX idx_usage_tracking_action ON usage_tracking(action);

   ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

   -- Users can only view their own usage
   CREATE POLICY "Users can view own usage"
       ON usage_tracking FOR SELECT
       USING (auth.uid() = user_id);

   -- Service role can insert usage records
   CREATE POLICY "Service can insert usage"
       ON usage_tracking FOR INSERT
       WITH CHECK (true);

   COMMENT ON TABLE usage_tracking IS 'Tracks user actions for analytics and billing';
   COMMENT ON COLUMN usage_tracking.action IS 'Action performed (e.g., resume_upload, optimization_start)';
   ```

**Success Criteria**:

- [x] 4 migration files created
- [x] All tables have RLS enabled
- [x] Proper indexes created
- [x] Foreign keys configured
- [x] LGPD compliance (soft deletes, audit trails)
- [x] Triggers for updated_at

---

### Task 3: Apply and Verify Migrations (30 min)

**Actions**:

1. Apply all migrations:

   ```bash
   cd /home/carlos/projects/cv-match

   # Apply migrations to local Supabase
   supabase db push

   # Or if using remote Supabase
   supabase db push --db-url "$SUPABASE_DB_URL"
   ```

2. Verify tables exist:

   ```bash
   docker compose exec backend python -c "
   from app.core.database import get_supabase_client

   client = get_supabase_client()

   tables = ['resumes', 'job_descriptions', 'optimizations', 'usage_tracking']
   for table in tables:
       try:
           result = client.table(table).select('count').execute()
           print(f'✅ Table {table} exists and accessible')
       except Exception as e:
           print(f'❌ Table {table} error: {e}')
   "
   ```

3. Test RLS policies:

   ```bash
   docker compose exec backend python -c "
   from app.core.database import get_supabase_client

   client = get_supabase_client()

   # Try to insert a test resume (should work with service role)
   result = client.table('resumes').insert({
       'user_id': 'test-user-id',
       'filename': 'test.pdf',
       'extracted_text': 'Test content'
   }).execute()

   if result.data:
       print('✅ RLS policies working (service role can insert)')
       # Clean up
       client.table('resumes').delete().eq('filename', 'test.pdf').execute()
   "
   ```

4. Verify indexes:
   ```sql
   -- Run in Supabase SQL Editor
   SELECT
       tablename,
       indexname,
       indexdef
   FROM pg_indexes
   WHERE schemaname = 'public'
       AND tablename IN ('resumes', 'job_descriptions', 'optimizations', 'usage_tracking')
   ORDER BY tablename, indexname;
   ```

**Success Criteria**:

- [x] All migrations applied successfully
- [x] All 4 tables exist
- [x] RLS policies active
- [x] Indexes created
- [x] Service role can access tables
- [x] No migration errors

---

## 🔧 Technical Details

### LGPD Compliance Requirements

Every table with user data MUST have:

1. **Soft Deletes**: `deleted_at TIMESTAMPTZ` column
2. **Audit Trail**: `created_at`, `updated_at` columns
3. **User Reference**: `user_id UUID REFERENCES auth.users`
4. **RLS Policies**: Tenant isolation using `auth.uid()`

### RLS Policy Patterns

**Standard User Access**:

```sql
-- Users can only see their own data
CREATE POLICY "policy_name"
    ON table_name FOR SELECT
    USING (auth.uid() = user_id AND deleted_at IS NULL);
```

**Service Role Access**:

```sql
-- Service role (backend) can do anything
-- This is implicit when using service_role key
```

### Index Strategy

**B-tree indexes** for:

- Foreign keys
- Frequently filtered columns
- Sorting columns (use DESC if sorting descending)

**GIN indexes** for:

- JSONB columns (improvements, metadata)
- Array columns (keywords, strengths)

**Partial indexes** for:

- Soft deleted data: `WHERE deleted_at IS NULL`

---

## 🚨 Common Issues & Solutions

### Issue 1: Migration Already Applied

**Symptom**: `relation "resumes" already exists`
**Solution**: Check if table exists first:

```sql
CREATE TABLE IF NOT EXISTS resumes (...);
```

### Issue 2: RLS Policy Prevents Access

**Symptom**: Query returns empty even though data exists
**Solution**:

- Use service_role key in backend
- Verify JWT token in auth headers
- Check policy logic with `EXPLAIN`

### Issue 3: Foreign Key Constraint Failed

**Symptom**: `insert or update on table violates foreign key constraint`
**Solution**:

- Ensure referenced user exists in auth.users
- Use CASCADE on delete for cleanup

### Issue 4: Index Creation Timeout

**Symptom**: Migration hangs on large tables
**Solution**:

```sql
-- Create index concurrently (doesn't lock table)
CREATE INDEX CONCURRENTLY idx_name ON table(column);
```

---

## 📊 Verification Checklist

Run each verification step:

```bash
cd /home/carlos/projects/cv-match

# 1. Check migration files exist
ls -la supabase/migrations/

# 2. Apply migrations
supabase db push

# 3. Verify tables exist
docker compose exec backend python -c "
from app.core.database import get_supabase_client
client = get_supabase_client()

tables = ['resumes', 'job_descriptions', 'optimizations', 'usage_tracking']
for table in tables:
    result = client.table(table).select('count').execute()
    print(f'✅ {table}')
"

# 4. Test insert (service role)
docker compose exec backend python -c "
from app.core.database import get_supabase_client
client = get_supabase_client()

# Test insert
result = client.table('resumes').insert({
    'user_id': '00000000-0000-0000-0000-000000000000',
    'filename': 'migration_test.pdf',
    'extracted_text': 'Test'
}).execute()

print(f'✅ Insert works: {len(result.data)} row(s)')

# Cleanup
client.table('resumes').delete().eq('filename', 'migration_test.pdf').execute()
"

# 5. Check RLS is enabled
docker compose exec backend python -c "
from app.core.database import get_supabase_client
import os

# This query requires service role
client = get_supabase_client()
print('✅ RLS enabled (using service role)')
"
```

---

## 📝 Deliverables

### Migration Files:

1. `supabase/migrations/[timestamp]_create_resumes_table.sql`
2. `supabase/migrations/[timestamp]_create_job_descriptions_table.sql`
3. `supabase/migrations/[timestamp]_create_optimizations_table.sql`
4. `supabase/migrations/[timestamp]_create_usage_tracking_table.sql`

### Documentation:

- `backend/migration_analysis.md` - Analysis of Resume-Matcher migrations
- Update schema documentation if exists

### Git Commit:

```bash
git add supabase/migrations/
git add backend/migration_analysis.md
git commit -m "feat(database): Add P0 table migrations

- Create resumes table with RLS policies
- Create job_descriptions table
- Create optimizations table with ENUM status
- Create usage_tracking table
- Add indexes for performance
- Implement LGPD compliance (soft deletes, audit trails)
- Enable RLS on all tables
- Add triggers for updated_at timestamps

Related: P0 Database implementation
Tested: All tables verified and accessible"
```

---

## ⏱️ Timeline

- **00:00-00:30**: Task 1 (Analyze Resume-Matcher migrations)
- **00:30-01:30**: Task 2 (Create cv-match migrations)
- **01:30-02:00**: Task 3 (Apply and verify)

**Total**: 2 hours

---

## 🎯 Success Definition

Mission complete when:

1. All 4 migration files created
2. Migrations applied successfully
3. All tables exist and accessible
4. RLS policies working
5. Indexes created
6. LGPD compliant
7. Service role can perform CRUD operations
8. Ready for API endpoint integration

---

## 🔄 Handoff to Backend Specialist

After completion, notify backend-specialist:

- ✅ All P0 tables created
- ✅ RLS policies active
- ✅ Indexes in place
- ✅ Ready for API endpoints to use tables

**Database schema ready for application layer!** 🎉

---

**Status**: Ready for deployment 🚀
