"""Pure game engine.

GameEngine.process(game, command, rng) → (new_game, list[Event])

All randomness goes through the injected ``rng`` so tests can be deterministic.
The engine never reads from or writes to any external system.
"""

from __future__ import annotations

from random import Random
from typing import Literal

from app.domain.board.cards import (
    CHANCE_CARDS,
    COMMUNITY_CHEST_CARDS,
    Card,
    CardDeck,
    CardEffect,
)
from app.domain.board.squares import (
    BOARD_BY_INDEX,
    BOARD_SIZE,
    COLOR_GROUP_INDICES,
    GO_SALARY,
    JAIL_INDEX,
    MAX_HOTELS,
    MAX_HOUSES,
    RAILROAD_INDICES,
    UTILITY_INDICES,
    PropertySquare,
    RailroadSquare,
    SquareType,
    UtilitySquare,
)
from app.domain.exceptions import (
    BuildingRuleViolationError,
    GameNotInProgressError,
    InsufficientFundsError,
    InvalidActionError,
    NotYourTurnError,
    PropertyNotOwnedError,
)
from app.domain.game.commands import (
    AcceptTradeCommand,
    AuctionBidCommand,
    AuctionPassCommand,
    BuyPropertyCommand,
    BuildHotelCommand,
    BuildHouseCommand,
    Command,
    DeclareBankruptcyCommand,
    EndTurnCommand,
    MortgagePropertyCommand,
    PassPropertyCommand,
    PayJailFineCommand,
    ProposeTradeCommand,
    RejectTradeCommand,
    RollDiceCommand,
    SellHotelCommand,
    SellHouseCommand,
    UnmortgagePropertyCommand,
    UseJailCardCommand,
)
from app.domain.game.events import (
    AuctionBidPlacedEvent,
    AuctionEndedWithNoBidderEvent,
    AuctionPassedEvent,
    AuctionStartedEvent,
    AuctionWonEvent,
    BankruptcyDeclaredEvent,
    CardDrawnEvent,
    DiceRolledEvent,
    Event,
    GameOverEvent,
    GameStartedEvent,
    HotelBuiltEvent,
    HotelSoldEvent,
    HouseBuiltEvent,
    HouseSoldEvent,
    PassedGoEvent,
    PlayerJailedEvent,
    PlayerMovedEvent,
    PlayerReleasedFromJailEvent,
    PropertyBoughtEvent,
    PropertyLandedEvent,
    PropertyMortgagedEvent,
    PropertyUnmortgagedEvent,
    RentPaidEvent,
    TaxPaidEvent,
    TradeAcceptedEvent,
    TradeProposedEvent,
    TradeRejectedEvent,
    TurnEndedEvent,
)
from app.domain.game.models import (
    AuctionState,
    Game,
    GameStatus,
    Player,
    TradeOffer,
    TradeStatus,
    TurnPhase,
)

_DEFAULT_RNG = Random()

JAIL_FINE = 50
UNMORTGAGE_FEE_MULTIPLIER = 1.1  # mortgage value × 110 %
STARTING_BALANCE = 1500


