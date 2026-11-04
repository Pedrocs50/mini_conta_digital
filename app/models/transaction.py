from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class TransactionType(StrEnum):
    DEPOSIT = "deposit"
    TRANSFER_OUT = "transfer_out"  # saiu dinheiro desta conta
    TRANSFER_IN = "transfer_in"  # entrou dinheiro nesta conta


class Transaction(BaseModel):
    """Uma linha do extrato. Imutável: histórico não se edita, só se acrescenta."""

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    account_id: UUID
    type: TransactionType
    amount_cents: int
    balance_after_cents: int
    counterparty_account_id: UUID | None = None
    transfer_id: UUID | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
