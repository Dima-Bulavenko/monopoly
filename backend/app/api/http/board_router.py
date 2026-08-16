from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import APIRouter
from app.domain.board.squares import (
    BOARD,
    PropertySquare,
    Square,
    RailroadSquare,
    UtilitySquare,
    TaxSquare,
)


router = APIRouter(prefix="/board", tags=["board"])


class BoardResponse(BaseModel):
    board: list[
        Annotated[
            PropertySquare | RailroadSquare | UtilitySquare | TaxSquare | Square,
            Field(discriminator="square_type"),
        ]
    ]


@router.get("/")
async def get_board() -> BoardResponse:
    return BoardResponse(board=list(BOARD))
