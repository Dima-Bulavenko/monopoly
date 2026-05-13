// AUTO-GENERATED — do not edit manually.
// Source of truth: backend/app/application/dto/websocket_dto.py
// Regenerate with: make gen-types

import { z } from "zod";

// ---------------------------------------------------------------------------
// Inbound messages (client → server)
// ---------------------------------------------------------------------------

export const InboundMessageSchema = z.any().superRefine((x, ctx) => {
	const schemas = [
		z.object({ action: z.literal("roll_dice").default("roll_dice") }),
		z.object({ action: z.literal("buy_property").default("buy_property") }),
		z.object({ action: z.literal("pass_property").default("pass_property") }),
		z.object({
			action: z.literal("auction_bid").default("auction_bid"),
			amount: z.number().int(),
		}),
		z.object({ action: z.literal("auction_pass").default("auction_pass") }),
		z.object({ action: z.literal("end_turn").default("end_turn") }),
		z.object({
			action: z.literal("build_house").default("build_house"),
			property_index: z.number().int(),
		}),
		z.object({
			action: z.literal("sell_house").default("sell_house"),
			property_index: z.number().int(),
		}),
		z.object({
			action: z.literal("build_hotel").default("build_hotel"),
			property_index: z.number().int(),
		}),
		z.object({
			action: z.literal("sell_hotel").default("sell_hotel"),
			property_index: z.number().int(),
		}),
		z.object({
			action: z.literal("mortgage_property").default("mortgage_property"),
			property_index: z.number().int(),
		}),
		z.object({
			action: z.literal("unmortgage_property").default("unmortgage_property"),
			property_index: z.number().int(),
		}),
		z.object({ action: z.literal("pay_jail_fine").default("pay_jail_fine") }),
		z.object({ action: z.literal("use_jail_card").default("use_jail_card") }),
		z.object({
			action: z.literal("propose_trade").default("propose_trade"),
			offer_money: z.number().int().default(0),
			offer_property_indices: z.array(z.number().int()).default([]),
			request_money: z.number().int().default(0),
			request_property_indices: z.array(z.number().int()).default([]),
			target_player_id: z.string(),
		}),
		z.object({
			action: z.literal("accept_trade").default("accept_trade"),
			trade_id: z.string(),
		}),
		z.object({
			action: z.literal("reject_trade").default("reject_trade"),
			trade_id: z.string(),
		}),
		z.object({
			action: z.literal("declare_bankruptcy").default("declare_bankruptcy"),
		}),
	];
	const { errors, failed } = schemas.reduce<{
		errors: z.core.$ZodIssue[];
		failed: number;
	}>(
		({ errors, failed }, schema) =>
			((result) =>
				result.error
					? {
							errors: [...errors, ...result.error.issues],
							failed: failed + 1,
						}
					: { errors, failed })(schema.safeParse(x)),
		{ errors: [], failed: 0 },
	);
	const passed = schemas.length - failed;
	if (passed !== 1) {
		ctx.addIssue(
			errors.length
				? {
						path: [],
						code: "invalid_union",
						errors: [errors],
						message:
							"Invalid input: Should pass single schema. Passed " + passed,
					}
				: {
						path: [],
						code: "custom",
						errors: [errors],
						message:
							"Invalid input: Should pass single schema. Passed " + passed,
					},
		);
	}
});

export type InboundMessage = z.infer<typeof InboundMessageSchema>;

// ---------------------------------------------------------------------------
// Outbound messages (server → client)
// ---------------------------------------------------------------------------

export const OutboundMessageSchema = z.any().superRefine((x, ctx) => {
	const schemas = [
		z.object({
			events: z.array(z.record(z.string(), z.any())).default([]),
			state: z.union([z.record(z.string(), z.any()), z.null()]).default(null),
			type: z.literal("game_update").default("game_update"),
		}),
		z.object({
			code: z.string(),
			message: z.string(),
			type: z.literal("error").default("error"),
		}),
	];
	const { errors, failed } = schemas.reduce<{
		errors: z.core.$ZodIssue[];
		failed: number;
	}>(
		({ errors, failed }, schema) =>
			((result) =>
				result.error
					? {
							errors: [...errors, ...result.error.issues],
							failed: failed + 1,
						}
					: { errors, failed })(schema.safeParse(x)),
		{ errors: [], failed: 0 },
	);
	const passed = schemas.length - failed;
	if (passed !== 1) {
		ctx.addIssue(
			errors.length
				? {
						path: [],
						code: "invalid_union",
						errors: [errors],
						message:
							"Invalid input: Should pass single schema. Passed " + passed,
					}
				: {
						path: [],
						code: "custom",
						errors: [errors],
						message:
							"Invalid input: Should pass single schema. Passed " + passed,
					},
		);
	}
});

export type OutboundMessage = z.infer<typeof OutboundMessageSchema>;
