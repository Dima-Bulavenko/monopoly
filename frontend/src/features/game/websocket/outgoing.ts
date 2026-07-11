import z from "zod";

export const GameUserJoined = z.object({
	type: z.literal("game.user.joined"),
	payload: z.object({
		userId: z.string(),
		username: z.string(),
	}),
});
