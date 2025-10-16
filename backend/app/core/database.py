"""
Database session and operations for cv-match backend.
"""

from typing import Any

from app.core.config import settings
from supabase import Client, create_client


class SupabaseSession:
    """Supabase session wrapper for database operations."""

    def __init__(self) -> None:
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


class DatabaseOperations:
    """Generic database operations for Supabase."""

    def __init__(self, db: SupabaseSession) -> None:
        self.db = db

    async def select_by_id(
        self, table: str, id_column: str, id_value: str
    ) -> dict[str, Any] | None:
        """
        Select a record by ID.

        Args:
            table: Table name
            id_column: ID column name
            id_value: ID value

        Returns:
            Record data or None if not found
        """
        result = self.db.client.table(table).select("*").eq(id_column, id_value).execute()
        return result.data[0] if result.data else None

    async def insert(self, table: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Insert a new record.

        Args:
            table: Table name
            data: Record data

        Returns:
            Inserted record data
        """
        result = self.db.client.table(table).insert(data).execute()
        if not result.data:
            raise ValueError(f"Failed to insert record into {table}")
        return result.data[0]

    async def update(
        self, table: str, id_column: str, id_value: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update a record.

        Args:
            table: Table name
            id_column: ID column name
            id_value: ID value
            data: Update data

        Returns:
            Updated record data
        """
        result = self.db.client.table(table).update(data).eq(id_column, id_value).execute()
        if not result.data:
            raise ValueError(f"Failed to update record in {table}")
        return result.data[0]

    async def delete(self, table: str, id_column: str, id_value: str) -> bool:
        """
        Delete a record.

        Args:
            table: Table name
            id_column: ID column name
            id_value: ID value

        Returns:
            True if deleted, False if not found
        """
        result = self.db.client.table(table).delete().eq(id_column, id_value).execute()
        return bool(result.data)


def get_supabase_client() -> Client:
    """
    Get a Supabase client instance.

    Returns:
        Supabase client instance
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
