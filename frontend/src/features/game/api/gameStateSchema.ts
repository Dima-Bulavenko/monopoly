import { z } from "zod";

export const GameStatusSchema = z.enum(["lobby", "in_progress", "finished"]);

export const TurnPhaseSchema = z.enum([
	"waiting_for_roll",
	"waiting_for_buy_decision",
	"in_auction",
	"waiting_for_trade_response",
	"in_jail",
	"end_of_turn",
]);

export const TradeStatusSchema = z.enum(["pending", "accepted", "rejected"]);

export const PropertyStateSchema = z.object({
	square_index: z.number().int(),
	owner_id: z.string().nullable(),
	houses: z.number().int(),
	hotel: z.boolean(),
	mortgaged: z.boolean(),
});

export const TradeOfferSchema = z.object({
	trade_id: z.string(),
	proposer_id: z.string(),
	target_id: z.string(),
	offer_property_indices: z.array(z.number().int()),
	offer_money: z.number().int(),
	request_property_indices: z.array(z.number().int()),
	request_money: z.number().int(),
	status: TradeStatusSchema,
});

export const PlayerSchema = z.object({
	player_id: z.string(),
	name: z.string(),
	position: z.number().int(),
	balance: z.number().int(),
	in_jail: z.boolean(),
	jail_turns: z.number().int(),
	consecutive_doubles: z.number().int(),
	get_out_of_jail_cards: z.number().int(),
	is_bankrupt: z.boolean(),
});

export const AuctionStateSchema = z.object({
	property_index: z.number().int(),
	bids: z.record(z.string(), z.number().int()),
	passed_player_ids: z.array(z.string()),
	current_bidder_index: z.number().int(),
});

export const GameSchema = z.object({
	game_id: z.string(),
	status: GameStatusSchema,
	players: z.array(PlayerSchema),
	current_player_index: z.number().int().nullable(),
	phase: TurnPhaseSchema,
	properties: z.record(z.int(), PropertyStateSchema),
	free_parking_pot: z.number().int(),
	max_players: z.number().int().min(2).max(6),
	pending_trade: TradeOfferSchema.nullable(),
	pending_auction: AuctionStateSchema.nullable(),
	last_roll: z.tuple([z.number().int(), z.number().int()]),
	version: z.number().int(),
});

export type GameStateType = z.infer<typeof GameSchema>;
