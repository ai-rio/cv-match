from typing import Optional

from supabase import Client, create_client

from app.core.config import settings



class SupabaseAuthService:
    """Service for handling Supabase authentication."""

    def __init__(self):
        """Initialize the Supabase client."""
        # Initialize with proper options structure
        # The headers attribute is needed by the Supabase client
        options = {
            "auto_refresh_token": True,
            "persist_session": True,
            "headers": {"X-Client-Info": "backend-api"},
        }

        # Create the client with the properly structured options
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    async def get_user(self, jwt_token: str) -> Optional[object]:
        """Get user data from a JWT token."""
        # Use the Supabase client to get user information
        try:
            response = self.supabase.auth.get_user(jwt_token)
            if response is None:
                return None
            return response.user
        except Exception:
            return None

    async def sign_in_with_email_password(self, email: str, password: str) -> str:
        """Sign in with email and password."""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not response.session or not response.session.access_token:
                raise ValueError("Failed to authenticate with email and password")

            return response.session.access_token
        except Exception as e:
            raise ValueError(f"Email/password authentication failed: {str(e)}")

    async def sign_in_with_provider_token(self, provider: str, token: str) -> str:
        """Exchange a provider token (Google, LinkedIn) for a Supabase token."""
        if provider not in ["google", "linkedin"]:
            raise ValueError(f"Unsupported provider: {provider}")

        # Use signInWithIDToken for Google OAuth
        # Note: This is a placeholder implementation
        # In a real implementation, you'd use the appropriate Supabase auth method
        try:
            # For Google, use signInWithIDToken with proper credentials structure
            if provider == "google":
                credentials = {"id_token": token, "provider": "google"}
                response = self.supabase.auth.sign_in_with_id_token(credentials)
            else:
                # For other providers, you might need different implementations
                raise ValueError(f"Provider {provider} not yet implemented")

            if not response.session or not response.session.access_token:
                raise ValueError(f"Failed to authenticate with {provider}")

            return response.session.access_token
        except Exception as e:
            raise ValueError(f"Authentication failed: {str(e)}")


# Dependency to get the auth service
def get_auth_service() -> SupabaseAuthService:
    """Return an instance of the Supabase auth service."""
    return SupabaseAuthService()
