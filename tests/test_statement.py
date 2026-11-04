from uuid import uuid4

from fastapi.testclient import TestClient

from tests.helpers import AccountFactory, post_transfer


def test_new_account_has_empty_statement(client: TestClient, make_account: AccountFactory) -> None:
    account_id = make_account()

    response = client.get(f"/accounts/{account_id}/statement")

    assert response.status_code == 200
    assert response.json() == []


def test_statement_lists_deposit_and_transfers_in_order(
    client: TestClient,
    make_account: AccountFactory,
) -> None:
    ana = make_account("Ana", balance_cents=10_000)  # 1º lançamento: depósito
    bruno = make_account("Bruno")
    post_transfer(client, ana, bruno, 2_500)

    ana_statement = client.get(f"/accounts/{ana}/statement").json()
    bruno_statement = client.get(f"/accounts/{bruno}/statement").json()

    assert [t["type"] for t in ana_statement] == ["deposit", "transfer_out"]
    assert [t["amount_cents"] for t in ana_statement] == [10_000, 2_500]
    assert [t["balance_after_cents"] for t in ana_statement] == [10_000, 7_500]
    assert ana_statement[1]["counterparty_account_id"] == bruno

    assert [t["type"] for t in bruno_statement] == ["transfer_in"]
    assert bruno_statement[0]["balance_after_cents"] == 2_500
    assert bruno_statement[0]["counterparty_account_id"] == ana
    # as duas pontas da transferência compartilham o mesmo transfer_id
    assert bruno_statement[0]["transfer_id"] == ana_statement[1]["transfer_id"]


def test_failed_transfer_does_not_appear_in_statement(
    client: TestClient,
    make_account: AccountFactory,
) -> None:
    ana = make_account("Ana", balance_cents=100)
    bruno = make_account("Bruno")
    post_transfer(client, ana, bruno, 999)  # saldo insuficiente

    assert [t["type"] for t in client.get(f"/accounts/{ana}/statement").json()] == ["deposit"]
    assert client.get(f"/accounts/{bruno}/statement").json() == []


def test_statement_of_unknown_account_returns_404(client: TestClient) -> None:
    response = client.get(f"/accounts/{uuid4()}/statement")

    assert response.status_code == 404