class GameEngine:
    """Pure, stateless game engine.

    Usage::

        engine = GameEngine()
        new_game, events = engine.process(game, RollDiceCommand(player_id="..."))
    """

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def process(
        self,
        game: Game,
        command: Command,
        rng: Random = _DEFAULT_RNG,
    ) -> tuple[Game, list[Event]]:
        """Apply *command* to *game* and return the updated game + emitted events.

        The original game object is never mutated — a deep copy is made first.
        """
        game = game.model_copy(deep=True)
        events: list[Event] = []

        match command:
            case RollDiceCommand():
                self._handle_roll(game, command, rng, events)
            case BuyPropertyCommand():
                self._handle_buy(game, command, events)
            case PassPropertyCommand():
                self._handle_pass_property(game, command, events)
            case AuctionBidCommand():
                self._handle_auction_bid(game, command, events)
            case AuctionPassCommand():
                self._handle_auction_pass(game, command, events)
            case EndTurnCommand():
                self._handle_end_turn(game, command, events)
            case BuildHouseCommand():
                self._handle_build_house(game, command, events)
            case SellHouseCommand():
                self._handle_sell_house(game, command, events)
            case BuildHotelCommand():
                self._handle_build_hotel(game, command, events)
            case SellHotelCommand():
                self._handle_sell_hotel(game, command, events)
            case MortgagePropertyCommand():
                self._handle_mortgage(game, command, events)
            case UnmortgagePropertyCommand():
                self._handle_unmortgage(game, command, events)
            case PayJailFineCommand():
                self._handle_pay_jail_fine(game, command, events)
            case UseJailCardCommand():
                self._handle_use_jail_card(game, command, events)
            case ProposeTradeCommand():
                self._handle_propose_trade(game, command, events)
            case AcceptTradeCommand():
                self._handle_accept_trade(game, command, events)
            case RejectTradeCommand():
                self._handle_reject_trade(game, command, events)
            case DeclareBankruptcyCommand():
                self._handle_bankruptcy(game, command, events)
            case _:
                raise InvalidActionError(f"Unknown command type: {type(command)}")

        return game, events

    # ------------------------------------------------------------------
    # Lobby helpers (called by application layer, not via process())
    # ------------------------------------------------------------------

    def start_game(
        self, game: Game, rng: Random = _DEFAULT_RNG
    ) -> tuple[Game, list[Event]]:
        """Transition a LOBBY game to IN_PROGRESS and deal decks."""
        game = game.model_copy(deep=True)
        if game.status != GameStatus.LOBBY:
            raise InvalidActionError("Game has already started")
        if len(game.players) < 2:
            raise InvalidActionError("Need at least 2 players to start")

        rng.shuffle(game.players)
        game.status = GameStatus.IN_PROGRESS
        game.current_player_index = 0
        game.phase = TurnPhase.WAITING_FOR_ROLL

        cc_deck = CardDeck(COMMUNITY_CHEST_CARDS, rng)
        chance_deck = CardDeck(CHANCE_CARDS, rng)
        game.community_chest_deck = cc_deck.to_list()
        game.chance_deck = chance_deck.to_list()

        events: list[Event] = [
            GameStartedEvent(
                game_id=game.game_id,
                player_ids=tuple(p.player_id for p in game.players),
                first_player_id=game.players[0].player_id,
            )
        ]
        return game, events

    # ------------------------------------------------------------------
    # Roll dice
    # ------------------------------------------------------------------

    def _handle_roll(
        self, game: Game, cmd: RollDiceCommand, rng: Random, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        self._require_current_player(game, cmd.player_id)
        player = game.current_player

        allowed_phases = {TurnPhase.WAITING_FOR_ROLL, TurnPhase.IN_JAIL}
        if game.phase not in allowed_phases:
            raise InvalidActionError(f"Cannot roll in phase {game.phase}")

        die1, die2 = rng.randint(1, 6), rng.randint(1, 6)
        is_doubles = die1 == die2
        game.last_roll = (die1, die2)
        events.append(DiceRolledEvent(player_id=player.player_id, die1=die1, die2=die2))

        # --- Jail handling ---
        if player.in_jail:
            if is_doubles:
                player.in_jail = False
                player.jail_turns = 0
                player.consecutive_doubles = 0
                events.append(
                    PlayerReleasedFromJailEvent(
                        player_id=player.player_id, method="rolled_doubles"
                    )
                )
                self._move_player(game, player, die1 + die2, events)
                game.phase = TurnPhase.END_OF_TURN
            else:
                player.jail_turns += 1
                if player.jail_turns >= 3:
                    # Force pay after 3 failed attempts
                    self._charge(player, JAIL_FINE, events)
                    player.in_jail = False
                    player.jail_turns = 0
                    events.append(
                        PlayerReleasedFromJailEvent(
                            player_id=player.player_id, method="paid_fine"
                        )
                    )
                    self._move_player(game, player, die1 + die2, events)
                game.phase = TurnPhase.END_OF_TURN
            return

        # --- Doubles check (outside jail) ---
        if is_doubles:
            player.consecutive_doubles += 1
            if player.consecutive_doubles >= 3:
                self._send_to_jail(game, player, "three_doubles", events)
                return
        else:
            player.consecutive_doubles = 0

        self._move_player(game, player, die1 + die2, events)

        # If still in END_OF_TURN phase after landing (e.g., tax square, card, etc.)
        # and rolled doubles — go again
        if is_doubles and game.phase == TurnPhase.END_OF_TURN and not player.in_jail:
            game.phase = TurnPhase.WAITING_FOR_ROLL

    # ------------------------------------------------------------------
    # Movement & square effects
    # ------------------------------------------------------------------

    def _move_player(
        self, game: Game, player: Player, steps: int, events: list[Event]
    ) -> None:
        old_pos = player.position
        new_pos = (old_pos + steps) % BOARD_SIZE
        passed_go = new_pos < old_pos or (old_pos == 0 and steps > 0)

        if passed_go:
            player.balance += GO_SALARY
            events.append(
                PassedGoEvent(player_id=player.player_id, amount_collected=GO_SALARY)
            )

        player.position = new_pos
        events.append(
            PlayerMovedEvent(
                player_id=player.player_id, from_position=old_pos, to_position=new_pos
            )
        )
        self._apply_square_effect(game, player, new_pos, events)

    def _apply_square_effect(
        self, game: Game, player: Player, position: int, events: list[Event]
    ) -> None:
        square = BOARD_BY_INDEX[position]

        match square.square_type:
            case SquareType.GO:
                game.phase = TurnPhase.END_OF_TURN

            case SquareType.PROPERTY | SquareType.RAILROAD | SquareType.UTILITY:
                prop = game.properties[position]
                events.append(
                    PropertyLandedEvent(
                        player_id=player.player_id, square_index=position
                    )
                )
                if prop.owner_id is None:
                    game.phase = TurnPhase.WAITING_FOR_BUY_DECISION
                elif prop.owner_id == player.player_id or prop.mortgaged:
                    game.phase = TurnPhase.END_OF_TURN
                else:
                    rent = self._calculate_rent(game, prop, square)
                    self._transfer(
                        player, game.player_by_id(prop.owner_id), rent, events
                    )
                    events.append(
                        RentPaidEvent(
                            payer_id=player.player_id,
                            owner_id=prop.owner_id,
                            square_index=position,
                            amount=rent,
                        )
                    )
                    game.phase = TurnPhase.END_OF_TURN

            case SquareType.TAX:
                from app.domain.board.squares import TaxSquare

                assert isinstance(square, TaxSquare)
                self._charge(player, square.amount, events)
                game.free_parking_pot += square.amount
                events.append(
                    TaxPaidEvent(
                        player_id=player.player_id,
                        square_index=position,
                        amount=square.amount,
                    )
                )
                game.phase = TurnPhase.END_OF_TURN

            case SquareType.COMMUNITY_CHEST:
                self._draw_card(game, player, "community_chest", events)

            case SquareType.CHANCE:
                self._draw_card(game, player, "chance", events)

            case SquareType.GO_TO_JAIL:
                self._send_to_jail(game, player, "go_to_jail_square", events)

            case SquareType.JAIL | SquareType.FREE_PARKING:
                game.phase = TurnPhase.END_OF_TURN

    # ------------------------------------------------------------------
    # Rent calculation
    # ------------------------------------------------------------------

    def _calculate_rent(self, game: Game, prop, square) -> int:
        if isinstance(square, PropertySquare):
            p_state = prop
            if p_state.hotel:
                return square.rent[5]
            if p_state.houses > 0:
                return square.rent[p_state.houses]
            # No buildings — check for monopoly
            group = COLOR_GROUP_INDICES[square.color_group]
            owns_all = all(game.properties[i].owner_id == prop.owner_id for i in group)
            base_rent = square.rent[0]
            return (
                base_rent * square.full_group_rent_multiplier if owns_all else base_rent
            )

        if isinstance(square, RailroadSquare):
            owner_railroad_count = sum(
                1
                for i in RAILROAD_INDICES
                if game.properties[i].owner_id == prop.owner_id
            )
            return RailroadSquare.rent_for_count(owner_railroad_count)

        if isinstance(square, UtilitySquare):
            owner_utility_count = sum(
                1
                for i in UTILITY_INDICES
                if game.properties[i].owner_id == prop.owner_id
            )
            dice_total = sum(game.last_roll)
            return UtilitySquare.rent_multiplier(owner_utility_count) * dice_total

        return 0

    # ------------------------------------------------------------------
    # Card handling
    # ------------------------------------------------------------------

    def _draw_card(
        self,
        game: Game,
        player: Player,
        deck_name: Literal["community_chest", "chance"],
        events: list[Event],
    ) -> None:
        rng = Random()  # stateless draw — order maintained in game.community_chest_deck
        if deck_name == "community_chest":
            deck = CardDeck.from_list(game.community_chest_deck, COMMUNITY_CHEST_CARDS)
            card = deck.draw(rng)
            game.community_chest_deck = deck.to_list()
        else:
            deck = CardDeck.from_list(game.chance_deck, CHANCE_CARDS)
            card = deck.draw(rng)
            game.chance_deck = deck.to_list()

        events.append(
            CardDrawnEvent(
                player_id=player.player_id,
                deck=deck_name,
                card_id=card.id,
                description=card.description,
            )
        )
        self._apply_card_effect(game, player, card, deck_name, events)

    def _apply_card_effect(
        self,
        game: Game,
        player: Player,
        card: Card,
        deck_name: Literal["community_chest", "chance"],
        events: list[Event],
    ) -> None:
        match card.effect:
            case CardEffect.COLLECT_FROM_BANK:
                player.balance += card.amount
                game.phase = TurnPhase.END_OF_TURN

            case CardEffect.PAY_BANK:
                self._charge(player, card.amount, events)
                game.free_parking_pot += card.amount
                game.phase = TurnPhase.END_OF_TURN

            case CardEffect.COLLECT_FROM_PLAYERS:
                for other in game.active_players:
                    if other.player_id != player.player_id:
                        amount = min(card.amount, other.balance)
                        other.balance -= amount
                        player.balance += amount
                game.phase = TurnPhase.END_OF_TURN

            case CardEffect.PAY_PLAYERS:
                for other in game.active_players:
                    if other.player_id != player.player_id:
                        amount = min(card.amount, player.balance)
                        player.balance -= amount
                        other.balance += amount
                game.phase = TurnPhase.END_OF_TURN

            case CardEffect.GET_OUT_OF_JAIL_FREE:
                player.get_out_of_jail_cards += 1
                game.phase = TurnPhase.END_OF_TURN

            case CardEffect.GO_TO_JAIL:
                self._send_to_jail(game, player, "card", events)

            case CardEffect.ADVANCE_TO:
                assert card.destination is not None
                old_pos = player.position
                new_pos = card.destination
                if new_pos < old_pos:
                    player.balance += GO_SALARY
                    events.append(
                        PassedGoEvent(
                            player_id=player.player_id, amount_collected=GO_SALARY
                        )
                    )
                player.position = new_pos
                events.append(
                    PlayerMovedEvent(
                        player_id=player.player_id,
                        from_position=old_pos,
                        to_position=new_pos,
                    )
                )
                self._apply_square_effect(game, player, new_pos, events)

            case CardEffect.GO_BACK:
                old_pos = player.position
                new_pos = (old_pos - card.squares_back) % BOARD_SIZE
                player.position = new_pos
                events.append(
                    PlayerMovedEvent(
                        player_id=player.player_id,
                        from_position=old_pos,
                        to_position=new_pos,
                    )
                )
                self._apply_square_effect(game, player, new_pos, events)

            case CardEffect.ADVANCE_NEAREST_RAILROAD:
                new_pos = self._nearest_of(player.position, RAILROAD_INDICES)
                old_pos = player.position
                if new_pos < old_pos:
                    player.balance += GO_SALARY
                    events.append(
                        PassedGoEvent(
                            player_id=player.player_id, amount_collected=GO_SALARY
                        )
                    )
                player.position = new_pos
                events.append(
                    PlayerMovedEvent(
                        player_id=player.player_id,
                        from_position=old_pos,
                        to_position=new_pos,
                    )
                )
                self._apply_square_effect(game, player, new_pos, events)

            case CardEffect.ADVANCE_NEAREST_UTILITY:
                new_pos = self._nearest_of(player.position, UTILITY_INDICES)
                old_pos = player.position
                if new_pos < old_pos:
                    player.balance += GO_SALARY
                    events.append(
                        PassedGoEvent(
                            player_id=player.player_id, amount_collected=GO_SALARY
                        )
                    )
                player.position = new_pos
                events.append(
                    PlayerMovedEvent(
                        player_id=player.player_id,
                        from_position=old_pos,
                        to_position=new_pos,
                    )
                )
                self._apply_square_effect(game, player, new_pos, events)

            case CardEffect.BUILDING_REPAIRS:
                cost = sum(
                    (p.houses * card.house_cost) + (int(p.hotel) * card.hotel_cost)
                    for p in game.properties.values()
                    if p.owner_id == player.player_id
                )
                if cost > 0:
                    self._charge(player, cost, events)
                    game.free_parking_pot += cost
                game.phase = TurnPhase.END_OF_TURN

    @staticmethod
    def _nearest_of(position: int, indices: tuple[int, ...]) -> int:
        for idx in sorted(indices):
            if idx > position:
                return idx
        return indices[0]  # wrap around

    # ------------------------------------------------------------------
    # Buy / Auction
    # ------------------------------------------------------------------

    def _handle_buy(
        self, game: Game, cmd: BuyPropertyCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        self._require_current_player(game, cmd.player_id)
        if game.phase != TurnPhase.WAITING_FOR_BUY_DECISION:
            raise InvalidActionError("Not waiting for a buy decision")

        player = game.current_player
        prop = game.properties[player.position]
        square = BOARD_BY_INDEX[player.position]

        price: int
        if isinstance(square, (PropertySquare, RailroadSquare, UtilitySquare)):
            price = square.price
        else:
            raise InvalidActionError("Cannot buy this square")

        if player.balance < price:
            raise InsufficientFundsError(f"Need ${price}, have ${player.balance}")

        player.balance -= price
        prop.owner_id = player.player_id
        events.append(
            PropertyBoughtEvent(
                player_id=player.player_id, square_index=player.position, price=price
            )
        )
        game.phase = TurnPhase.END_OF_TURN

    def _handle_pass_property(
        self, game: Game, cmd: PassPropertyCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        self._require_current_player(game, cmd.player_id)
        if game.phase != TurnPhase.WAITING_FOR_BUY_DECISION:
            raise InvalidActionError("Not waiting for a buy decision")

        prop_index = game.current_player.position
        self._start_auction(game, prop_index, events)

    def _start_auction(self, game: Game, prop_index: int, events: list[Event]) -> None:
        active = game.active_players
        # Start bidding from the player *after* the current one (or first in list)
        start_idx = (game.current_player_index + 1) % len(active)
        starting_player = active[start_idx % len(active)]
        game.pending_auction = AuctionState(
            property_index=prop_index,
            current_bidder_index=start_idx % len(active),
        )
        game.phase = TurnPhase.IN_AUCTION
        events.append(
            AuctionStartedEvent(
                square_index=prop_index, starting_bidder_id=starting_player.player_id
            )
        )

    def _handle_auction_bid(
        self, game: Game, cmd: AuctionBidCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        if game.phase != TurnPhase.IN_AUCTION or not game.pending_auction:
            raise InvalidActionError("No auction in progress")

        auction = game.pending_auction
        active = [
            p
            for p in game.active_players
            if p.player_id not in auction.passed_player_ids
        ]
        current_bidder = active[auction.current_bidder_index % len(active)]

        if cmd.player_id != current_bidder.player_id:
            raise NotYourTurnError("Not your turn to bid")

        current_max = max(auction.bids.values(), default=0)
        if cmd.amount <= current_max:
            raise InvalidActionError(
                f"Bid must be higher than current max ${current_max}"
            )

        player = game.player_by_id(cmd.player_id)
        if player.balance < cmd.amount:
            raise InsufficientFundsError(f"Cannot bid ${cmd.amount}")

        auction.bids[cmd.player_id] = cmd.amount
        events.append(AuctionBidPlacedEvent(player_id=cmd.player_id, amount=cmd.amount))
        auction.current_bidder_index = (auction.current_bidder_index + 1) % len(active)

    def _handle_auction_pass(
        self, game: Game, cmd: AuctionPassCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        if game.phase != TurnPhase.IN_AUCTION or not game.pending_auction:
            raise InvalidActionError("No auction in progress")

        auction = game.pending_auction
        active = [
            p
            for p in game.active_players
            if p.player_id not in auction.passed_player_ids
        ]
        current_bidder = active[auction.current_bidder_index % len(active)]

        if cmd.player_id != current_bidder.player_id:
            raise NotYourTurnError("Not your turn")

        auction.passed_player_ids.append(cmd.player_id)
        events.append(AuctionPassedEvent(player_id=cmd.player_id))

        remaining = [
            p
            for p in game.active_players
            if p.player_id not in auction.passed_player_ids
        ]

        if len(remaining) == 0:
            # Everyone passed — no one buys, property stays unowned
            game.pending_auction = None
            game.phase = TurnPhase.END_OF_TURN
            events.append(
                AuctionEndedWithNoBidderEvent(square_index=auction.property_index)
            )
            return

        if len(remaining) == 1 and auction.bids:
            # Last bidder standing wins
            winner_id = max(auction.bids, key=lambda pid: auction.bids[pid])
            winner = game.player_by_id(winner_id)
            winning_bid = auction.bids[winner_id]
            winner.balance -= winning_bid
            game.properties[auction.property_index].owner_id = winner_id
            events.append(
                AuctionWonEvent(
                    player_id=winner_id,
                    square_index=auction.property_index,
                    amount=winning_bid,
                )
            )
            game.pending_auction = None
            game.phase = TurnPhase.END_OF_TURN
            return

        auction.current_bidder_index = (auction.current_bidder_index) % len(remaining)

    # ------------------------------------------------------------------
    # End turn
    # ------------------------------------------------------------------

    def _handle_end_turn(
        self, game: Game, cmd: EndTurnCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        self._require_current_player(game, cmd.player_id)
        if game.phase != TurnPhase.END_OF_TURN:
            raise InvalidActionError(f"Cannot end turn in phase {game.phase}")

        current_player = game.current_player
        current_player.consecutive_doubles = 0

        active = game.active_players
        current_active_idx = next(
            i for i, p in enumerate(active) if p.player_id == current_player.player_id
        )
        next_active = active[(current_active_idx + 1) % len(active)]
        game.current_player_index = next(
            i
            for i, p in enumerate(game.players)
            if p.player_id == next_active.player_id
        )
        next_player = game.current_player

        if next_player.in_jail:
            game.phase = TurnPhase.IN_JAIL
        else:
            game.phase = TurnPhase.WAITING_FOR_ROLL

        events.append(
            TurnEndedEvent(
                player_id=current_player.player_id, next_player_id=next_player.player_id
            )
        )

    # ------------------------------------------------------------------
    # Buildings
    # ------------------------------------------------------------------

    def _handle_build_house(
        self, game: Game, cmd: BuildHouseCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        player = game.player_by_id(cmd.player_id)
        prop = game.properties.get(cmd.property_index)
        if prop is None or prop.owner_id != cmd.player_id:
            raise PropertyNotOwnedError("You don't own this property")

        square = BOARD_BY_INDEX[cmd.property_index]
        if not isinstance(square, PropertySquare):
            raise BuildingRuleViolationError(
                "Can only build on colour-group properties"
            )

        if prop.mortgaged:
            raise BuildingRuleViolationError("Cannot build on a mortgaged property")
        if prop.hotel:
            raise BuildingRuleViolationError("Already has a hotel")
        if prop.houses >= 4:
            raise BuildingRuleViolationError("Build a hotel instead (already 4 houses)")

        # Must own full group
        group = COLOR_GROUP_INDICES[square.color_group]
        if not all(game.properties[i].owner_id == cmd.player_id for i in group):
            raise BuildingRuleViolationError("Must own the full colour group to build")

        # Even build rule — cannot build if another property in group has fewer houses
        min_houses = min(game.properties[i].houses for i in group)
        if prop.houses > min_houses:
            raise BuildingRuleViolationError(
                "Must build evenly across the colour group"
            )

        # House bank limit
        total_houses = sum(p.houses for p in game.properties.values())
        if total_houses >= MAX_HOUSES:
            raise BuildingRuleViolationError("No houses left in the bank")

        if player.balance < square.house_cost:
            raise InsufficientFundsError(f"Need ${square.house_cost}")

        player.balance -= square.house_cost
        prop.houses += 1
        events.append(
            HouseBuiltEvent(
                player_id=cmd.player_id,
                square_index=cmd.property_index,
                cost=square.house_cost,
            )
        )

    def _handle_sell_house(
        self, game: Game, cmd: SellHouseCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        player = game.player_by_id(cmd.player_id)
        prop = game.properties.get(cmd.property_index)
        if prop is None or prop.owner_id != cmd.player_id:
            raise PropertyNotOwnedError("You don't own this property")

        square = BOARD_BY_INDEX[cmd.property_index]
        if not isinstance(square, PropertySquare):
            raise BuildingRuleViolationError("Not a colour property")
        if prop.houses == 0:
            raise BuildingRuleViolationError("No houses to sell")

        # Even sell rule
        group = COLOR_GROUP_INDICES[square.color_group]
        max_houses = max(game.properties[i].houses for i in group)
        if prop.houses < max_houses:
            raise BuildingRuleViolationError("Must sell evenly across the colour group")

        refund = square.house_cost // 2
        prop.houses -= 1
        player.balance += refund
        events.append(
            HouseSoldEvent(
                player_id=cmd.player_id, square_index=cmd.property_index, refund=refund
            )
        )

    def _handle_build_hotel(
        self, game: Game, cmd: BuildHotelCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        player = game.player_by_id(cmd.player_id)
        prop = game.properties.get(cmd.property_index)
        if prop is None or prop.owner_id != cmd.player_id:
            raise PropertyNotOwnedError("You don't own this property")

        square = BOARD_BY_INDEX[cmd.property_index]
        if not isinstance(square, PropertySquare):
            raise BuildingRuleViolationError(
                "Can only build hotels on colour properties"
            )
        if prop.hotel:
            raise BuildingRuleViolationError("Already has a hotel")
        if prop.houses < 4:
            raise BuildingRuleViolationError("Need 4 houses before building a hotel")
        if prop.mortgaged:
            raise BuildingRuleViolationError("Cannot build on a mortgaged property")

        group = COLOR_GROUP_INDICES[square.color_group]
        if not all(game.properties[i].owner_id == cmd.player_id for i in group):
            raise BuildingRuleViolationError("Must own the full colour group")

        # Even build — all must have 4 houses
        if not all(
            game.properties[i].houses == 4 or game.properties[i].hotel for i in group
        ):
            raise BuildingRuleViolationError("Must build hotels evenly")

        total_hotels = sum(1 for p in game.properties.values() if p.hotel)
        if total_hotels >= MAX_HOTELS:
            raise BuildingRuleViolationError("No hotels left in the bank")

        if player.balance < square.house_cost:
            raise InsufficientFundsError(f"Need ${square.house_cost}")

        player.balance -= square.house_cost
        prop.houses = 0
        prop.hotel = True
        events.append(
            HotelBuiltEvent(
                player_id=cmd.player_id,
                square_index=cmd.property_index,
                cost=square.house_cost,
            )
        )

    def _handle_sell_hotel(
        self, game: Game, cmd: SellHotelCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        player = game.player_by_id(cmd.player_id)
        prop = game.properties.get(cmd.property_index)
        if prop is None or prop.owner_id != cmd.player_id:
            raise PropertyNotOwnedError("You don't own this property")

        square = BOARD_BY_INDEX[cmd.property_index]
        if not isinstance(square, PropertySquare):
            raise BuildingRuleViolationError("Not a colour property")
        if not prop.hotel:
            raise BuildingRuleViolationError("No hotel to sell")

        refund = square.house_cost // 2
        prop.hotel = False
        prop.houses = 4
        player.balance += refund
        events.append(
            HotelSoldEvent(
                player_id=cmd.player_id, square_index=cmd.property_index, refund=refund
            )
        )

    # ------------------------------------------------------------------
    # Mortgage
    # ------------------------------------------------------------------

    def _handle_mortgage(
        self, game: Game, cmd: MortgagePropertyCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        player = game.player_by_id(cmd.player_id)
        prop = game.properties.get(cmd.property_index)
        if prop is None or prop.owner_id != cmd.player_id:
            raise PropertyNotOwnedError("You don't own this property")
        if prop.mortgaged:
            raise InvalidActionError("Already mortgaged")
        if prop.houses > 0 or prop.hotel:
            raise BuildingRuleViolationError("Sell all buildings before mortgaging")

        square = BOARD_BY_INDEX[cmd.property_index]
        if isinstance(square, (PropertySquare, RailroadSquare, UtilitySquare)):
            mv = square.mortgage_value
        else:
            raise InvalidActionError("Cannot mortgage this square")

        prop.mortgaged = True
        player.balance += mv
        events.append(
            PropertyMortgagedEvent(
                player_id=cmd.player_id,
                square_index=cmd.property_index,
                mortgage_value=mv,
            )
        )

    def _handle_unmortgage(
        self, game: Game, cmd: UnmortgagePropertyCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        player = game.player_by_id(cmd.player_id)
        prop = game.properties.get(cmd.property_index)
        if prop is None or prop.owner_id != cmd.player_id:
            raise PropertyNotOwnedError("You don't own this property")
        if not prop.mortgaged:
            raise InvalidActionError("Property is not mortgaged")

        square = BOARD_BY_INDEX[cmd.property_index]
        if isinstance(square, (PropertySquare, RailroadSquare, UtilitySquare)):
            mv = square.mortgage_value
        else:
            raise InvalidActionError("Cannot unmortgage this square")

        cost = int(mv * UNMORTGAGE_FEE_MULTIPLIER)
        if player.balance < cost:
            raise InsufficientFundsError(f"Need ${cost} to unmortgage")

        player.balance -= cost
        prop.mortgaged = False
        events.append(
            PropertyUnmortgagedEvent(
                player_id=cmd.player_id, square_index=cmd.property_index, cost=cost
            )
        )

    # ------------------------------------------------------------------
    # Jail
    # ------------------------------------------------------------------

    def _handle_pay_jail_fine(
        self, game: Game, cmd: PayJailFineCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        self._require_current_player(game, cmd.player_id)
        player = game.current_player
        if not player.in_jail:
            raise InvalidActionError("Not in jail")
        if player.balance < JAIL_FINE:
            raise InsufficientFundsError(f"Need ${JAIL_FINE}")

        player.balance -= JAIL_FINE
        player.in_jail = False
        player.jail_turns = 0
        game.free_parking_pot += JAIL_FINE
        events.append(
            PlayerReleasedFromJailEvent(player_id=player.player_id, method="paid_fine")
        )
        game.phase = TurnPhase.WAITING_FOR_ROLL

    def _handle_use_jail_card(
        self, game: Game, cmd: UseJailCardCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        self._require_current_player(game, cmd.player_id)
        player = game.current_player
        if not player.in_jail:
            raise InvalidActionError("Not in jail")
        if player.get_out_of_jail_cards <= 0:
            raise InvalidActionError("No Get Out of Jail Free cards")

        player.get_out_of_jail_cards -= 1
        player.in_jail = False
        player.jail_turns = 0
        events.append(
            PlayerReleasedFromJailEvent(player_id=player.player_id, method="used_card")
        )
        game.phase = TurnPhase.WAITING_FOR_ROLL

    # ------------------------------------------------------------------
    # Trading
    # ------------------------------------------------------------------

    def _handle_propose_trade(
        self, game: Game, cmd: ProposeTradeCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        if game.pending_trade is not None:
            raise InvalidActionError("A trade is already pending")

        proposer = game.player_by_id(cmd.player_id)

        # Validate proposer owns the offered properties
        for idx in cmd.offer_property_indices:
            if game.properties[idx].owner_id != cmd.player_id:
                raise PropertyNotOwnedError(f"You don't own property at index {idx}")
        # Validate target owns the requested properties
        for idx in cmd.request_property_indices:
            if game.properties[idx].owner_id != cmd.target_player_id:
                raise PropertyNotOwnedError(
                    f"Target doesn't own property at index {idx}"
                )

        if proposer.balance < cmd.offer_money:
            raise InsufficientFundsError("Insufficient funds for the trade offer")

        from uuid import uuid4

        trade = TradeOffer(
            trade_id=str(uuid4()),
            proposer_id=cmd.player_id,
            target_id=cmd.target_player_id,
            offer_property_indices=list(cmd.offer_property_indices),
            offer_money=cmd.offer_money,
            request_property_indices=list(cmd.request_property_indices),
            request_money=cmd.request_money,
        )
        game.pending_trade = trade
        game.phase = TurnPhase.WAITING_FOR_TRADE_RESPONSE
        events.append(
            TradeProposedEvent(
                trade_id=trade.trade_id,
                proposer_id=cmd.player_id,
                target_id=cmd.target_player_id,
                offer_property_indices=cmd.offer_property_indices,
                offer_money=cmd.offer_money,
                request_property_indices=cmd.request_property_indices,
                request_money=cmd.request_money,
            )
        )

    def _handle_accept_trade(
        self, game: Game, cmd: AcceptTradeCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        if game.pending_trade is None or game.pending_trade.trade_id != cmd.trade_id:
            raise InvalidActionError("No matching trade pending")
        if cmd.player_id != game.pending_trade.target_id:
            raise InvalidActionError("Only the trade target can accept")

        trade = game.pending_trade
        proposer = game.player_by_id(trade.proposer_id)
        target = game.player_by_id(trade.target_id)

        if target.balance < trade.request_money:
            raise InsufficientFundsError("Target has insufficient funds")

        # Execute the swap
        proposer.balance -= trade.offer_money
        target.balance += trade.offer_money
        target.balance -= trade.request_money
        proposer.balance += trade.request_money

        for idx in trade.offer_property_indices:
            game.properties[idx].owner_id = trade.target_id
        for idx in trade.request_property_indices:
            game.properties[idx].owner_id = trade.proposer_id

        trade.status = TradeStatus.ACCEPTED
        events.append(
            TradeAcceptedEvent(
                trade_id=trade.trade_id,
                proposer_id=trade.proposer_id,
                target_id=trade.target_id,
            )
        )
        game.pending_trade = None
        game.phase = TurnPhase.END_OF_TURN

    def _handle_reject_trade(
        self, game: Game, cmd: RejectTradeCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        if game.pending_trade is None or game.pending_trade.trade_id != cmd.trade_id:
            raise InvalidActionError("No matching trade pending")
        if cmd.player_id not in (
            game.pending_trade.target_id,
            game.pending_trade.proposer_id,
        ):
            raise InvalidActionError("Not a participant in this trade")

        trade = game.pending_trade
        trade.status = TradeStatus.REJECTED
        events.append(
            TradeRejectedEvent(
                trade_id=trade.trade_id,
                proposer_id=trade.proposer_id,
                target_id=trade.target_id,
            )
        )
        game.pending_trade = None
        game.phase = TurnPhase.END_OF_TURN

    # ------------------------------------------------------------------
    # Bankruptcy
    # ------------------------------------------------------------------

    def _handle_bankruptcy(
        self, game: Game, cmd: DeclareBankruptcyCommand, events: list[Event]
    ) -> None:
        self._require_in_progress(game)
        player = game.player_by_id(cmd.player_id)
        player.is_bankrupt = True

        # Return all properties to bank (unowned)
        for prop in game.properties.values():
            if prop.owner_id == cmd.player_id:
                prop.owner_id = None
                prop.houses = 0
                prop.hotel = False
                prop.mortgaged = False

        events.append(BankruptcyDeclaredEvent(player_id=cmd.player_id))

        # Check for game over
        active = game.active_players
        if len(active) == 1:
            game.status = GameStatus.FINISHED
            events.append(GameOverEvent(winner_id=active[0].player_id))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _send_to_jail(
        self,
        game: Game,
        player: Player,
        reason: Literal["go_to_jail_square", "three_doubles", "card"],
        events: list[Event],
    ) -> None:
        old_pos = player.position
        player.position = JAIL_INDEX
        player.in_jail = True
        player.jail_turns = 0
        player.consecutive_doubles = 0
        events.append(
            PlayerMovedEvent(
                player_id=player.player_id,
                from_position=old_pos,
                to_position=JAIL_INDEX,
            )
        )
        events.append(PlayerJailedEvent(player_id=player.player_id, reason=reason))
        game.phase = TurnPhase.END_OF_TURN

    def _charge(self, player: Player, amount: int, events: list[Event]) -> None:
        """Deduct amount from player balance (allows going negative — caller decides bankruptcy)."""
        player.balance -= amount

    def _transfer(
        self, payer: Player, recipient: Player, amount: int, events: list[Event]
    ) -> None:
        actual = min(amount, payer.balance)
        payer.balance -= actual
        recipient.balance += actual

    def _require_in_progress(self, game: Game) -> None:
        if game.status != GameStatus.IN_PROGRESS:
            raise GameNotInProgressError("Game is not in progress")

    def _require_current_player(self, game: Game, player_id: str) -> None:
        if game.current_player.player_id != player_id:
            raise NotYourTurnError("It is not your turn")
