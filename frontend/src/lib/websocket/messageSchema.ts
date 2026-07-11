import { z } from "zod";

export const WsMessageSchema = z.object({
	type: z.string(),
	payload: z.unknown(),
});

export type WsMessage = z.infer<typeof WsMessageSchema>;
