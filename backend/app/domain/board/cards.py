"""Community Chest and Chance card definitions and deck management."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from random import Random


class CardEffect(str, Enum):
    ADVANCE_TO = "advance_to"  # move to specific square index
    ADVANCE_NEAREST_RAILROAD = "advance_nearest_railroad"
    ADVANCE_NEAREST_UTILITY = "advance_nearest_utility"
    GO_BACK = "go_back"  # go back N squares
    COLLECT_FROM_BANK = "collect_from_bank"
    PAY_BANK = "pay_bank"
    COLLECT_FROM_PLAYERS = "collect_from_players"
    PAY_PLAYERS = "pay_players"
    GET_OUT_OF_JAIL_FREE = "get_out_of_jail_free"
    GO_TO_JAIL = "go_to_jail"
    BUILDING_REPAIRS = "building_repairs"  # pay per house/hotel


@dataclass(frozen=True)
class Card:
    id: str
    description: str
    effect: CardEffect
    amount: int = 0  # money involved (+ collect, - pay)
    destination: int | None = None  # for ADVANCE_TO
    squares_back: int = 0  # for GO_BACK
    house_cost: int = 0  # for BUILDING_REPAIRS
    hotel_cost: int = 0  # for BUILDING_REPAIRS


COMMUNITY_CHEST_CARDS: tuple[Card, ...] = (
    Card("cc_01", "Advance to Go (Collect $200)", CardEffect.ADVANCE_TO, destination=0),
    Card(
        "cc_02",
        "Bank error in your favor – Collect $200",
        CardEffect.COLLECT_FROM_BANK,
        200,
    ),
    Card("cc_03", "Doctor's fees – Pay $50", CardEffect.PAY_BANK, 50),
    Card("cc_04", "From sale of stock you get $50", CardEffect.COLLECT_FROM_BANK, 50),
    Card("cc_05", "Get Out of Jail Free", CardEffect.GET_OUT_OF_JAIL_FREE),
    Card("cc_06", "Go to Jail", CardEffect.GO_TO_JAIL),
    Card(
        "cc_07",
        "Grand Opera Night – Collect $50 from every player",
        CardEffect.COLLECT_FROM_PLAYERS,
        50,
    ),
    Card(
        "cc_08",
        "Holiday Fund matures – Receive $100",
        CardEffect.COLLECT_FROM_BANK,
        100,
    ),
    Card("cc_09", "Income tax refund – Collect $20", CardEffect.COLLECT_FROM_BANK, 20),
    Card(
        "cc_10",
        "It is your birthday – Collect $10 from every player",
        CardEffect.COLLECT_FROM_PLAYERS,
        10,
    ),
    Card(
        "cc_11",
        "Life insurance matures – Collect $100",
        CardEffect.COLLECT_FROM_BANK,
        100,
    ),
    Card("cc_12", "Hospital fees – Pay $50", CardEffect.PAY_BANK, 50),
    Card("cc_13", "School fees – Pay $50", CardEffect.PAY_BANK, 50),
    Card("cc_14", "Receive $25 consultancy fee", CardEffect.COLLECT_FROM_BANK, 25),
    Card(
        "cc_15",
        "You are assessed for street repairs: $40/house $115/hotel",
        CardEffect.BUILDING_REPAIRS,
        house_cost=40,
        hotel_cost=115,
    ),
    Card(
        "cc_16",
        "You have won second prize in a beauty contest – Collect $10",
        CardEffect.COLLECT_FROM_BANK,
        10,
    ),
    Card("cc_17", "You inherit $100", CardEffect.COLLECT_FROM_BANK, 100),
)

CHANCE_CARDS: tuple[Card, ...] = (
    Card("ch_01", "Advance to Go (Collect $200)", CardEffect.ADVANCE_TO, destination=0),
    Card("ch_02", "Advance to Illinois Ave.", CardEffect.ADVANCE_TO, destination=24),
    Card(
        "ch_03", "Advance to St. Charles Place", CardEffect.ADVANCE_TO, destination=11
    ),
    Card(
        "ch_04",
        "Advance token to nearest Railroad",
        CardEffect.ADVANCE_NEAREST_RAILROAD,
    ),
    Card(
        "ch_05",
        "Advance token to nearest Railroad (pay double)",
        CardEffect.ADVANCE_NEAREST_RAILROAD,
    ),
    Card(
        "ch_06", "Advance token to nearest Utility", CardEffect.ADVANCE_NEAREST_UTILITY
    ),
    Card("ch_07", "Bank pays you dividend of $50", CardEffect.COLLECT_FROM_BANK, 50),
    Card("ch_08", "Get Out of Jail Free", CardEffect.GET_OUT_OF_JAIL_FREE),
    Card("ch_09", "Go Back 3 Spaces", CardEffect.GO_BACK, squares_back=3),
    Card("ch_10", "Go to Jail", CardEffect.GO_TO_JAIL),
    Card(
        "ch_11",
        "Make general repairs on all your property: $25/house $100/hotel",
        CardEffect.BUILDING_REPAIRS,
        house_cost=25,
        hotel_cost=100,
    ),
    Card("ch_12", "Pay poor tax of $15", CardEffect.PAY_BANK, 15),
    Card(
        "ch_13", "Take a trip to Reading Railroad", CardEffect.ADVANCE_TO, destination=5
    ),
    Card(
        "ch_14", "Take a walk on the Boardwalk", CardEffect.ADVANCE_TO, destination=39
    ),
    Card(
        "ch_15",
        "Elected Chairman of the Board – Pay each player $50",
        CardEffect.PAY_PLAYERS,
        50,
    ),
    Card(
        "ch_16",
        "Your building loan matures – Collect $150",
        CardEffect.COLLECT_FROM_BANK,
        150,
    ),
)


class CardDeck:
    """A shuffled draw pile that auto-reshuffles when empty.

    The Get-Out-of-Jail card is removed from the deck when drawn and returned
    when the player uses it (tracked separately in game state).
    """

    def __init__(self, cards: tuple[Card, ...], rng: Random) -> None:
        self._all_cards = list(cards)
        self._pile: list[Card] = []
        self._reshuffle(rng)

    def _reshuffle(self, rng: Random) -> None:
        self._pile = self._all_cards.copy()
        rng.shuffle(self._pile)

    def draw(self, rng: Random) -> Card:
        if not self._pile:
            self._reshuffle(rng)
        return self._pile.pop()

    def return_card(self, card: Card) -> None:
        """Return a Get-Out-of-Jail card to the bottom of the deck."""
        self._pile.insert(0, card)

    def to_list(self) -> list[str]:
        """Serialise the current pile order as card IDs."""
        return [c.id for c in self._pile]

    @classmethod
    def from_list(cls, card_ids: list[str], all_cards: tuple[Card, ...]) -> "CardDeck":
        """Deserialise from saved card IDs (restores draw order without shuffling)."""
        lookup = {c.id: c for c in all_cards}
        deck = object.__new__(cls)
        deck._all_cards = list(all_cards)
        deck._pile = [lookup[cid] for cid in card_ids]
        return deck
