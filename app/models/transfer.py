from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import AmountCents


class TransferRequest(BaseModel):
    from_account_id: UUID
    to_account_id: UUID
    amount_cents: AmountCents


class Transfer(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    from_account_id: UUID
    to_account_id: UUID
    amount_cents: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
