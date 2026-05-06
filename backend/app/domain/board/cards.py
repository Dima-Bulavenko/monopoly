"""Community Chest and Chance card definitions and deck management."""

from __future__ import annotations

from enum import Enum
from random import Random

from pydantic import BaseModel, ConfigDict


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


class Card(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    description: str
    effect: CardEffect
    amount: int = 0  # money involved (+ collect, - pay)
    destination: int | None = None  # for ADVANCE_TO
    squares_back: int = 0  # for GO_BACK
    house_cost: int = 0  # for BUILDING_REPAIRS
    hotel_cost: int = 0  # for BUILDING_REPAIRS


COMMUNITY_CHEST_CARDS: tuple[Card, ...] = (
    Card(
        id="cc_01",
        description="Advance to Go (Collect $200)",
        effect=CardEffect.ADVANCE_TO,
        destination=0,
    ),
    Card(
        id="cc_02",
        description="Bank error in your favor – Collect $200",
        effect=CardEffect.COLLECT_FROM_BANK,
        amount=200,
    ),
    Card(
        id="cc_03",
        description="Doctor's fees – Pay $50",
        effect=CardEffect.PAY_BANK,
        amount=50,
    ),
    Card(
        id="cc_04",
        description="From sale of stock you get $50",
        effect=CardEffect.COLLECT_FROM_BANK,
        amount=50,
    ),
    Card(
        id="cc_05",
        description="Get Out of Jail Free",
        effect=CardEffect.GET_OUT_OF_JAIL_FREE,
    ),
    Card(id="cc_06", description="Go to Jail", effect=CardEffect.GO_TO_JAIL),
    Card(
        id="cc_07",
        description="Grand Opera Night – Collect $50 from every player",
        effect=CardEffect.COLLECT_FROM_PLAYERS,
        amount=50,
    ),
    Card(
        id="cc_08",
        description="Holiday Fund matures – Receive $100",
        effect=CardEffect.COLLECT_FROM_BANK,
        amount=100,
    ),
    Card(
        id="cc_09",
        description="Income tax refund – Collect $20",
        effect=CardEffect.COLLECT_FROM_BANK,
        amount=20,
    ),
    Card(
        id="cc_10",
        description="It is your birthday – Collect $10 from every player",
        effect=CardEffect.COLLECT_FROM_PLAYERS,
        amount=10,
    ),
    Card(
        id="cc_11",
        description="Life insurance matures – Collect $100",
        effect=CardEffect.COLLECT_FROM_BANK,
        amount=100,
    ),
    Card(
        id="cc_12",
        description="Hospital fees – Pay $50",
        effect=CardEffect.PAY_BANK,
        amount=50,
    ),
    Card(
        id="cc_13",
        description="School fees – Pay $50",
        effect=CardEffect.PAY_BANK,
        amount=50,
    ),
    Card(
        id="cc_14",
        description="Receive $25 consultancy fee",
        effect=CardEffect.COLLECT_FROM_BANK,
        amount=25,
    ),
    Card(
        id="cc_15",
        description="You are assessed for street repairs: $40/house $115/hotel",
        effect=CardEffect.BUILDING_REPAIRS,
        house_cost=40,
        hotel_cost=115,
    ),
    Card(
        id="cc_16",
        description="You have won second prize in a beauty contest – Collect $10",
        effect=CardEffect.COLLECT_FROM_BANK,
        amount=10,
    ),
    Card(
        id="cc_17",
        description="You inherit $100",
        effect=CardEffect.COLLECT_FROM_BANK,
        amount=100,
    ),
)

CHANCE_CARDS: tuple[Card, ...] = (
    Card(
        id="ch_01",
        description="Advance to Go (Collect $200)",
        effect=CardEffect.ADVANCE_TO,
        destination=0,
    ),
    Card(
        id="ch_02",
        description="Advance to Illinois Ave.",
        effect=CardEffect.ADVANCE_TO,
        destination=24,
    ),
    Card(
        id="ch_03",
        description="Advance to St. Charles Place",
        effect=CardEffect.ADVANCE_TO,
        destination=11,
    ),
    Card(
        id="ch_04",
        description="Advance token to nearest Railroad",
        effect=CardEffect.ADVANCE_NEAREST_RAILROAD,
    ),
    Card(
        id="ch_05",
        description="Advance token to nearest Railroad (pay double)",
        effect=CardEffect.ADVANCE_NEAREST_RAILROAD,
    ),
    Card(
        id="ch_06",
        description="Advance token to nearest Utility",
        effect=CardEffect.ADVANCE_NEAREST_UTILITY,
    ),
    Card(
        id="ch_07",
        description="Bank pays you dividend of $50",
        effect=CardEffect.COLLECT_FROM_BANK,
        amount=50,
    ),
    Card(
        id="ch_08",
        description="Get Out of Jail Free",
        effect=CardEffect.GET_OUT_OF_JAIL_FREE,
    ),
    Card(
        id="ch_09",
        description="Go Back 3 Spaces",
        effect=CardEffect.GO_BACK,
        squares_back=3,
    ),
    Card(id="ch_10", description="Go to Jail", effect=CardEffect.GO_TO_JAIL),
    Card(
        id="ch_11",
        description="Make general repairs on all your property: $25/house $100/hotel",
        effect=CardEffect.BUILDING_REPAIRS,
        house_cost=25,
        hotel_cost=100,
    ),
    Card(
        id="ch_12",
        description="Pay poor tax of $15",
        effect=CardEffect.PAY_BANK,
        amount=15,
    ),
    Card(
        id="ch_13",
        description="Take a trip to Reading Railroad",
        effect=CardEffect.ADVANCE_TO,
        destination=5,
    ),
    Card(
        id="ch_14",
        description="Take a walk on the Boardwalk",
        effect=CardEffect.ADVANCE_TO,
        destination=39,
    ),
    Card(
        id="ch_15",
        description="Elected Chairman of the Board – Pay each player $50",
        effect=CardEffect.PAY_PLAYERS,
        amount=50,
    ),
    Card(
        id="ch_16",
        description="Your building loan matures – Collect $150",
        effect=CardEffect.COLLECT_FROM_BANK,
        amount=150,
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
