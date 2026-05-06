// AUTO-GENERATED — do not edit manually.
// Source of truth: backend/app/application/dto/websocket_dto.py
// Regenerate with: make gen-types

import { z } from "zod";

// ---------------------------------------------------------------------------
// Inbound messages (client → server)
// ---------------------------------------------------------------------------

export const InboundMessageSchema = z.discriminatedUnion("action", [
	z.object({ action: z.literal("roll_dice") }),
	z.object({ action: z.literal("end_turn") }),
	z.object({ action: z.literal("buy_property") }),
	z.object({ action: z.literal("pass_property") }),
	z.object({ action: z.literal("auction_bid"), amount: z.number().int() }),
	z.object({ action: z.literal("auction_pass") }),
	z.object({
		action: z.literal("build_house"),
		property_index: z.number().int(),
	}),
	z.object({
		action: z.literal("sell_house"),
		property_index: z.number().int(),
	}),
	z.object({
		action: z.literal("build_hotel"),
		property_index: z.number().int(),
	}),
	z.object({
		action: z.literal("sell_hotel"),
		property_index: z.number().int(),
	}),
	z.object({
		action: z.literal("mortgage_property"),
		property_index: z.number().int(),
	}),
	z.object({
		action: z.literal("unmortgage_property"),
		property_index: z.number().int(),
	}),
	z.object({ action: z.literal("pay_jail_fine") }),
	z.object({ action: z.literal("use_jail_card") }),
	z.object({
		action: z.literal("propose_trade"),
		offer_money: z.number().int().default(0),
		offer_property_indices: z.array(z.number().int()).default([]),
		request_money: z.number().int().default(0),
		request_property_indices: z.array(z.number().int()).default([]),
		target_player_id: z.string(),
	}),
	z.object({ action: z.literal("accept_trade"), trade_id: z.string() }),
	z.object({ action: z.literal("reject_trade"), trade_id: z.string() }),
	z.object({ action: z.literal("declare_bankruptcy") }),
]);

export type InboundMessage = z.infer<typeof InboundMessageSchema>;

// ---------------------------------------------------------------------------
// Outbound messages (server → client)
// ---------------------------------------------------------------------------

