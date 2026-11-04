from typing import Annotated

from fastapi import Depends, Request

from app.services.account_service import AccountService


def get_account_service(request: Request) -> AccountService:
    service: AccountService = request.app.state.account_service
    return service


ServiceDep = Annotated[AccountService, Depends(get_account_service)]
