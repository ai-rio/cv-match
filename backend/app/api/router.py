from fastapi import APIRouter

from app.api import pricing, subscriptions
from app.api.endpoints import auth, llm, optimizations, payments, resumes, users, vectordb, webhooks

api_router = APIRouter()

# Include sub-routers for different API endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(resumes.router, tags=["Resumes"])
api_router.include_router(optimizations.router, tags=["Optimizations"])
api_router.include_router(llm.router, prefix="/llm", tags=["LLM Services"])
api_router.include_router(vectordb.router, prefix="/vectordb", tags=["Vector Database"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(webhooks.router, tags=["Webhooks"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["Pricing"])
api_router.include_router(subscriptions.router, tags=["Subscriptions"])