export const OutboundMessageSchema = z.discriminatedUnion("type", [
	z.object({
		events: z.array(
			z.discriminatedUnion("type", [
				z.object({
					die1: z.number().int(),
					die2: z.number().int(),
					player_id: z.string(),
					type: z.literal("DiceRolledEvent"),
				}),
				z.object({
					from_position: z.number().int(),
					player_id: z.string(),
					to_position: z.number().int(),
					type: z.literal("PlayerMovedEvent"),
				}),
				z.object({
					amount_collected: z.number().int(),
					player_id: z.string(),
					type: z.literal("PassedGoEvent"),
				}),
				z.object({
					player_id: z.string(),
					square_index: z.number().int(),
					type: z.literal("PropertyLandedEvent"),
				}),
				z.object({
					amount: z.number().int(),
					owner_id: z.string(),
					payer_id: z.string(),
					square_index: z.number().int(),
					type: z.literal("RentPaidEvent"),
				}),
				z.object({
					player_id: z.string(),
					price: z.number().int(),
					square_index: z.number().int(),
					type: z.literal("PropertyBoughtEvent"),
				}),
				z.object({
					mortgage_value: z.number().int(),
					player_id: z.string(),
					square_index: z.number().int(),
					type: z.literal("PropertyMortgagedEvent"),
				}),
				z.object({
					cost: z.number().int(),
					player_id: z.string(),
					square_index: z.number().int(),
					type: z.literal("PropertyUnmortgagedEvent"),
				}),
				z.object({
					square_index: z.number().int(),
					starting_bidder_id: z.string(),
					type: z.literal("AuctionStartedEvent"),
				}),
				z.object({
					amount: z.number().int(),
					player_id: z.string(),
					type: z.literal("AuctionBidPlacedEvent"),
				}),
				z.object({
					player_id: z.string(),
					type: z.literal("AuctionPassedEvent"),
				}),
				z.object({
					amount: z.number().int(),
					player_id: z.string(),
					square_index: z.number().int(),
					type: z.literal("AuctionWonEvent"),
				}),
				z.object({
					square_index: z.number().int(),
					type: z.literal("AuctionEndedWithNoBidderEvent"),
				}),
				z.object({
					cost: z.number().int(),
					player_id: z.string(),
					square_index: z.number().int(),
					type: z.literal("HouseBuiltEvent"),
				}),
				z.object({
					player_id: z.string(),
					refund: z.number().int(),
					square_index: z.number().int(),
					type: z.literal("HouseSoldEvent"),
				}),
				z.object({
					cost: z.number().int(),
					player_id: z.string(),
					square_index: z.number().int(),
					type: z.literal("HotelBuiltEvent"),
				}),
				z.object({
					player_id: z.string(),
					refund: z.number().int(),
					square_index: z.number().int(),
					type: z.literal("HotelSoldEvent"),
				}),
				z.object({
					player_id: z.string(),
					reason: z.enum(["go_to_jail_square", "three_doubles", "card"]),
					type: z.literal("PlayerJailedEvent"),
				}),
				z.object({
					method: z.enum(["paid_fine", "used_card", "rolled_doubles"]),
					player_id: z.string(),
					type: z.literal("PlayerReleasedFromJailEvent"),
				}),
				z.object({
					amount: z.number().int(),
					player_id: z.string(),
					square_index: z.number().int(),
					type: z.literal("TaxPaidEvent"),
				}),
				z.object({
					card_id: z.string(),
					deck: z.enum(["community_chest", "chance"]),
					description: z.string(),
					player_id: z.string(),
					type: z.literal("CardDrawnEvent"),
				}),
				z.object({
					offer_money: z.number().int(),
					offer_property_indices: z.array(z.number().int()),
					proposer_id: z.string(),
					request_money: z.number().int(),
					request_property_indices: z.array(z.number().int()),
					target_id: z.string(),
					trade_id: z.string(),
					type: z.literal("TradeProposedEvent"),
				}),
				z.object({
					proposer_id: z.string(),
					target_id: z.string(),
					trade_id: z.string(),
					type: z.literal("TradeAcceptedEvent"),
				}),
				z.object({
					proposer_id: z.string(),
					target_id: z.string(),
					trade_id: z.string(),
					type: z.literal("TradeRejectedEvent"),
				}),
				z.object({
					player_id: z.string(),
					type: z.literal("BankruptcyDeclaredEvent"),
				}),
				z.object({
					next_player_id: z.string(),
					player_id: z.string(),
					type: z.literal("TurnEndedEvent"),
				}),
				z.object({
					first_player_id: z.string(),
					game_id: z.string(),
					player_ids: z.array(z.string()),
					type: z.literal("GameStartedEvent"),
				}),
				z.object({ type: z.literal("GameOverEvent"), winner_id: z.string() }),
			]),
		),
		state: z.object({
			chance_deck: z.array(z.string()),
			community_chest_deck: z.array(z.string()),
			current_player_index: z.number().int(),
			free_parking_pot: z.number().int(),
			game_id: z.string(),
			last_roll: z.array(z.number().int()),
			pending_auction: z
				.union([
					z.object({
						bids: z.record(z.string(), z.number().int()),
						current_bidder_index: z.number().int(),
						passed_player_ids: z.array(z.string()),
						property_index: z.number().int(),
					}),
					z.null(),
				])
				.default(null),
			pending_trade: z
				.union([
					z.object({
						offer_money: z.number().int(),
						offer_property_indices: z.array(z.number().int()),
						proposer_id: z.string(),
						request_money: z.number().int(),
						request_property_indices: z.array(z.number().int()),
						status: z.string(),
						target_id: z.string(),
						trade_id: z.string(),
					}),
					z.null(),
				])
				.default(null),
			phase: z.string(),
			players: z.array(
				z.object({
					balance: z.number().int(),
					consecutive_doubles: z.number().int(),
					get_out_of_jail_cards: z.number().int(),
					in_jail: z.boolean(),
					is_bankrupt: z.boolean(),
					jail_turns: z.number().int(),
					name: z.string(),
					player_id: z.string(),
					position: z.number().int(),
				}),
			),
			properties: z.record(
				z.string(),
				z.object({
					hotel: z.boolean().default(false),
					houses: z.number().int().default(0),
					mortgaged: z.boolean().default(false),
					owner_id: z.union([z.string(), z.null()]).default(null),
					square_index: z.number().int(),
				}),
			),
			status: z.string(),
			version: z.number().int(),
		}),
		type: z.literal("game_update"),
	}),
	z.object({ code: z.string(), message: z.string(), type: z.literal("error") }),
]);

export type OutboundMessage = z.infer<typeof OutboundMessageSchema>;
