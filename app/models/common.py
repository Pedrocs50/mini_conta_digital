from typing import Annotated

from pydantic import Field

# Dinheiro SEMPRE em centavos, como inteiro: R$ 10,50 = 1050.
# `strict=True` impede que o Pydantic "ajude" convertendo 10.5 ou "100" em inteiro:
# quem manda valor fracionado ou texto recebe 422, em vez de um arredondamento silencioso.
AmountCents = Annotated[
    int,
    Field(
        strict=True,
        gt=0,
        description="Valor em centavos, inteiro e positivo. Ex.: R$ 10,50 = 1050.",
    ),
]
