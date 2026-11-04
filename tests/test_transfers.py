from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.helpers import AccountFactory, get_balance, post_transfer


def test_transfer_moves_money_between_accounts(
    client: TestClient, make_account: AccountFactory
) -> None:
    source = make_account("Ana", balance_cents=10_000)
    destination = make_account("Bruno")

    response = post_transfer(client, source, destination, 2_500)

    assert response.status_code == 201
    body = response.json()
    assert body["from_account_id"] == source
    assert body["to_account_id"] == destination
    assert body["amount_cents"] == 2_500
    assert get_balance(client, source) == 7_500
    assert get_balance(client, destination) == 2_500


def test_transfer_of_entire_balance_is_allowed(
    client: TestClient, make_account: AccountFactory
) -> None:
    source = make_account("Ana", balance_cents=1_000)
    destination = make_account("Bruno")

    response = post_transfer(client, source, destination, 1_000)

    assert response.status_code == 201
    assert get_balance(client, source) == 0
    assert get_balance(client, destination) == 1_000


def test_transfer_with_insufficient_funds_returns_409_and_changes_nothing(
    client: TestClient,
    make_account: AccountFactory,
) -> None:
    source = make_account("Ana", balance_cents=1_000)
    destination = make_account("Bruno", balance_cents=500)

    response = post_transfer(client, source, destination, 1_001)

    assert response.status_code == 409
    assert response.json()["code"] == "insufficient_funds"
    assert get_balance(client, source) == 1_000
    assert get_balance(client, destination) == 500


def test_transfer_from_unknown_account_returns_404(
    client: TestClient, make_account: AccountFactory
) -> None:
    destination = make_account("Bruno")

    response = post_transfer(client, str(uuid4()), destination, 100)

    assert response.status_code == 404
    assert get_balance(client, destination) == 0


def test_transfer_to_unknown_account_returns_404_and_does_not_debit(
    client: TestClient,
    make_account: AccountFactory,
) -> None:
    source = make_account("Ana", balance_cents=1_000)

    response = post_transfer(client, source, str(uuid4()), 100)

    assert response.status_code == 404
    assert get_balance(client, source) == 1_000


def test_transfer_to_same_account_returns_422(
    client: TestClient, make_account: AccountFactory
) -> None:
    account = make_account("Ana", balance_cents=1_000)

    response = post_transfer(client, account, account, 100)

    assert response.status_code == 422
    assert response.json()["code"] == "same_account_transfer"
    assert get_balance(client, account) == 1_000


@pytest.mark.parametrize("amount", [0, -1, 10.5, "100", None, True])
def test_transfer_rejects_invalid_amount(
    client: TestClient,
    make_account: AccountFactory,
    amount: Any,
) -> None:
    source = make_account("Ana", balance_cents=1_000)
    destination = make_account("Bruno")

    response = post_transfer(client, source, destination, amount)

    assert response.status_code == 422
    assert get_balance(client, source) == 1_000


def test_transfer_rejects_malformed_account_id(
    client: TestClient, make_account: AccountFactory
) -> None:
    destination = make_account("Bruno")

    response = post_transfer(client, "abc", destination, 100)

    assert response.status_code == 422


# ---------- Idempotência ----------


def test_same_idempotency_key_does_not_duplicate_transfer(
    client: TestClient,
    make_account: AccountFactory,
) -> None:
    source = make_account("Ana", balance_cents=10_000)
    destination = make_account("Bruno")

    first = post_transfer(client, source, destination, 3_000, idempotency_key="pedido-1")
    second = post_transfer(client, source, destination, 3_000, idempotency_key="pedido-1")

    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json() == first.json()  # mesma transferência devolvida
    assert get_balance(client, source) == 7_000  # debitou UMA vez só
    assert get_balance(client, destination) == 3_000


def test_same_idempotency_key_with_different_payload_returns_422(
    client: TestClient,
    make_account: AccountFactory,
) -> None:
    source = make_account("Ana", balance_cents=10_000)
    destination = make_account("Bruno")
    post_transfer(client, source, destination, 3_000, idempotency_key="pedido-1")

    response = post_transfer(client, source, destination, 9_000, idempotency_key="pedido-1")

    assert response.status_code == 422
    assert response.json()["code"] == "idempotency_key_conflict"
    assert get_balance(client, source) == 7_000


def test_without_idempotency_key_each_request_is_a_new_transfer(
    client: TestClient,
    make_account: AccountFactory,
) -> None:
    source = make_account("Ana", balance_cents=10_000)
    destination = make_account("Bruno")

    post_transfer(client, source, destination, 1_000)
    post_transfer(client, source, destination, 1_000)

    assert get_balance(client, source) == 8_000


def test_failed_transfer_does_not_consume_idempotency_key(
    client: TestClient,
    make_account: AccountFactory,
) -> None:
    source = make_account("Ana", balance_cents=100)
    destination = make_account("Bruno")

    failed = post_transfer(client, source, destination, 500, idempotency_key="pedido-1")
    client.post(f"/accounts/{source}/deposits", json={"amount_cents": 1_000})
    retried = post_transfer(client, source, destination, 500, idempotency_key="pedido-1")

    assert failed.status_code == 409
    assert retried.status_code == 201
    assert get_balance(client, destination) == 500
