"""Static board configuration for a standard Monopoly game (40 squares, 0-indexed)."""

from dataclasses import dataclass
from enum import Enum


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


@dataclass(frozen=True)
class Square:
    index: int
    name: str
    square_type: SquareType


@dataclass(frozen=True)
class PropertySquare(Square):
    """A colour-group property."""

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


@dataclass(frozen=True)
class RailroadSquare(Square):
    price: int
    mortgage_value: int

    @staticmethod
    def rent_for_count(count: int) -> int:
        """Rent based on how many railroads the owner holds (1-4)."""
        return {1: 25, 2: 50, 3: 100, 4: 200}[count]


@dataclass(frozen=True)
class UtilitySquare(Square):
    price: int
    mortgage_value: int

    @staticmethod
    def rent_multiplier(utilities_owned: int) -> int:
        """Dice-sum multiplier: 4× for 1 utility, 10× for both."""
        return 4 if utilities_owned == 1 else 10


@dataclass(frozen=True)
class TaxSquare(Square):
    amount: int


# ---------------------------------------------------------------------------
# The 40 squares — index == board position (0 = Go, 10 = Jail / Just Visiting)
# ---------------------------------------------------------------------------
BOARD: tuple[Square, ...] = (
    # 0
    Square(0, "Go", SquareType.GO),
    # 1 – 9
    PropertySquare(
        1,
        "Mediterranean Avenue",
        SquareType.PROPERTY,
        ColorGroup.BROWN,
        60,
        (2, 10, 30, 90, 160, 250),
        50,
        30,
    ),
    Square(2, "Community Chest", SquareType.COMMUNITY_CHEST),
    PropertySquare(
        3,
        "Baltic Avenue",
        SquareType.PROPERTY,
        ColorGroup.BROWN,
        60,
        (4, 20, 60, 180, 320, 450),
        50,
        30,
    ),
    TaxSquare(4, "Income Tax", SquareType.TAX, 200),
    RailroadSquare(5, "Reading Railroad", SquareType.RAILROAD, 200, 100),
    PropertySquare(
        6,
        "Oriental Avenue",
        SquareType.PROPERTY,
        ColorGroup.LIGHT_BLUE,
        100,
        (6, 30, 90, 270, 400, 550),
        50,
        50,
    ),
    Square(7, "Chance", SquareType.CHANCE),
    PropertySquare(
        8,
        "Vermont Avenue",
        SquareType.PROPERTY,
        ColorGroup.LIGHT_BLUE,
        100,
        (6, 30, 90, 270, 400, 550),
        50,
        50,
    ),
    PropertySquare(
        9,
        "Connecticut Avenue",
        SquareType.PROPERTY,
        ColorGroup.LIGHT_BLUE,
        120,
        (8, 40, 100, 300, 450, 600),
        50,
        60,
    ),
    # 10
    Square(10, "Jail / Just Visiting", SquareType.JAIL),
    # 11 – 19
    PropertySquare(
        11,
        "St. Charles Place",
        SquareType.PROPERTY,
        ColorGroup.PINK,
        140,
        (10, 50, 150, 450, 625, 750),
        100,
        70,
    ),
    UtilitySquare(12, "Electric Company", SquareType.UTILITY, 150, 75),
    PropertySquare(
        13,
        "States Avenue",
        SquareType.PROPERTY,
        ColorGroup.PINK,
        140,
        (10, 50, 150, 450, 625, 750),
        100,
        70,
    ),
    PropertySquare(
        14,
        "Virginia Avenue",
        SquareType.PROPERTY,
        ColorGroup.PINK,
        160,
        (12, 60, 180, 500, 700, 900),
        100,
        80,
    ),
    RailroadSquare(15, "Pennsylvania Railroad", SquareType.RAILROAD, 200, 100),
    PropertySquare(
        16,
        "St. James Place",
        SquareType.PROPERTY,
        ColorGroup.ORANGE,
        180,
        (14, 70, 200, 550, 750, 950),
        100,
        90,
    ),
    Square(17, "Community Chest", SquareType.COMMUNITY_CHEST),
    PropertySquare(
        18,
        "Tennessee Avenue",
        SquareType.PROPERTY,
        ColorGroup.ORANGE,
        180,
        (14, 70, 200, 550, 750, 950),
        100,
        90,
    ),
    PropertySquare(
        19,
        "New York Avenue",
        SquareType.PROPERTY,
        ColorGroup.ORANGE,
        200,
        (16, 80, 220, 600, 800, 1000),
        100,
        100,
    ),
    # 20
    Square(20, "Free Parking", SquareType.FREE_PARKING),
    # 21 – 29
    PropertySquare(
        21,
        "Kentucky Avenue",
        SquareType.PROPERTY,
        ColorGroup.RED,
        220,
        (18, 90, 250, 700, 875, 1050),
        150,
        110,
    ),
    Square(22, "Chance", SquareType.CHANCE),
    PropertySquare(
        23,
        "Indiana Avenue",
        SquareType.PROPERTY,
        ColorGroup.RED,
        220,
        (18, 90, 250, 700, 875, 1050),
        150,
        110,
    ),
    PropertySquare(
        24,
        "Illinois Avenue",
        SquareType.PROPERTY,
        ColorGroup.RED,
        240,
        (20, 100, 300, 750, 925, 1100),
        150,
        120,
    ),
    RailroadSquare(25, "B&O Railroad", SquareType.RAILROAD, 200, 100),
    PropertySquare(
        26,
        "Atlantic Avenue",
        SquareType.PROPERTY,
        ColorGroup.YELLOW,
        260,
        (22, 110, 330, 800, 975, 1150),
        150,
        130,
    ),
    PropertySquare(
        27,
        "Ventnor Avenue",
        SquareType.PROPERTY,
        ColorGroup.YELLOW,
        260,
        (22, 110, 330, 800, 975, 1150),
        150,
        130,
    ),
    UtilitySquare(28, "Water Works", SquareType.UTILITY, 150, 75),
    PropertySquare(
        29,
        "Marvin Gardens",
        SquareType.PROPERTY,
        ColorGroup.YELLOW,
        280,
        (24, 120, 360, 850, 1025, 1200),
        150,
        140,
    ),
    # 30
    Square(30, "Go To Jail", SquareType.GO_TO_JAIL),
    # 31 – 39
    PropertySquare(
        31,
        "Pacific Avenue",
        SquareType.PROPERTY,
        ColorGroup.GREEN,
        300,
        (26, 130, 390, 900, 1100, 1275),
        200,
        150,
    ),
    PropertySquare(
        32,
        "North Carolina Avenue",
        SquareType.PROPERTY,
        ColorGroup.GREEN,
        300,
        (26, 130, 390, 900, 1100, 1275),
        200,
        150,
    ),
    Square(33, "Community Chest", SquareType.COMMUNITY_CHEST),
    PropertySquare(
        34,
        "Pennsylvania Avenue",
        SquareType.PROPERTY,
        ColorGroup.GREEN,
        320,
        (28, 150, 450, 1000, 1200, 1400),
        200,
        160,
    ),
    RailroadSquare(35, "Short Line Railroad", SquareType.RAILROAD, 200, 100),
    Square(36, "Chance", SquareType.CHANCE),
    PropertySquare(
        37,
        "Park Place",
        SquareType.PROPERTY,
        ColorGroup.DARK_BLUE,
        350,
        (35, 175, 500, 1100, 1300, 1500),
        200,
        175,
    ),
    TaxSquare(38, "Luxury Tax", SquareType.TAX, 100),
    PropertySquare(
        39,
        "Boardwalk",
        SquareType.PROPERTY,
        ColorGroup.DARK_BLUE,
        400,
        (50, 200, 600, 1400, 1700, 2000),
        200,
        200,
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
