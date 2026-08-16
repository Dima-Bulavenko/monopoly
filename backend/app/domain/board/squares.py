"""Static board configuration for a standard Monopoly game (40 squares, 0-indexed)."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict


class SquareType(str, Enum):
    GO = "go"
    PROPERTY = "property"
    COMMUNITY_CHEST = "community_chest"
    TAX = "tax"
    RAILROAD = "railroad"
    CHANCE = "chance"
    JAIL = "jail"  # just visiting / jail
    UTILITY = "utility"
    FREE_PARKING = "free_parking"
    GO_TO_JAIL = "go_to_jail"


class ColorGroup(str, Enum):
    BROWN = "brown"
    LIGHT_BLUE = "light_blue"
    PINK = "pink"
    ORANGE = "orange"
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    DARK_BLUE = "dark_blue"


class Square(BaseModel):
    model_config = ConfigDict(frozen=True)

    index: int
    name: str
    square_type: Literal[
        SquareType.GO,
        SquareType.COMMUNITY_CHEST,
        SquareType.CHANCE,
        SquareType.JAIL,
        SquareType.FREE_PARKING,
        SquareType.GO_TO_JAIL,
    ]


class PropertySquare(Square):
    """A colour-group property."""

    square_type: Literal[SquareType.PROPERTY] = SquareType.PROPERTY
    color_group: ColorGroup
    price: int
    # rent[0]=base, [1]=1H, [2]=2H, [3]=3H, [4]=4H, [5]=hotel
    rent: tuple[int, ...]
    house_cost: int
    mortgage_value: int

    @property
    def full_group_rent_multiplier(self) -> int:
        """Rent multiplier when player owns the full colour group (no houses)."""
        return 2


class RailroadSquare(Square):
    square_type: Literal[SquareType.RAILROAD] = SquareType.RAILROAD
    price: int
    mortgage_value: int

    @staticmethod
    def rent_for_count(count: int) -> int:
        """Rent based on how many railroads the owner holds (1-4)."""
        return {1: 25, 2: 50, 3: 100, 4: 200}[count]


class UtilitySquare(Square):
    square_type: Literal[SquareType.UTILITY] = SquareType.UTILITY
    price: int
    mortgage_value: int

    @staticmethod
    def rent_multiplier(utilities_owned: int) -> int:
        """Dice-sum multiplier: 4× for 1 utility, 10× for both."""
        return 4 if utilities_owned == 1 else 10


class TaxSquare(Square):
    square_type: Literal[SquareType.TAX] = SquareType.TAX
    amount: int


# ---------------------------------------------------------------------------
# The 40 squares — index == board position (0 = Go, 10 = Jail / Just Visiting)
# ---------------------------------------------------------------------------
BOARD: tuple[Square, ...] = (
    # 0
    Square(index=0, name="Go", square_type=SquareType.GO),
    # 1 – 9
    PropertySquare(
        index=1,
        name="Mediterranean Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.BROWN,
        price=60,
        rent=(2, 10, 30, 90, 160, 250),
        house_cost=50,
        mortgage_value=30,
    ),
    Square(index=2, name="Community Chest", square_type=SquareType.COMMUNITY_CHEST),
    PropertySquare(
        index=3,
        name="Baltic Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.BROWN,
        price=60,
        rent=(4, 20, 60, 180, 320, 450),
        house_cost=50,
        mortgage_value=30,
    ),
    TaxSquare(index=4, name="Income Tax", square_type=SquareType.TAX, amount=200),
    RailroadSquare(
        index=5,
        name="Reading Railroad",
        square_type=SquareType.RAILROAD,
        price=200,
        mortgage_value=100,
    ),
    PropertySquare(
        index=6,
        name="Oriental Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.LIGHT_BLUE,
        price=100,
        rent=(6, 30, 90, 270, 400, 550),
        house_cost=50,
        mortgage_value=50,
    ),
    Square(index=7, name="Chance", square_type=SquareType.CHANCE),
    PropertySquare(
        index=8,
        name="Vermont Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.LIGHT_BLUE,
        price=100,
        rent=(6, 30, 90, 270, 400, 550),
        house_cost=50,
        mortgage_value=50,
    ),
    PropertySquare(
        index=9,
        name="Connecticut Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.LIGHT_BLUE,
        price=120,
        rent=(8, 40, 100, 300, 450, 600),
        house_cost=50,
        mortgage_value=60,
    ),
    # 10
    Square(index=10, name="Jail / Just Visiting", square_type=SquareType.JAIL),
    # 11 – 19
    PropertySquare(
        index=11,
        name="St. Charles Place",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.PINK,
        price=140,
        rent=(10, 50, 150, 450, 625, 750),
        house_cost=100,
        mortgage_value=70,
    ),
    UtilitySquare(
        index=12,
        name="Electric Company",
        square_type=SquareType.UTILITY,
        price=150,
        mortgage_value=75,
    ),
    PropertySquare(
        index=13,
        name="States Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.PINK,
        price=140,
        rent=(10, 50, 150, 450, 625, 750),
        house_cost=100,
        mortgage_value=70,
    ),
    PropertySquare(
        index=14,
        name="Virginia Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.PINK,
        price=160,
        rent=(12, 60, 180, 500, 700, 900),
        house_cost=100,
        mortgage_value=80,
    ),
    RailroadSquare(
        index=15,
        name="Pennsylvania Railroad",
        square_type=SquareType.RAILROAD,
        price=200,
        mortgage_value=100,
    ),
    PropertySquare(
        index=16,
        name="St. James Place",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.ORANGE,
        price=180,
        rent=(14, 70, 200, 550, 750, 950),
        house_cost=100,
        mortgage_value=90,
    ),
    Square(index=17, name="Community Chest", square_type=SquareType.COMMUNITY_CHEST),
    PropertySquare(
        index=18,
        name="Tennessee Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.ORANGE,
        price=180,
        rent=(14, 70, 200, 550, 750, 950),
        house_cost=100,
        mortgage_value=90,
    ),
    PropertySquare(
        index=19,
        name="New York Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.ORANGE,
        price=200,
        rent=(16, 80, 220, 600, 800, 1000),
        house_cost=100,
        mortgage_value=100,
    ),
    # 20
    Square(index=20, name="Free Parking", square_type=SquareType.FREE_PARKING),
    # 21 – 29
    PropertySquare(
        index=21,
        name="Kentucky Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.RED,
        price=220,
        rent=(18, 90, 250, 700, 875, 1050),
        house_cost=150,
        mortgage_value=110,
    ),
    Square(index=22, name="Chance", square_type=SquareType.CHANCE),
    PropertySquare(
        index=23,
        name="Indiana Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.RED,
        price=220,
        rent=(18, 90, 250, 700, 875, 1050),
        house_cost=150,
        mortgage_value=110,
    ),
    PropertySquare(
        index=24,
        name="Illinois Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.RED,
        price=240,
        rent=(20, 100, 300, 750, 925, 1100),
        house_cost=150,
        mortgage_value=120,
    ),
    RailroadSquare(
        index=25,
        name="B&O Railroad",
        square_type=SquareType.RAILROAD,
        price=200,
        mortgage_value=100,
    ),
    PropertySquare(
        index=26,
        name="Atlantic Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.YELLOW,
        price=260,
        rent=(22, 110, 330, 800, 975, 1150),
        house_cost=150,
        mortgage_value=130,
    ),
    PropertySquare(
        index=27,
        name="Ventnor Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.YELLOW,
        price=260,
        rent=(22, 110, 330, 800, 975, 1150),
        house_cost=150,
        mortgage_value=130,
    ),
    UtilitySquare(
        index=28,
        name="Water Works",
        square_type=SquareType.UTILITY,
        price=150,
        mortgage_value=75,
    ),
    PropertySquare(
        index=29,
        name="Marvin Gardens",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.YELLOW,
        price=280,
        rent=(24, 120, 360, 850, 1025, 1200),
        house_cost=150,
        mortgage_value=140,
    ),
    # 30
    Square(index=30, name="Go To Jail", square_type=SquareType.GO_TO_JAIL),
    # 31 – 39
    PropertySquare(
        index=31,
        name="Pacific Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.GREEN,
        price=300,
        rent=(26, 130, 390, 900, 1100, 1275),
        house_cost=200,
        mortgage_value=150,
    ),
    PropertySquare(
        index=32,
        name="North Carolina Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.GREEN,
        price=300,
        rent=(26, 130, 390, 900, 1100, 1275),
        house_cost=200,
        mortgage_value=150,
    ),
    Square(index=33, name="Community Chest", square_type=SquareType.COMMUNITY_CHEST),
    PropertySquare(
        index=34,
        name="Pennsylvania Avenue",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.GREEN,
        price=320,
        rent=(28, 150, 450, 1000, 1200, 1400),
        house_cost=200,
        mortgage_value=160,
    ),
    RailroadSquare(
        index=35,
        name="Short Line Railroad",
        square_type=SquareType.RAILROAD,
        price=200,
        mortgage_value=100,
    ),
    Square(index=36, name="Chance", square_type=SquareType.CHANCE),
    PropertySquare(
        index=37,
        name="Park Place",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.DARK_BLUE,
        price=350,
        rent=(35, 175, 500, 1100, 1300, 1500),
        house_cost=200,
        mortgage_value=175,
    ),
    TaxSquare(index=38, name="Luxury Tax", square_type=SquareType.TAX, amount=100),
    PropertySquare(
        index=39,
        name="Boardwalk",
        square_type=SquareType.PROPERTY,
        color_group=ColorGroup.DARK_BLUE,
        price=400,
        rent=(50, 200, 600, 1400, 1700, 2000),
        house_cost=200,
        mortgage_value=200,
    ),
)

# Convenience maps built once at import time
BOARD_BY_INDEX: dict[int, Square] = {sq.index: sq for sq in BOARD}

# Which square indices belong to each colour group
COLOR_GROUP_INDICES: dict[ColorGroup, tuple[int, ...]] = {}
for _sq in BOARD:
    if isinstance(_sq, PropertySquare):
        COLOR_GROUP_INDICES.setdefault(_sq.color_group, []).append(_sq.index)  # ty: ignore[no-matching-overload]
COLOR_GROUP_INDICES = {k: tuple(v) for k, v in COLOR_GROUP_INDICES.items()}

RAILROAD_INDICES: tuple[int, ...] = tuple(
    sq.index for sq in BOARD if isinstance(sq, RailroadSquare)
)

UTILITY_INDICES: tuple[int, ...] = tuple(
    sq.index for sq in BOARD if isinstance(sq, UtilitySquare)
)

JAIL_INDEX = 10
GO_TO_JAIL_INDEX = 30
GO_INDEX = 0
GO_SALARY = 200
BOARD_SIZE = 40

# Building bank limits (standard rules)
MAX_HOUSES = 32
MAX_HOTELS = 12
