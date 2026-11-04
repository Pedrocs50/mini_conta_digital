from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models.common import AmountCents

OwnerName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class CreateAccountRequest(BaseModel):
    owner_name: OwnerName


class DepositRequest(BaseModel):
    amount_cents: AmountCents


class Account(BaseModel):
    # validate_assignment: se algum código tentar deixar o saldo negativo, o Pydantic
    # levanta erro na hora. É uma "rede de segurança"; a regra de verdade fica no serviço.
    model_config = ConfigDict(validate_assignment=True)

    id: UUID = Field(default_factory=uuid4)
    owner_name: str
    balance_cents: int = Field(default=0, ge=0, description="Saldo em centavos.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
