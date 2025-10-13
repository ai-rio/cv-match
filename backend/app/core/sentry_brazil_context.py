"""
Brazilian Market Context for Sentry Backend

This utility provides Brazilian market-specific context and localization
for Sentry error tracking and performance monitoring in CV-Match backend.
"""

from typing import Optional, Dict, Any, Union
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BrazilianUserContext:
    """Brazilian user context for Sentry"""

    def __init__(
        self,
        id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        locale: str = "pt-BR",
        currency: str = "BRL",
        plan: Optional[str] = None,
        subscription_status: Optional[str] = None
    ):
        self.id = id
        self.email = email
        self.name = name
        self.locale = locale
        self.currency = currency
        self.plan = plan
        self.subscription_status = subscription_status


class BrazilianTransactionContext:
    """Brazilian transaction context for Sentry"""

    def __init__(
        self,
        transaction_name: str,
        operation: str,
        currency: str = "BRL",
        amount: Optional[float] = None,
        payment_method: Optional[str] = None,
        success: Optional[bool] = None
    ):
        self.transaction_name = transaction_name
        self.operation = operation
        self.currency = currency
        self.amount = amount
        self.payment_method = payment_method
        self.success = success


class SentryBrazilianContext:
    """
    Brazilian Market Context Manager for Sentry Backend

    Provides Brazilian market-specific context, localization, and
    business logic for Sentry error tracking and performance monitoring.
    """

    def __init__(self, sentry_config):
        self.sentry_config = sentry_config

    def set_user_context(self, user: BrazilianUserContext) -> None:
        """
        Set user context with Brazilian market information

        Args:
            user: Brazilian user context object
        """
        try:
            # Build user data without calling sentry_config.set_user_context to avoid duplicate parameters
            user_data = {
                "id": user.id,
                "username": user.name,
                # Brazilian-specific context
                "locale": user.locale,
                "market": "brazil",
                "currency": user.currency,
                "country": "BR",
                "timezone": "America/Sao_Paulo",
                # Plan and subscription context
                "plan": user.plan,
                "subscription_status": user.subscription_status,
                # Additional context
                "region": "latam",
                "saas_type": "resume-matching",
                "industry": "HR_Tech"
            }

            # Only add email if provided
            if user.email:
                user_data["email"] = user.email

            # Use Sentry SDK directly
            import sentry_sdk
            sentry_sdk.set_user(user_data)

            self.add_breadcrumb("User context set", "user", "info")
            logger.info(f"Brazilian user context set for user {user.id}")

        except Exception as e:
            logger.error(f"Failed to set Brazilian user context: {e}")

    def set_transaction_context(self, transaction: BrazilianTransactionContext) -> None:
        """
        Set transaction context with Brazilian business logic

        Args:
            transaction: Brazilian transaction context object
        """
        try:
            # Set tags
            self.sentry_config.add_breadcrumb(
                message=f"Transaction context: {transaction.transaction_name}",
                category="transaction",
                level="info",
                data={
                    "operation": transaction.operation,
                    "currency": transaction.currency,
                    "payment_method": transaction.payment_method,
                    "amount": transaction.amount,
                    "success": transaction.success,
                    "market": "brazil",
                    "locale": "pt-BR"
                }
            )

            # Set transaction name with Brazilian context
            self.sentry_config.set_transaction_name(
                f"cv-match-brazil/{transaction.transaction_name}"
            )

            logger.info(f"Brazilian transaction context set for {transaction.operation}")

        except Exception as e:
            logger.error(f"Failed to set Brazilian transaction context: {e}")

    def add_breadcrumb(
        self,
        message: str,
        category: str = "brazil-context",
        level: str = "info",
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add Brazilian market breadcrumb

        Args:
            message: Breadcrumb message
            category: Breadcrumb category
            level: Breadcrumb level (info, warning, error)
            data: Additional data
        """
        try:
            breadcrumb_data = {
                "market": "brazil",
                "locale": "pt-BR",
                "country": "BR",
                "currency": "BRL",
                "timezone": "America/Sao_Paulo"
            }

            if data:
                breadcrumb_data.update(data)

            self.sentry_config.add_breadcrumb(message, category, level)

        except Exception as e:
            logger.error(f"Failed to add Brazilian breadcrumb: {e}")

    def capture_exception(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Capture exception with Brazilian context

        Args:
            error: Exception to capture
            context: Additional context information
        """
        try:
            extra_context = {
                "market": "brazil",
                "locale": "pt-BR",
                "country": "BR",
                "currency": "BRL",
                "application": "cv-match-backend",
                "timestamp": datetime.now().isoformat()
            }

            if context:
                extra_context.update(context)

            # Localize error messages for common Brazilian scenarios
            localized_message = self._localize_error_message(str(error), context or {})

            self.sentry_config.capture_exception(error, extra_context)

            self.add_breadcrumb(
                f"Exception captured: {localized_message}",
                "error",
                "error",
                {
                    "error_type": error.__class__.__name__,
                    "localized_message": localized_message,
                    "original_message": str(error)
                }
            )

            logger.info(f"Brazilian exception captured: {error.__class__.__name__}")

        except Exception as e:
            logger.error(f"Failed to capture Brazilian exception: {e}")

    def capture_message(
        self,
        message: str,
        level: str = "info",
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Capture message with Brazilian context

        Args:
            message: Message to capture
            level: Message level (info, warning, error)
            context: Additional context information
        """
        try:
            localized_message = self._localize_message(message)

            extra_context = {
                "market": "brazil",
                "locale": "pt-BR",
                "country": "BR",
                "currency": "BRL",
                "application": "cv-match-backend",
                "timestamp": datetime.now().isoformat()
            }

            if context:
                extra_context.update(context)

            self.sentry_config.capture_message(localized_message, level, extra_context)

            self.add_breadcrumb(
                f"Message captured: {localized_message}",
                "message",
                level,
                {
                    "original_message": message,
                    "localized_message": localized_message
                }
            )

            logger.info(f"Brazilian message captured: {message}")

        except Exception as e:
            logger.error(f"Failed to capture Brazilian message: {e}")

    def set_brazilian_tags(self, tags: Dict[str, Any]) -> None:
        """
        Set Brazilian market tags

        Args:
            tags: Dictionary of tags to set
        """
        try:
            # Add base Brazilian tags
            base_tags = {
                "market": "brazil",
                "locale": "pt-BR",
                "country": "BR",
                "currency": "BRL",
                "region": "latam",
                "saas_type": "resume-matching",
                "industry": "HR_Tech"
            }

            # Combine with custom tags
            all_tags = {**base_tags, **tags}

            # Add breadcrumb for tag setting
            self.add_breadcrumb(
                "Brazilian tags set",
                "tagging",
                "info",
                {"tags": all_tags}
            )

            logger.info(f"Brazilian tags set: {list(all_tags.keys())}")

        except Exception as e:
            logger.error(f"Failed to set Brazilian tags: {e}")

    def add_business_context(self, context: Dict[str, Any]) -> None:
        """
        Add Brazilian business context

        Args:
            context: Business context information
        """
        try:
            business_context = {
                **context,
                "market": "brazil",
                "locale": "pt-BR",
                "country": "BR",
                "currency": "BRL",
                "timezone": "America/Sao_Paulo",
                "timestamp": datetime.now().isoformat()
            }

            self.add_breadcrumb(
                "Business context added",
                "business",
                "info",
                business_context
            )

            logger.info("Brazilian business context added")

        except Exception as e:
            logger.error(f"Failed to add Brazilian business context: {e}")

    def _localize_error_message(self, message: str, context: Dict[str, Any]) -> str:
        """
        Localize error messages for Brazilian market

        Args:
            message: Original error message
            context: Additional context for localization

        Returns:
            Localized error message
        """
        lower_message = message.lower()

        # Payment-related errors
        if context.get("payment_context"):
            if "payment failed" in lower_message:
                return "Falha no processamento do pagamento. Tente novamente ou use outro método."
            if "card declined" in lower_message:
                return "Cartão recusado. Verifique os dados ou use outro cartão."
            if "insufficient funds" in lower_message:
                return "Saldo insuficiente. Verifique seu saldo ou use outra forma de pagamento."
            if "invalid cvv" in lower_message:
                return "CVV inválido. Verifique os três dígitos atrás do cartão."
            if "invalid expiry" in lower_message:
                return "Data de validade inválida. Verifique a data no cartão."

        # Validation errors
        if "email invalid" in lower_message:
            return "E-mail inválido. Verifique o endereço digitado."
        if "cpf invalid" in lower_message:
            return "CPF inválido. Verifique os 11 números digitados."
        if "cnpj invalid" in lower_message:
            return "CNPJ inválido. Verifique os 14 números digitados."
        if "phone invalid" in lower_message:
            return "Telefone inválido. Verifique o DDD e o número."

        # Database errors
        if "database connection failed" in lower_message:
            return "Falha na conexão com o banco de dados. Tente novamente em alguns instantes."
        if "timeout" in lower_message:
            return "Tempo esgotado. Tente novamente mais tarde."
        if "duplicate key" in lower_message:
            return "Registro já existe. Verifique os dados informados."

        # Authentication errors
        if "unauthorized" in lower_message:
            return "Não autorizado. Verifique suas credenciais de acesso."
        if "token expired" in lower_message:
            return "Sessão expirada. Faça login novamente."
        if "invalid credentials" in lower_message:
            return "Credenciais inválidas. Verifique seu e-mail e senha."

        # LLM API errors
        if "openai api error" in lower_message:
            return "Erro no serviço de processamento de IA. Tente novamente em alguns instantes."
        if "anthropic api error" in lower_message:
            return "Erro no serviço de processamento de IA. Tente novamente em alguns instantes."
        if "rate limit exceeded" in lower_message:
            return "Limite de requisições excedido. Tente novamente mais tarde."

        # General errors
        if "network error" in lower_message:
            return "Erro de conexão. Verifique sua internet e tente novamente."
        if "server error" in lower_message:
            return "Erro interno do servidor. Tente novamente em alguns instantes."
        if "not found" in lower_message:
            return "Recurso não encontrado. Verifique as informações informadas."

        return message

    def _localize_message(self, message: str) -> str:
        """
        Localize general messages

        Args:
            message: Original message

        Returns:
            Localized message
        """
        lower_message = message.lower()

        # Common Portuguese translations
        translations = {
            "user logged in": "Usuário logado com sucesso",
            "user logged out": "Usuário deslogado",
            "payment successful": "Pagamento realizado com sucesso",
            "payment failed": "Falha no pagamento",
            "subscription created": "Assinatura criada com sucesso",
            "subscription cancelled": "Assinatura cancelada",
            "resume uploaded": "Currículo enviado com sucesso",
            "resume processed": "Currículo processado com sucesso",
            "job matched": "Vaga compatível encontrada",
            "profile updated": "Perfil atualizado com sucesso",
            "account created": "Conta criada com sucesso",
            "password reset": "Senha redefinida com sucesso",
            "email verified": "E-mail verificado com sucesso",
            "api request received": "Requisição de API recebida",
            "database query executed": "Consulta ao banco de dados executada",
            "cache updated": "Cache atualizado",
            "background job started": "Tarefa em segundo plano iniciada",
            "background job completed": "Tarefa em segundo plano concluída"
        }

        for english, portuguese in translations.items():
            if english in lower_message:
                return portuguese

        return message

    def clear_user_context(self) -> None:
        """Clear user context (for logout)"""
        try:
            self.sentry_config.add_breadcrumb(
                "User context cleared",
                "auth",
                "info"
            )
            logger.info("Brazilian user context cleared")

        except Exception as e:
            logger.error(f"Failed to clear Brazilian user context: {e}")


def get_brazilian_context(sentry_config) -> SentryBrazilianContext:
    """
    Get Brazilian context manager instance

    Args:
        sentry_config: Sentry configuration instance

    Returns:
        Brazilian context manager instance
    """
    return SentryBrazilianContext(sentry_config)