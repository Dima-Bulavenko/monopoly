import z from "zod";
import { useGameStore } from "#/stores/game.store";
import { PlayerSchema } from "../../api/gameStateSchema";

export const GameUserJoined = z.object({
	type: z.literal("game.user.joined"),
	payload: PlayerSchema,
});

export type GameUserJoined = z.infer<typeof GameUserJoined>;

export function handleGameUserJoined(message: z.infer<typeof GameUserJoined>) {
	useGameStore.getState().updateActiveGame((gameState) => {
		gameState.players.push(message.payload);
	});
}
