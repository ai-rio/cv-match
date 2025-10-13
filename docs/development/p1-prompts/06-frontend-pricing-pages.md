# Agent Prompt: Frontend Pricing Pages

**Agent**: frontend-specialist
**Phase**: 4 - Frontend (Parallel with testing)
**Priority**: P0
**Time**: 1.5 hours

## Mission

Create pricing page in Portuguese with BRL pricing and Stripe Checkout integration.

## Tasks

### Task 1: Copy Pricing Page (1h)

**Source**: Resume-Matcher `app/[locale]/pricing/page.tsx`
**Target**: cv-match `frontend/app/[locale]/pricing/page.tsx`

Update with:

- BRL currency (R$)
- Portuguese translations
- Stripe checkout integration
- Credit tiers: Free (3), Basic (10), Pro (50)

### Task 2: Create Payment Pages (30min)

**Success Page** (`app/payment/success/page.tsx`):

```tsx
export default function PaymentSuccess() {
  return (
    <div className="text-center py-12">
      <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
      <h1 className="text-2xl font-bold mt-4">Pagamento Aprovado!</h1>
      <p>Seus créditos foram adicionados com sucesso.</p>
      <Button href="/dashboard">Ver Créditos</Button>
    </div>
  );
}
```

**Cancel Page** (`app/payment/canceled/page.tsx`):

```tsx
export default function PaymentCanceled() {
  return (
    <div className="text-center py-12">
      <XCircle className="w-16 h-16 text-red-500 mx-auto" />
      <h1 className="text-2xl font-bold mt-4">Pagamento Cancelado</h1>
      <p>Você pode tentar novamente quando quiser.</p>
      <Button href="/pricing">Ver Planos</Button>
    </div>
  );
}
```

### Task 3: Add Credit Display to Dashboard (30min)

```tsx
export default function Dashboard() {
  const [credits, setCredits] = useState(0);

  useEffect(() => {
    fetch("/api/credits")
      .then((r) => r.json())
      .then((data) => setCredits(data.credits));
  }, []);

  return (
    <div>
      <Card>
        <CardTitle>Seus Créditos</CardTitle>
        <CardContent>
          <p className="text-3xl font-bold">{credits}</p>
          <p className="text-sm text-gray-600">otimizações restantes</p>
          <Button href="/pricing">Comprar Mais</Button>
        </CardContent>
      </Card>
    </div>
  );
}
```

## Success Criteria

- Pricing page in Portuguese
- BRL currency displayed correctly
- Stripe checkout works
- Payment success/cancel pages
- Credit balance visible in dashboard

Total: 1.5 hours
