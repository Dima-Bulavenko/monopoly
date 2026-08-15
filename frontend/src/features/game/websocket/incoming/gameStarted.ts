import z from "zod";
import { useGameStore } from "#/stores/game.store";
import { GameStatusSchema } from "../../api/gameStateSchema";

const GameStartedPayloadSchema = z.object({
	game_id: z.string(),
	status: GameStatusSchema,
});

export const GameStarted = z.object({
	type: z.literal("game_started"),
	payload: GameStartedPayloadSchema,
});

export type GameStarted = z.infer<typeof GameStarted>;

export function handleGameStarted(message: GameStarted) {
	console.log("game was started", message);
	useGameStore.getState().updateActiveGame((gameState) => {
		gameState.status = message.payload.status;
	});
	console.log("game state", useGameStore.getState().gameState);
}
